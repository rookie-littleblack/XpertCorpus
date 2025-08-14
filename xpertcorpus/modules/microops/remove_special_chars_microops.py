"""
Micro-ops: remove special characters

@author: rookielittleblack
@date:   2025-08-13
"""
import re
import string
from typing import Dict, Any, Optional, Set

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_special_chars")
class RemoveSpecialCharsMicroops(OperatorABC):
    """
    Special characters removal micro-operation with configurable character sets
    and unified error handling.
    
    Features:
    - Customizable character removal sets
    - Preserves essential punctuation optionally
    - Unicode-aware processing
    - Configurable replacement options
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the special characters removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - replacement_text: Text to replace special chars with (default: '')
                - preserve_basic_punctuation: Keep .,!?;: (default: True)
                - preserve_quotes: Keep quotes and apostrophes (default: True)
                - preserve_parentheses: Keep ()[]{}  (default: True)
                - preserve_math_symbols: Keep +-*/=<>% (default: False)
                - custom_preserve_chars: Additional chars to preserve (default: '')
                - custom_remove_chars: Additional chars to force remove (default: '')
                - remove_unicode_symbols: Remove Unicode symbols (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'replacement_text': '',
            'preserve_basic_punctuation': True,
            'preserve_quotes': True,
            'preserve_parentheses': True,
            'preserve_math_symbols': False,
            'custom_preserve_chars': '',
            'custom_remove_chars': '',
            'remove_unicode_symbols': False
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Build character sets
        self._build_character_sets()
        
        # Statistics
        self.stats = {
            'special_chars_removed': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _build_character_sets(self):
        """Build character sets for removal and preservation."""
        # Start with all punctuation and symbols
        all_special = set(string.punctuation)
        
        # Add common Unicode symbols if configured
        if self.config['remove_unicode_symbols']:
            # Common Unicode symbol ranges
            unicode_symbols = set()
            for i in range(0x2000, 0x206F):  # General Punctuation
                unicode_symbols.add(chr(i))
            for i in range(0x2190, 0x21FF):  # Arrows
                unicode_symbols.add(chr(i))
            for i in range(0x2200, 0x22FF):  # Mathematical Operators
                unicode_symbols.add(chr(i))
            all_special.update(unicode_symbols)
        
        # Build preserve set based on configuration
        preserve_chars = set()
        
        if self.config['preserve_basic_punctuation']:
            preserve_chars.update('.,!?;:')
        
        if self.config['preserve_quotes']:
            preserve_chars.update('\'""`''""')
        
        if self.config['preserve_parentheses']:
            preserve_chars.update('()[]{}<>')
        
        if self.config['preserve_math_symbols']:
            preserve_chars.update('+-*/=<>%')
        
        # Add custom preserve chars
        if self.config['custom_preserve_chars']:
            preserve_chars.update(self.config['custom_preserve_chars'])
        
        # Force remove custom chars even if they would be preserved
        force_remove = set(self.config['custom_remove_chars'])
        preserve_chars -= force_remove
        
        # Final removal set = all special chars - preserved chars
        self.remove_chars = all_special - preserve_chars
        
        # Create regex pattern for efficient removal
        if self.remove_chars:
            escaped_chars = [re.escape(char) for char in self.remove_chars]
            self.removal_pattern = re.compile(f'[{"".join(escaped_chars)}]+')
        else:
            self.removal_pattern = None
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
        
        xlogger.debug(f"Special chars to remove: {len(self.remove_chars)} characters")
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除文本中的特殊字符，可配置保留规则"
        elif lang == "en":
            return "Remove special characters from text with configurable preservation rules"
        else:
            return "Special characters removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove special characters from the input string.
        
        Args:
            input_string: Input text containing special characters
            
        Returns:
            Cleaned text with special characters removed
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_special_chars,
            args=(input_string,),
            max_retries=2,
            operation_name="Special characters removal"
        )
    
    def _remove_special_chars(self, text: str) -> str:
        """
        Internal method to remove special characters from text.
        
        Args:
            text: Input text with special characters
            
        Returns:
            Cleaned text without unwanted special characters
        """
        try:
            original_text = text
            
            if self.removal_pattern:
                # Count characters before removal
                chars_before = len(self.removal_pattern.findall(text))
                
                # Remove special characters
                text = self.removal_pattern.sub(self.config['replacement_text'], text)
                
                self.stats['special_chars_removed'] += chars_before
            
            # Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Log statistics periodically
            if self.stats['special_chars_removed'] % 1000 == 0 and self.stats['special_chars_removed'] > 0:
                xlogger.debug(f"Special chars removal stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"Special chars removal failed for text sample: {text[:100]}... Error: {e}")
            return original_text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'special_chars_removed': self.stats['special_chars_removed'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 