"""
This script is the pipeline of generating pretraining data.

@author: rookielittleblack
@date:   2025-08-11
"""
from xpertcorpus.utils import xlogger, count_tokens, XpertCorpusStorage
from concurrent.futures import ThreadPoolExecutor
from xpertcorpus.modules.others.xapi import XApi
from xpertcorpus.modules.others.xprompts import XPrompt4CleanText
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


@OPERATOR_REGISTRY.register()
class XLlmCleaner(OperatorABC):
    '''
    XLlmCleaner is a class that use LLM for text cleaning.
    '''
    def __init__(self, max_workers: int = 1, limit: int = 0):
        """
        Initialize the XLlmCleaner.

        Args:
            max_workers: The number of workers.
            limit: The number of limit, 0 means no limit.
        """
        self.max_workers = max_workers
        self.limit = limit
        self.prompts = XPrompt4CleanText()
        self.xapi = XApi(max_workers=self.max_workers)
    
    @staticmethod
    def get_desc(lang: str = "zh"):
        return "基于大模型对文本进行清洗。" if lang == "zh" else "Using LLM for text cleaning."

    def run(self, storage: XpertCorpusStorage, input_key: str = "raw_content", output_key: str = None):
        self.input_key, self.output_key = input_key, output_key
        xlogger.info(f"Running XLlmCleaner: self.input_key: `{self.input_key}`, self.output_key: `{self.output_key}`...")

        # If the output key is not set, use the default output key
        if self.output_key is None:
            self.output_key = f"step{storage.operator_step + 1}_content"
        xlogger.info(f"===> XLlmCleaner output key: `{self.output_key}`")

        # Load the raw dataframe from the input file
        dataframe = storage.read('dataframe')
        xlogger.info(f"Loading, total number of rows: {len(dataframe)}")

        # Check if limit is set
        if self.limit > 0:
            dataframe = dataframe.head(self.limit)
            xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")

        # Create a list to hold all generated questions and answers
        llm_inputs = []

        # Prepare LLM inputs by formatting the prompt with raw content from the dataframe
        items = list(dataframe.iterrows())

        def build_prompt(row):
            """
            Build the LLM input prompt for a single row.
            This function extracts the raw content, formats it using the prompt template,
            counts the tokens, and returns the prompt string.
            If the raw content is empty, returns None.
            """
            raw_content = row[1].get(self.input_key, '')
            if raw_content:
                llm_input = self.prompts.get_prompt(raw_content)
                llm_input_tokens = count_tokens(llm_input)
                xlogger.debug(f"Calculated LLM input token count: {llm_input_tokens}")
                return llm_input
            return None

        # Use ThreadPoolExecutor to parallelize prompt construction.
        # Note: For CPU-bound tasks, consider using ProcessPoolExecutor for better performance.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            llm_inputs = list(executor.map(build_prompt, items))
        # Filter out None results (rows with empty raw_content)
        llm_inputs = [x for x in llm_inputs if x]

        # Generate the text using the model
        try:
            xlogger.info("Generating text using the model...")
            generated_outputs = self.xapi.generate_from_input(llm_inputs)
            xlogger.info("Text generation completed.")
        except Exception as e:
            xlogger.error(f"Error during text generation: {e}")
            return

        # Add the generated content back to the dataframe
        dataframe[self.output_key] = generated_outputs

        # Add the token count to the dataframe
        output_tokens = [count_tokens(x) for x in generated_outputs]
        dataframe[self.output_key + '_tokens'] = output_tokens

        # Calculate tokens change
        input_tokens_key = input_key + '_tokens'
        if input_tokens_key in dataframe.columns:
            input_tokens = dataframe[input_tokens_key]
            output_tokens = dataframe[self.output_key + '_tokens']
            dataframe[self.output_key + '_tokens_changed'] = output_tokens - input_tokens
        else:
            dataframe[self.output_key + '_tokens_changed'] = 0
            xlogger.warning(f"Input tokens key {input_tokens_key} not found in dataframe, set tokens change to 0.")

        # Save the updated dataframe to the output file
        output_file = storage.write(dataframe)
        xlogger.info(f"Successfully generated text. Saved to {output_file}")

        # Return the output key
        return self.output_key