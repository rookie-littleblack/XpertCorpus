"""
This pipeline is used for text cleaning.

@author: rookielittleblack
@date:   2025-08-12
"""
from typing import Optional
from datetime import datetime
from xpertcorpus.utils import xlogger, XpertCorpusStorage
from concurrent.futures import ThreadPoolExecutor
from xpertcorpus.modules.microops import (
    RemoveEmoticonsMicroops, RemoveEmojiMicroops, RemoveExtraSpacesMicroops,
    RemoveHTMLTagsMicroops, RemoveURLsMicroops, RemoveEmailsMicroops,
    RemovePhoneNumbersMicroops, RemoveSpecialCharsMicroops, 
    RemoveNonPrintableMicroops, RemoveFooterHeaderMicroops
)
from xpertcorpus.modules.others.xpipeline import PipelineABC, PipelineState, register_pipeline


@register_pipeline("text_cleaning")
class XCleaningPipe(PipelineABC):
    """
    Enhanced text cleaning pipeline that orchestrates multiple micro-operations.
    
    Features:
    - Comprehensive text cleaning with 10 micro-operations
    - Configurable micro-operation selection
    - Parallel processing support
    - Configurable processing limits
    - Performance monitoring and statistics
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, max_workers: int = 4, limit: int = 0, config: Optional[dict] = None):
        """
        Initialize the XCleaningPipe.
        
        Args:
            max_workers: The number of worker threads for parallel processing.
            limit: The number of limit, 0 means no limit.
            config: Optional configuration dictionary with micro-operation settings:
                - enable_emoticons_removal: Enable emoticons removal (default: True)
                - enable_emoji_removal: Enable emoji removal (default: True)
                - enable_spaces_cleaning: Enable extra spaces cleaning (default: True)
                - enable_html_removal: Enable HTML tags removal (default: True)
                - enable_url_removal: Enable URL removal (default: True)
                - enable_email_removal: Enable email removal (default: False)
                - enable_phone_removal: Enable phone number removal (default: False)
                - enable_special_chars_removal: Enable special chars removal (default: False)
                - enable_non_printable_removal: Enable non-printable chars removal (default: True)
                - enable_footer_header_removal: Enable footer/header removal (default: False)
                
                Plus individual micro-operation configurations:
                - html_config: Configuration for HTML removal
                - url_config: Configuration for URL removal
                - email_config: Configuration for email removal
                - etc.
        """
        # Initialize default micro-operation enablement BEFORE calling super().__init__
        # This is critical because super().__init__() calls _configure_operators()
        self.default_enabled = {
            'enable_emoticons_removal': True,
            'enable_emoji_removal': True,
            'enable_spaces_cleaning': True,
            'enable_html_removal': True,
            'enable_url_removal': True,
            'enable_email_removal': False,  # Privacy-sensitive, disabled by default
            'enable_phone_removal': False,  # Privacy-sensitive, disabled by default
            'enable_special_chars_removal': False,  # May remove important punctuation
            'enable_non_printable_removal': True,
            'enable_footer_header_removal': False  # May remove important content
        }
        
        # Initialize config with defaults if not provided
        if config is None:
            config = {}
        
        # Merge with provided config
        for key, default_value in self.default_enabled.items():
            if key not in config:
                config[key] = default_value
        
        # Now call parent constructor which will invoke _configure_operators()
        super().__init__(max_workers=max_workers, limit=limit, config=config)
        
    def _configure_operators(self) -> None:
        """Configure micro-operations for the cleaning pipeline based on configuration."""
        
        # 1. Remove emoticons (traditional text emoticons)
        if self.config.get('enable_emoticons_removal', True):
            emoticons_config = self.config.get('emoticons_config', {})
            self.add_operator(RemoveEmoticonsMicroops(emoticons_config))
        
        # 2. Remove emoji (Unicode emoji)
        if self.config.get('enable_emoji_removal', True):
            emoji_config = self.config.get('emoji_config', {})
            self.add_operator(RemoveEmojiMicroops(emoji_config))
        
        # 3. Clean extra spaces (should be done after content removal)
        if self.config.get('enable_spaces_cleaning', True):
            spaces_config = self.config.get('spaces_config', {})
            self.add_operator(RemoveExtraSpacesMicroops(spaces_config))
        
        # 4. Remove HTML tags
        if self.config.get('enable_html_removal', True):
            html_config = self.config.get('html_config', {
                'preserve_formatting': False,
                'decode_entities': True,
                'remove_style_script': True
            })
            self.add_operator(RemoveHTMLTagsMicroops(html_config))
        
        # 5. Remove URLs
        if self.config.get('enable_url_removal', True):
            url_config = self.config.get('url_config', {
                'preserve_email_domains': True,
                'remove_partial_urls': True
            })
            self.add_operator(RemoveURLsMicroops(url_config))
        
        # 6. Remove email addresses (optional, privacy-sensitive)
        if self.config.get('enable_email_removal', False):
            email_config = self.config.get('email_config', {
                'mask_instead_remove': True,  # Safer default
                'preserve_domains': False
            })
            self.add_operator(RemoveEmailsMicroops(email_config))
        
        # 7. Remove phone numbers (optional, privacy-sensitive)
        if self.config.get('enable_phone_removal', False):
            phone_config = self.config.get('phone_config', {
                'mask_instead_remove': True  # Safer default
            })
            self.add_operator(RemovePhoneNumbersMicroops(phone_config))
        
        # 8. Remove special characters (optional, may affect meaning)
        if self.config.get('enable_special_chars_removal', False):
            special_config = self.config.get('special_chars_config', {
                'preserve_basic_punctuation': True,
                'preserve_quotes': True,
                'preserve_parentheses': True
            })
            self.add_operator(RemoveSpecialCharsMicroops(special_config))
        
        # 9. Remove non-printable characters
        if self.config.get('enable_non_printable_removal', True):
            non_printable_config = self.config.get('non_printable_config', {
                'preserve_whitespace': True,
                'remove_bom': True
            })
            self.add_operator(RemoveNonPrintableMicroops(non_printable_config))
        
        # 10. Remove footer/header (optional, may remove important content)
        if self.config.get('enable_footer_header_removal', False):
            footer_header_config = self.config.get('footer_header_config', {
                'remove_page_numbers': True,
                'remove_copyright': True,
                'min_line_length': 15
            })
            self.add_operator(RemoveFooterHeaderMicroops(footer_header_config))
        
        xlogger.info(f"Configured {len(self.operators)} micro-operations for enhanced cleaning pipeline")
        
        # Log enabled operations
        enabled_ops = [name for name, enabled in self.default_enabled.items() 
                      if self.config.get(name, enabled)]
        xlogger.debug(f"Enabled cleaning operations: {enabled_ops}")
        
    def get_desc(self, lang: str = "zh") -> str:
        """Get pipeline description."""
        if lang == "zh":
            return "XCleaningPipe 是增强的文本清洗管道，集成了10种微算子，支持全面的文本清理"
        elif lang == "en":
            return "XCleaningPipe is an enhanced text cleaning pipeline with 10 micro-operations for comprehensive text cleaning"
        else:
            return "XCleaningPipe - Enhanced text cleaning pipeline"
        
    def run(self, storage: XpertCorpusStorage, input_key: str = "raw_content", output_key: Optional[str] = None) -> str:
        """
        Execute the enhanced text cleaning pipeline.
        
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
            
            xlogger.info(f"Running Enhanced XCleaningPipe v{self.VERSION}: input_key='{input_key}', output_key='{output_key}'...")
            
            # Generate output key if not provided
            if output_key is None:
                output_key = f"step{storage.operator_step + 1}_content"
            xlogger.info(f"===> Enhanced XCleaningPipe output key: '{output_key}'")
            
            # Load the dataframe from storage
            dataframe = storage.read('dataframe')
            xlogger.info(f"Loading, total number of rows: {len(dataframe)}")
            
            # Apply limit if set
            if self.limit > 0:
                dataframe = dataframe.head(self.limit)
                xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")
            
            # Text cleaning
            xlogger.info(f"Starting enhanced text cleaning process with {len(self.operators)} operations...")
            
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
                    operation_stats = {}
                    
                    for i, operator in enumerate(self.operators):
                        try:
                            before_length = len(cleaned_text)
                            cleaned_text = operator.run(cleaned_text)
                            after_length = len(cleaned_text)
                            
                            # Track reduction per operation
                            reduction = before_length - after_length
                            op_name = operator.__class__.__name__
                            operation_stats[op_name] = reduction
                            
                        except Exception as e:
                            xlogger.warning(f"Error in operation {operator.__class__.__name__} for row {row[0]}: {e}")
                            # Continue with next operation
                    
                    # Log significant reductions periodically
                    total_reduction = len(raw_content) - len(cleaned_text)
                    if total_reduction > len(raw_content) * 0.3:  # More than 30% reduction
                        xlogger.debug(f"Significant text reduction in row {row[0]}: "
                                    f"{len(raw_content)} -> {len(cleaned_text)} "
                                    f"({total_reduction} chars, {total_reduction/len(raw_content)*100:.1f}%)")
                    
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
            xlogger.info("Enhanced text cleaning completed successfully.")
            
            # Calculate and log statistics
            self._log_cleaning_statistics(dataframe, input_key, output_key)
            
            # Save the updated dataframe
            output_file = storage.write(dataframe)
            xlogger.info(f"Successfully cleaned text data with enhanced pipeline. Saved to {output_file}")
            
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
            
            xlogger.error(f"Enhanced XCleaningPipe execution failed: {e}")
            raise
    
    def _log_cleaning_statistics(self, dataframe, input_key: str, output_key: str) -> None:
        """Log cleaning statistics and improvements."""
        try:
            original_lengths = dataframe[input_key].str.len()
            cleaned_lengths = dataframe[output_key].str.len()
            
            total_original = original_lengths.sum()
            total_cleaned = cleaned_lengths.sum()
            total_reduction = total_original - total_cleaned
            
            avg_original = original_lengths.mean()
            avg_cleaned = cleaned_lengths.mean()
            
            reduction_percentage = (total_reduction / total_original * 100) if total_original > 0 else 0
            
            xlogger.info(f"=== Enhanced Cleaning Statistics ===")
            xlogger.info(f"Total characters: {total_original:,} -> {total_cleaned:,}")
            xlogger.info(f"Reduction: {total_reduction:,} characters ({reduction_percentage:.2f}%)")
            xlogger.info(f"Average length: {avg_original:.1f} -> {avg_cleaned:.1f}")
            xlogger.info(f"Active operations: {len(self.operators)}")
            
            # Log individual operator statistics if available
            for operator in self.operators:
                if hasattr(operator, 'get_stats'):
                    stats = operator.get_stats()
                    xlogger.debug(f"Operator {stats.get('microop_name', 'Unknown')}: {stats}")
            
        except Exception as e:
            xlogger.warning(f"Failed to calculate cleaning statistics: {e}")
    
    def get_configuration_info(self) -> dict:
        """Get current configuration information."""
        return {
            'version': self.VERSION,
            'enabled_operations': {name: self.config.get(name, default) 
                                 for name, default in self.default_enabled.items()},
            'total_operators': len(self.operators),
            'operator_names': [op.__class__.__name__ for op in self.operators]
        }
