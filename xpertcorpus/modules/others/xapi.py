"""
XXXXXX

@author: rookielittleblack
@date:   2025-08-11
"""
import re
import os
import json
import requests
import threading

from abc import ABC, abstractmethod
from tqdm import tqdm
from typing import Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xconfig import XConfigLoader


class ApiABC(ABC):
    """
    Abstract base class for data generators. Which may be used to generate data from a model or API. Called by operators
    """    
    @abstractmethod
    def generate_from_input(self, user_inputs: List[str], system_prompt: str) -> List[str]:
        """
        Generate data from input.
        input: List[str], the input of the generator
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Cleanup the generator and garbage collect all GPU/CPU memory.
        """
        pass
    
    def load_model(self, model_name_or_path: str, **kwargs: Any):
        """
        Load the model from the given path.
        This method is optional and can be overridden by subclasses if needed.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

class XApi(ApiABC):
    """
    Use OpenAI API to generate responses based on input messages.
    """

    def __init__(self, max_workers: int = None):
        # Load config
        config_loader = XConfigLoader()
        config = config_loader.load_config()
        llm_model_config = config.get("llm_model")
        self.api_url = llm_model_config.get("base_url")
        self.api_key = llm_model_config.get("api_key")
        self.model_name = llm_model_config.get("model_name")
        self.temperature = llm_model_config.get("temperature")
        self.top_p = llm_model_config.get("top_p")
        self.top_k = llm_model_config.get("top_k")
        self.enable_thinking = llm_model_config.get("enable_thinking", "none").lower()

        # Set max_workers
        self.max_workers = llm_model_config.get("max_workers", 1)
        if max_workers is not None:
            self.max_workers = max_workers
        xlogger.debug(f"XApi using max_workers: `{self.max_workers}`..")

        # Set logger
        self.logger = xlogger

        # Count tokens
        self.token_count_dict = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "total_requests": 0
        }
        
        # Add a lock for thread-safe token counting
        self._token_lock = threading.Lock()

    def update_token_counts(self, response_data):
        """
        Thread-safe update of token usage statistics from API response
        """
        if not response_data or 'usage' not in response_data:
            return
            
        usage = response_data['usage']
        with self._token_lock:
            if 'prompt_tokens' in usage:
                self.token_count_dict["input_tokens"] += usage['prompt_tokens']
            if 'completion_tokens' in usage:
                self.token_count_dict["output_tokens"] += usage['completion_tokens']
            if 'total_tokens' in usage:
                self.token_count_dict["total_tokens"] += usage['total_tokens']
            self.token_count_dict["total_requests"] += 1  # Increment total requests count
    
    def get_token_counts(self):
        """
        Get current token usage statistics
        """
        with self._token_lock:
            raw_dict = self.token_count_dict.copy()
            if raw_dict["total_requests"] == 0:
                # If no requests, return the raw dict
                return raw_dict
            else:
                # Calculate mean tokens
                raw_dict["mean_input_tokens"] = int(raw_dict["input_tokens"] / raw_dict["total_requests"])
                raw_dict["mean_output_tokens"] = int(raw_dict["output_tokens"] / raw_dict["total_requests"])
                raw_dict["mean_total_tokens"] = int(raw_dict["total_tokens"] / raw_dict["total_requests"])

                # Return the dict
                return raw_dict

    def reset_token_counts(self):
        """
        Reset token counters to zero
        """
        with self._token_lock:
            self.token_count_dict = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "total_requests": 0
            }

    def format_response(self, response: dict) -> str:    
        # Safely get content and reasoning_content, defaulting to an empty string if they are None or missing.
        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content')
            if content is None:
                content = ""
        except (KeyError, IndexError):
            content = ""

        try:
            reasoning_content = response.get('choices', [{}])[0].get('message', {}).get('reasoning_content')
            if reasoning_content is None:
                reasoning_content = ""
        except (KeyError, IndexError):
            reasoning_content = ""
        
        # Now that `content` is guaranteed to be a string, we can process it.
        # Added re.DOTALL to handle multiline thinking blocks.
        if re.search(r'<think>.*</think>.*<answer>.*</answer>', content, re.DOTALL):
            return content
        
        if content:
            if reasoning_content:
                return f"<think>{reasoning_content}</think>\n<answer>{content}</answer>"
            else:
                return content
        else:
            # If content is empty (PS: This can be happen when disable thinking for models like Qwen3-32B), just return reasoning_content.
            return reasoning_content

    def generate_from_input(self, user_inputs: list[str], system_prompt: str = "You are a helpful assistant") -> list[str]:
        def api_chat_with_id(system_info: str, messages: str, model: str, id):
            try:
                # Construct payload_dict
                payload_dict = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_info},
                        {"role": "user", "content": messages}
                    ],
                    "temperature": self.temperature
                }

                # Add chat_template_kwargs to the payload_dict if enable_thinking is 'true' or 'false'
                if self.enable_thinking == "true":
                    payload_dict["chat_template_kwargs"] = {"enable_thinking": True}
                    self.logger.info(f"===> enable_thinking is 'true', add chat_template_kwargs to the payload_dict")
                elif self.enable_thinking == "false":
                    payload_dict["chat_template_kwargs"] = {"enable_thinking": False}
                    self.logger.info(f"===> enable_thinking is 'false', add chat_template_kwargs to the payload_dict")
                else:
                    # DONOT add chat_template_kwargs
                    pass

                # Add top_p and top_k to the payload_dict if they are not 999999
                if self.top_p != 999999:
                    payload_dict["top_p"] = self.top_p
                if self.top_k != 999999:
                    payload_dict["top_k"] = self.top_k

                # Serialize the payload_dict to JSON
                payload = json.dumps(payload_dict)
                #self.logger.info(f"===> payload: `{payload}`")

                # Set headers
                headers = {
                    'Authorization': f"Bearer {self.api_key}",
                    'Content-Type': 'application/json',
                    #'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
                }

                # Make a POST request to the API
                response = requests.post(self.api_url, headers=headers, data=payload, timeout=1800)
                # self.logger.debug(f"===> 1 self.api_url: {self.api_url}, self.model_name: {self.model_name}")
                # self.logger.debug(f"===> 1 payload: {payload}")
                # self.logger.debug(f"===> 1 response.status_code: {response.status_code}")
                # self.logger.debug(f"===> 1 response.content: {response.content}")
                
                # Check if the response is successful
                if response.status_code == 200:
                    # self.logger.info(f"API request successful")
                    response_data = response.json()
                    # Track token usage for this request
                    self.update_token_counts(response_data)
                    # self.logger.info(f"API response: {response_data['choices'][0]['message']['content']}")
                    return id, self.format_response(response_data)
                else:
                    self.logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    return id, None
            except Exception as e:
                self.logger.error(f"API request error: {e}")
                return id, None
                
        responses = [None] * len(user_inputs)
        # -- end of subfunction api_chat_with_id --

        # Use ThreadPoolExecutor to parallelize the API calls.
        # self.logger.info(f"Generating {len(questions)} responses")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(
                    api_chat_with_id,
                    system_info = system_prompt,
                    messages = question,
                    model = self.model_name,
                    id = idx
                ) for idx, question in enumerate(user_inputs)
            ]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Generating......"):
                    response = future.result() # (id, response)
                    responses[response[0]] = response[1]
                    
        #self.logger.info(f"Token usage summary: {self.get_token_counts()}")
        return responses
    
    def cleanup(self):
        # Cleanup resources if needed
        self.logger.info("Cleaning up resources in XApi")
        # No specific cleanup actions needed for this implementation
        pass