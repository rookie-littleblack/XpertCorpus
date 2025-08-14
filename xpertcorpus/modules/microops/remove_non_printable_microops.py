"""
Micro-ops: remove non-printable characters

@author: rookielittleblack
@date:   2025-08-13
"""
import re
import unicodedata
from typing import Dict, Any, Optional

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_non_printable")
class RemoveNonPrintableMicroops(OperatorABC):
    """
    Non-printable characters removal micro-operation with Unicode-aware processing
    and unified error handling.
    
    Features:
    - Removes control characters and non-printable Unicode
    - Preserves essential whitespace (space, tab, newline)
    - Configurable replacement options
    - Unicode category-based filtering
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the non-printable characters removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - replacement_text: Text to replace non-printable chars with (default: '')
                - preserve_whitespace: Keep space, tab, newline (default: True)
                - preserve_zero_width: Keep zero-width characters (default: False)
                - remove_bom: Remove Byte Order Mark (default: True)
                - strict_ascii: Only allow ASCII printable characters (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'replacement_text': '',
            'preserve_whitespace': True,
            'preserve_zero_width': False,
            'remove_bom': True,
            'strict_ascii': False
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'non_printable_removed': 0,
            'control_chars_removed': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for non-printable character detection."""
        # Control characters (0x00-0x1F, 0x7F-0x9F)
        self.control_chars_pattern = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
        
        # Byte Order Mark (BOM)
        if self.config['remove_bom']:
            self.bom_pattern = re.compile(r'[\uFEFF\uFFFE\u0000FEFF\u0000FFFE]')
        else:
            self.bom_pattern = None
        
        # Zero-width characters
        if not self.config['preserve_zero_width']:
            self.zero_width_pattern = re.compile(r'[\u200B-\u200F\u2028-\u202E\u2060-\u2064\u206A-\u206F]')
        else:
            self.zero_width_pattern = None
        
        # Preserved whitespace if configured
        if self.config['preserve_whitespace']:
            self.preserve_chars = {'\t', '\n', '\r', ' '}
        else:
            self.preserve_chars = set()
        
        # ASCII printable range for strict mode
        if self.config['strict_ascii']:
            # ASCII printable: 0x20-0x7E plus preserved whitespace
            ascii_printable = set(chr(i) for i in range(0x20, 0x7F))
            ascii_printable.update(self.preserve_chars)
            self.allowed_chars = ascii_printable
        else:
            self.allowed_chars = None
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除文本中的不可打印字符和控制字符"
        elif lang == "en":
            return "Remove non-printable and control characters from text"
        else:
            return "Non-printable characters removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove non-printable characters from the input string.
        
        Args:
            input_string: Input text containing non-printable characters
            
        Returns:
            Cleaned text with non-printable characters removed
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_non_printable,
            args=(input_string,),
            max_retries=2,
            operation_name="Non-printable characters removal"
        )
    
    def _remove_non_printable(self, text: str) -> str:
        """
        Internal method to remove non-printable characters from text.
        
        Args:
            text: Input text with non-printable characters
            
        Returns:
            Cleaned text without non-printable characters
        """
        try:
            original_text = text
            
            # 1. Remove BOM if configured
            if self.bom_pattern:
                bom_count = len(self.bom_pattern.findall(text))
                text = self.bom_pattern.sub('', text)
                self.stats['non_printable_removed'] += bom_count
            
            # 2. Remove control characters
            control_count = len(self.control_chars_pattern.findall(text))
            text = self.control_chars_pattern.sub(self.config['replacement_text'], text)
            self.stats['control_chars_removed'] += control_count
            
            # 3. Remove zero-width characters if configured
            if self.zero_width_pattern:
                zw_count = len(self.zero_width_pattern.findall(text))
                text = self.zero_width_pattern.sub('', text)
                self.stats['non_printable_removed'] += zw_count
            
            # 4. Strict ASCII mode - remove all non-ASCII printable
            if self.allowed_chars:
                filtered_chars = []
                for char in text:
                    if char in self.allowed_chars:
                        filtered_chars.append(char)
                    else:
                        filtered_chars.append(self.config['replacement_text'])
                        self.stats['non_printable_removed'] += 1
                text = ''.join(filtered_chars)
            else:
                # 5. Unicode category-based filtering
                filtered_chars = []
                for char in text:
                    if self._is_printable_unicode(char):
                        filtered_chars.append(char)
                    else:
                        filtered_chars.append(self.config['replacement_text'])
                        self.stats['non_printable_removed'] += 1
                text = ''.join(filtered_chars)
            
            # 6. Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Log statistics periodically
            total_removed = self.stats['non_printable_removed'] + self.stats['control_chars_removed']
            if total_removed % 1000 == 0 and total_removed > 0:
                xlogger.debug(f"Non-printable removal stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"Non-printable removal failed for text sample: {text[:100]}... Error: {e}")
            return original_text
    
    def _is_printable_unicode(self, char: str) -> bool:
        """
        Check if a Unicode character is printable.
        
        Args:
            char: Single character to check
            
        Returns:
            True if character is printable, False otherwise
        """
        # Always preserve configured whitespace
        if char in self.preserve_chars:
            return True
        
        # Get Unicode category
        category = unicodedata.category(char)
        
        # Categories to preserve:
        # L* - Letters
        # N* - Numbers  
        # P* - Punctuation (except some control-like)
        # S* - Symbols (except some private use)
        # Zs - Space separators (if preserving whitespace)
        
        if category.startswith(('L', 'N')):  # Letters and Numbers
            return True
        
        if category.startswith('P'):  # Punctuation
            # Exclude some problematic punctuation categories
            if category in ('Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps'):
                return True
        
        if category.startswith('S'):  # Symbols
            # Exclude private use and some control symbols
            if category in ('Sc', 'Sk', 'Sm', 'So'):
                return True
        
        if category == 'Zs' and self.config['preserve_whitespace']:  # Space separators
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'non_printable_removed': self.stats['non_printable_removed'],
            'control_chars_removed': self.stats['control_chars_removed'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 