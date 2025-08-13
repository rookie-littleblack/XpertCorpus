"""
Pretraining data generation framework for XpertCorpus.

This framework provides end-to-end processing for generating high-quality
pretraining data from raw text/markdown corpus.

Usage:
    python -m xpertcorpus.main --input ./data/raw_content_test_1.jsonl --output ./output --max_workers 1

@author: rookielittleblack
@date:   2025-08-13
"""
import os
import json

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from xpertcorpus.utils import xlogger, error_handler, safe_execute, count_tokens
from xpertcorpus.modules.operators import XTextSplitter, XLlmCleaner
from xpertcorpus.modules.others.xlimitor import XLimitor
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType, FrameworkState, register_framework
from xpertcorpus.modules.pipelines.xcleaning_pipe import XCleaningPipe


@register_framework("pretraining")
class XFramework_PT(FrameworkABC):
    """
    XFramework_PT is a framework for generating pretrain data.
    
    Features:
    - Raw corpus processing (txt/md → jsonl)
    - LLM-based content cleaning
    - Multi-stage cleaning pipeline
    - Intelligent text splitting
    - Token usage tracking
    - Error handling and recovery
    - Automatic state management (auto-prepare when needed)
    
    Usage:
        # Simple usage (recommended)
        framework = XFramework_PT(
            input_file="./data/corpus.jsonl", 
            output_dir="./output",
            max_workers=4
        )
        results = framework.run()  # Automatically prepares and executes
        
        # With custom configuration
        config = {
            "text_splitter": {"chunk_size": 1024, "chunk_overlap": 100},
            "llm_cleaner": {"enable_token_tracking": True}
        }
        framework = XFramework_PT(..., config=config)
        results = framework.run()
        
        # Manual lifecycle management
        framework = XFramework_PT(...)
        framework.prepare()  # Manually prepare components
        results = framework.run()  # Execute pipeline
        
    Processing Pipeline:
        1. Input validation and raw corpus detection
        2. Optional: Raw corpus preprocessing (txt/md → jsonl)
        3. Data limiting (if configured)
        4. LLM-based content cleaning
        5. Multi-stage cleaning pipeline
        6. Intelligent text splitting
        7. Result aggregation and storage
    """
    
    # Framework metadata
    FRAMEWORK_TYPE = FrameworkType.PRETRAINING
    VERSION = "1.0.0"
    REQUIRED_OPERATORS = ["llm_cleaner", "text_splitter"]  # limitor is optional
    REQUIRED_PIPELINES = ["cleaning_pipe"]
    
    def __init__(self, 
                 input_file: str, 
                 output_dir: str = "./output", 
                 max_workers: int = 1, 
                 limit: int = 0,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the XFramework_PT.

        Args:
            input_file: The input file or directory path. Can be:
                       - JSONL file with 'raw_content' field (processed corpus)
                       - Directory with .txt/.md files (raw corpus)
            output_dir: The output directory path. If default "./output",
                       will create timestamped subdirectory
            max_workers: The number of worker threads for parallel processing
            limit: The number of records to process, 0 means no limit
            config: Optional configuration dictionary to override defaults.
                   See class docstring for configuration examples.
                   
        Note:
            Framework starts in INITIALIZED state. Call run() to automatically
            prepare and execute, or call prepare() manually for explicit control.
        """
        # Set default configuration
        default_config = {
            # Text splitter configuration
            "text_splitter": {
                "chunk_size": 512,
                "chunk_overlap": 200,
                "split_method": "markdown",  # or "semantic"
                "min_tokens_per_chunk": 20
            },
            # LLM cleaner configuration
            "llm_cleaner": {
                "enable_token_tracking": True,
                "reset_tokens_on_start": True
            },
            # Storage configuration
            "storage": {
                "enable_compression": False,
                "validate_on_write": True,
                "cache_type": "jsonl"
            },
            # Processing configuration
            "processing": {
                "auto_detect_raw_corpus": True,
                "supported_extensions": [".txt", ".md"],
                "exclude_patterns": [".bak"]
            }
        }
        
        # Merge with provided config
        if config:
            self._deep_merge_config(default_config, config)
        
        # Initialize parent class
        super().__init__(
            input_file=input_file,
            output_dir=output_dir,
            max_workers=max_workers,
            limit=limit,
            config=default_config
        )
        
        # Framework-specific attributes
        self.is_raw_corpus = False
        self.preprocessed_file: Optional[str] = None
        
        # Component references (will be initialized in _prepare_components)
        self.limitor: Optional[XLimitor] = None
        self.xllmcleaner: Optional[XLlmCleaner] = None
        self.xcleaningpipe: Optional[XCleaningPipe] = None
        self.corpus_text_splitter: Optional[XTextSplitter] = None
    
    def _deep_merge_config(self, target: Dict, source: Dict) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge_config(target[key], value)
            else:
                target[key] = value
    
    def _on_init(self) -> None:
        """Framework-specific initialization."""
        xlogger.info(
            f"XFramework_PT initializing: input_file='{self.input_file}', "
            f"output_dir='{self.output_dir}', max_workers={self.max_workers}, limit={self.limit}"
        )
        
        # Detect if input is raw corpus
        self._detect_raw_corpus()
        
        # Process raw corpus if needed
        if self.is_raw_corpus:
            self.preprocessed_file = self._process_raw_corpus()
            if self.preprocessed_file:
                self.input_file = self.preprocessed_file
                # Update storage with new input file
                self._initialize_storage()
    
    def _detect_raw_corpus(self) -> None:
        """Detect if input is a raw corpus directory."""
        if os.path.isdir(self.input_file):
            xlogger.info(
                f"Input path is a directory: '{self.input_file}', "
                "will be processed as raw text/markdown corpus."
            )
            self.is_raw_corpus = True
        else:
            xlogger.info(
                f"Input path is a file: '{self.input_file}', "
                "will be processed as potential cleaned corpus."
            )
            self.is_raw_corpus = False
    
    @safe_execute(fallback_value=None, retry_enabled=False)
    def _process_raw_corpus(self) -> Optional[str]:
        """
        Process raw corpus: from raw text/markdown corpus to cleaned JSONL corpus.
        
        Returns:
            Path to processed JSONL file or None if processing failed
        """
        xlogger.info("Processing raw corpus...")
        
        try:
            # Get supported file extensions and exclude patterns
            extensions = self.config["processing"]["supported_extensions"]
            exclude_patterns = self.config["processing"]["exclude_patterns"]
            
            # Find all supported files
            files_list = []
            for root, _, filenames in os.walk(self.input_file):
                for file in filenames:
                    abs_file_path = os.path.join(root, file)
                    
                    # Check exclude patterns
                    if any(pattern in abs_file_path for pattern in exclude_patterns):
                        continue
                    
                    # Check supported extensions
                    if any(file.endswith(ext) for ext in extensions):
                        files_list.append(abs_file_path)
            
            if not files_list:
                xlogger.warning(f"No supported files found in '{self.input_file}'")
                return None
            
            xlogger.info(f"Found {len(files_list)} files to process")
            
            # Prepare output files
            file_list_path = os.path.join(self.output_dir, "preprocess_raw_corpus_files_list.tsv")
            jsonl_output_path = os.path.join(self.output_dir, "preprocess_raw_corpus.jsonl")
            
            # Process files
            total_files = 0
            total_tokens = 0
            
            with open(file_list_path, "w", encoding="utf-8") as list_file:
                with open(jsonl_output_path, "w", encoding="utf-8") as jsonl_file:
                    for file_path in files_list:
                        total_files += 1
                        xlogger.info(f"Processing file {total_files}: '{file_path}'")
                        
                        try:
                            # Read file content
                            with open(file_path, "r", encoding="utf-8") as infile:
                                content = infile.read()
                            
                            # Count tokens
                            tokens = count_tokens(content)
                            total_tokens += tokens
                            
                            # Prepare record
                            record = {
                                "file_path": file_path,
                                "raw_content": content,
                                "raw_content_tokens": tokens,
                                "processed_at": datetime.now().isoformat()
                            }
                            
                            # Write to JSONL
                            jsonl_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                            
                            # Write to TSV
                            list_file.write(f"{file_path}\t{tokens}\n")
                            
                        except Exception as e:
                            xlogger.error(f"Failed to process file '{file_path}': {e}")
                            self.metrics["errors_count"] += 1
                            continue
            
            # Update metrics
            self.metrics["files_processed"] = total_files
            self.metrics["tokens_processed"] = total_tokens
            
            xlogger.success(
                f"Raw corpus processing completed: {total_files} files, "
                f"{total_tokens} tokens processed"
            )
            
            return jsonl_output_path
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "stage": "raw_corpus_processing",
                    "input_path": self.input_file,
                    "output_dir": self.output_dir
                },
                should_raise=False
            )
            return None
    
    def _prepare_components(self) -> None:
        """Prepare framework components (operators, pipelines)."""
        try:
            xlogger.info("Preparing PT framework components...")
            
            # Initialize limitor
            if self.limit > 0:
                self.limitor = XLimitor(limit=self.limit)
                self.add_operator("limitor", self.limitor)
                xlogger.debug(f"Limitor initialized with limit: {self.limit}")
            
            # Initialize LLM cleaner
            self.xllmcleaner = XLlmCleaner(max_workers=self.max_workers)
            self.add_operator("llm_cleaner", self.xllmcleaner)
            
            # Initialize cleaning pipeline
            self.xcleaningpipe = XCleaningPipe(max_workers=self.max_workers)
            self.add_pipeline("cleaning_pipe", self.xcleaningpipe)
            
            # Initialize text splitter
            splitter_config = self.config["text_splitter"]
            self.corpus_text_splitter = XTextSplitter(
                chunk_size=splitter_config["chunk_size"],
                chunk_overlap=splitter_config["chunk_overlap"],
                split_method=splitter_config["split_method"],
                min_tokens_per_chunk=splitter_config["min_tokens_per_chunk"]
            )
            self.add_operator("text_splitter", self.corpus_text_splitter)
            
            xlogger.success("All PT framework components prepared")
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"stage": "component_preparation"},
                should_raise=True
            )
    
    def _execute_pipeline(self) -> Dict[str, Any]:
        """Execute the main processing pipeline."""
        try:
            # Validate input file
            if not self.input_file or not os.path.exists(self.input_file):
                raise FileNotFoundError(f"Input file not found: {self.input_file}")
            
            if not self.input_file.endswith(".jsonl"):
                raise ValueError("Input file must be a JSONL file for processing")
            
            # Reset token usage if configured
            if self.config["llm_cleaner"]["reset_tokens_on_start"]:
                self.xllmcleaner.xapi.reset_token_counts()
                xlogger.info("Token usage has been reset")
            
            xlogger.info("Starting XFramework_PT pipeline execution...")
            xlogger.info("=" * 60)
            
            results = {"pipeline_outputs": {}}
            
            # Step 1: Run limitor (if configured)
            if self.limitor:
                xlogger.info(self.limitor.get_desc(lang="en"))
                self.limitor.run(self.storage.step())
                self.metrics["pipeline_steps_completed"] += 1
                results["pipeline_outputs"]["limitor"] = "Applied data limiting"
            
            # Step 2: Run LLM Cleaner
            xlogger.info(self.xllmcleaner.get_desc(lang="en"))
            xllmcleaner_output_key = self.xllmcleaner.run(
                self.storage.step(),
                input_key="raw_content"
            )
            self.metrics["pipeline_steps_completed"] += 1
            results["pipeline_outputs"]["llm_cleaner"] = xllmcleaner_output_key
            xlogger.info(f"XLlmCleaner output key: '{xllmcleaner_output_key}'")
            
            # Step 3: Run Cleaning Pipeline
            xlogger.info(self.xcleaningpipe.get_desc(lang="en"))
            xcleaningpipe_output_key = self.xcleaningpipe.run(
                self.storage.step(),
                input_key=xllmcleaner_output_key
            )
            self.metrics["pipeline_steps_completed"] += 1
            results["pipeline_outputs"]["cleaning_pipe"] = xcleaningpipe_output_key
            xlogger.info(f"XCleaningPipe output key: '{xcleaningpipe_output_key}'")
            
            # Step 4: Run Text Splitter
            xlogger.info(self.corpus_text_splitter.get_desc(lang="en"))
            corpus_text_splitter_output_key = self.corpus_text_splitter.run(
                self.storage.step(),
                input_key=xcleaningpipe_output_key
            )
            self.metrics["pipeline_steps_completed"] += 1
            results["pipeline_outputs"]["text_splitter"] = corpus_text_splitter_output_key
            xlogger.info(f"Corpus text splitter output key: '{corpus_text_splitter_output_key}'")
            
            # Collect final results
            results.update({
                "output_path": self.storage.cache_path,
                "final_output_key": corpus_text_splitter_output_key,
                "token_usage": self.xllmcleaner.xapi.get_token_counts() if self.config["llm_cleaner"]["enable_token_tracking"] else None,
                "storage_stats": self.storage.get_storage_stats()
            })
            
            # Update metrics
            storage_stats = self.storage.get_storage_stats()
            self.metrics["records_processed"] = storage_stats.get("total_records", 0)
            
            xlogger.success(f"Pipeline execution completed. Output path: '{self.storage.cache_path}'")
            
            # Log token usage
            if self.config["llm_cleaner"]["enable_token_tracking"]:
                token_usage = self.xllmcleaner.xapi.get_token_counts()
                xlogger.info(f"Token usage: {token_usage}")
            
            return results
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "stage": "pipeline_execution",
                    "input_file": self.input_file,
                    "current_step": self.metrics["pipeline_steps_completed"]
                },
                should_raise=True
            )
    
    def get_desc(self, lang: str = "zh") -> str:
        """Get framework description."""
        if lang == "zh":
            return (
                "XFramework_PT - 预训练数据生成框架\n"
                "功能：原始语料处理、LLM清洗、多阶段清理管道、智能文本分割\n"
                f"版本：{self.VERSION}"
            )
        else:
            return (
                "XFramework_PT - Pretraining Data Generation Framework\n"
                "Features: Raw corpus processing, LLM cleaning, multi-stage cleaning pipeline, intelligent text splitting\n"
                f"Version: {self.VERSION}"
            )
    
    # Legacy method for backward compatibility
    def forward(self) -> Dict[str, Any]:
        """
        Legacy forward method for backward compatibility.
        
        Automatically handles framework preparation based on current state:
        - INITIALIZED: Calls prepare() then run()
        - CONFIGURED: Calls run() directly
        - Other states: Raises ValueError
        
        Returns:
            Pipeline execution results
            
        Note:
            This method is deprecated. Use run() method instead for better
            state management and clearer semantics.
        """
        xlogger.warning("Using legacy forward() method. Consider using run() instead.")
        
        try:
            # Prepare if not already prepared
            if self.state == FrameworkState.INITIALIZED:
                self.prepare()
            elif self.state == FrameworkState.CONFIGURED:
                # Already configured, can proceed directly
                pass
            else:
                raise ValueError(f"Framework cannot run in current state: {self.state}")
            
            # Execute pipeline
            return self.run()
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"method": "forward", "legacy_mode": True},
                should_raise=True
            )
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get detailed information about the processing pipeline."""
        return {
            "framework_type": self.FRAMEWORK_TYPE.value,
            "version": self.VERSION,
            "is_raw_corpus": self.is_raw_corpus,
            "preprocessed_file": self.preprocessed_file,
            "components": {
                "limitor": self.limitor is not None,
                "llm_cleaner": self.xllmcleaner is not None,
                "cleaning_pipe": self.xcleaningpipe is not None,
                "text_splitter": self.corpus_text_splitter is not None
            },
            "configuration": self.config,
            "metrics": self.get_metrics(),
            "state": self.state.value
        }


# For backward compatibility
XFrameworkPT = XFramework_PT