"""
This pipeline is used for text cleaning.

@author: rookielittleblack
@date:   2025-08-12
"""
from typing import Optional
from datetime import datetime
from xpertcorpus.utils import xlogger, XpertCorpusStorage
from concurrent.futures import ThreadPoolExecutor
from xpertcorpus.modules.microops import RemoveEmoticonsMicroops, RemoveEmojiMicroops
from xpertcorpus.modules.others.xpipeline import PipelineABC, PipelineState, register_pipeline


@register_pipeline("text_cleaning")
class XCleaningPipe(PipelineABC):
    """
    Text cleaning pipeline that orchestrates multiple micro-operations.
    
    Features:
    - Emoticon removal
    - Emoji removal
    - Parallel processing support
    - Configurable processing limits
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, max_workers: int = 4, limit: int = 0, config: Optional[dict] = None):
        """
        Initialize the XCleaningPipe.
        
        Args:
            max_workers: The number of worker threads for parallel processing.
            limit: The number of limit, 0 means no limit.
            config: Optional configuration dictionary.
        """
        super().__init__(max_workers=max_workers, limit=limit, config=config)
        
    def _configure_operators(self) -> None:
        """Configure micro-operations for the cleaning pipeline."""
        # Add micro-operations to the pipeline
        self.add_operator(RemoveEmoticonsMicroops())
        self.add_operator(RemoveEmojiMicroops())
        
        xlogger.debug(f"Configured {len(self.operators)} micro-operations for cleaning pipeline")
        
    def get_desc(self, lang: str = "zh") -> str:
        """Get pipeline description."""
        if lang == "zh":
            return "XCleaningPipe 是文本清洗管道，集成了多种微操作"
        elif lang == "en":
            return "XCleaningPipe is a text cleaning pipeline that integrates multiple micro-operations"
        else:
            return "XCleaningPipe - Text cleaning pipeline"
        
    def run(self, storage: XpertCorpusStorage, input_key: str = "raw_content", output_key: Optional[str] = None) -> str:
        """
        Execute the text cleaning pipeline.
        
        Args:
            storage: Storage instance for data management
            input_key: Input data key
            output_key: Output data key (auto-generated if None)
            
        Returns:
            Output key for the cleaned data
        """
        start_time = datetime.now()
        
        try:
            # Update state
            self.state = PipelineState.RUNNING
            self.metrics["execution_count"] += 1
            
            xlogger.info(f"Running XCleaningPipe: input_key='{input_key}', output_key='{output_key}'...")
            
            # Generate output key if not provided
            if output_key is None:
                output_key = f"step{storage.operator_step + 1}_content"
            xlogger.info(f"===> XCleaningPipe output key: '{output_key}'")
            
            # Load the dataframe from storage
            dataframe = storage.read('dataframe')
            xlogger.info(f"Loading, total number of rows: {len(dataframe)}")
            
            # Apply limit if set
            if self.limit > 0:
                dataframe = dataframe.head(self.limit)
                xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")
            
            # Text cleaning
            xlogger.info("Starting text cleaning process...")
            
            # Prepare data for parallel processing
            items = list(dataframe.iterrows())
            
            def clean_text(row):
                """
                Clean text for a single row using the configured micro-operations.
                """
                try:
                    raw_content = row[1].get(input_key, '')
                    if not raw_content:
                        return raw_content
                    
                    # Apply all micro-operations sequentially
                    cleaned_text = raw_content
                    for operator in self.operators:
                        cleaned_text = operator.run(cleaned_text)
                    
                    return cleaned_text
                    
                except Exception as e:
                    xlogger.error(f"Error cleaning text for row {row[0]}: {e}")
                    return raw_content  # Return original content if cleaning fails
            
            # Use ThreadPoolExecutor for parallel processing
            xlogger.info(f"Using {self.max_workers} worker threads for parallel text cleaning...")
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                cleaned_texts = list(executor.map(clean_text, items))
            
            # Add the cleaned content back to the dataframe
            dataframe[output_key] = cleaned_texts
            xlogger.info("Text cleaning completed successfully.")
            
            # Save the updated dataframe
            output_file = storage.write(dataframe)
            xlogger.info(f"Successfully cleaned text data. Saved to {output_file}")
            
            # Update metrics and state
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics["total_processing_time"] += execution_time
            self.metrics["last_execution_time"] = execution_time
            self.state = PipelineState.COMPLETED
            
            return output_key
            
        except Exception as e:
            # Handle errors
            self.state = PipelineState.FAILED
            self.metrics["error_count"] += 1
            
            xlogger.error(f"XCleaningPipe execution failed: {e}")
            raise
