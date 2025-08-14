"""
Micro-ops: remove phone numbers

@author: rookielittleblack
@date:   2025-08-13
"""
import re
from typing import Dict, Any, Optional

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_phone_numbers")
class RemovePhoneNumbersMicroops(OperatorABC):
    """
    Phone number removal micro-operation with international format support
    and unified error handling.
    
    Features:
    - Supports various phone number formats (international, national, local)
    - Configurable masking vs complete removal
    - Country-specific pattern support
    - Handles common separators and formats
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the phone number removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - replacement_text: Text to replace phone numbers with (default: '')
                - mask_instead_remove: Replace with masked format (default: False)
                - country_codes: List of country codes to specifically target (default: [])
                - preserve_extensions: Keep extension numbers (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'replacement_text': '',
            'mask_instead_remove': False,
            'country_codes': [],
            'preserve_extensions': False
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'phone_numbers_removed': 0,
            'phone_numbers_masked': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for phone number detection."""
        # International format with country code
        self.intl_pattern = re.compile(
            r'\b(?:\+|00)?[1-9]\d{0,3}[-.\s]?(?:\(\d{1,4}\)[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
        )
        
        # US/North American format
        self.us_pattern = re.compile(
            r'\b(?:1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?ext\.?\s?\d{1,5})?\b'
        )
        
        # General phone number pattern (more flexible)
        self.general_pattern = re.compile(
            r'\b(?:(?:\+|00)?[1-9]\d{0,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,9}\b'
        )
        
        # Pattern for phone numbers with common prefixes
        self.prefix_pattern = re.compile(
            r'\b(?:phone|tel|call|mobile|cell|fax):\s*(?:\+|00)?[1-9][\d\-.\s\(\)]{7,20}\b',
            re.IGNORECASE
        )
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除或脱敏文本中的电话号码"
        elif lang == "en":
            return "Remove or mask phone numbers in text"
        else:
            return "Phone number removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove or mask phone numbers from the input string.
        
        Args:
            input_string: Input text containing phone numbers
            
        Returns:
            Cleaned text with phone numbers removed or masked
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_phone_numbers,
            args=(input_string,),
            max_retries=2,
            operation_name="Phone number removal"
        )
    
    def _remove_phone_numbers(self, text: str) -> str:
        """
        Internal method to remove phone numbers from text.
        
        Args:
            text: Input text with phone numbers
            
        Returns:
            Cleaned text without phone numbers
        """
        try:
            original_text = text
            
            def replace_phone(match):
                phone = match.group(0)
                
                if self._should_remove_phone(phone):
                    if self.config['mask_instead_remove']:
                        masked = self._mask_phone(phone)
                        self.stats['phone_numbers_masked'] += 1
                        return masked
                    else:
                        self.stats['phone_numbers_removed'] += 1
                        return self.config['replacement_text']
                
                return phone
            
            # Apply phone number replacement in order of specificity
            text = self.prefix_pattern.sub(replace_phone, text)
            text = self.us_pattern.sub(replace_phone, text)
            text = self.intl_pattern.sub(replace_phone, text)
            text = self.general_pattern.sub(replace_phone, text)
            
            # Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Log statistics periodically
            total_processed = self.stats['phone_numbers_removed'] + self.stats['phone_numbers_masked']
            if total_processed % 500 == 0 and total_processed > 0:
                xlogger.debug(f"Phone number processing stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"Phone number removal failed for text sample: {text[:100]}... Error: {e}")
            return original_text
    
    def _should_remove_phone(self, phone: str) -> bool:
        """
        Determine if a phone number should be removed.
        
        Args:
            phone: Phone number to check
            
        Returns:
            True if phone should be removed, False otherwise
        """
        # Extract digits only for validation
        digits = re.sub(r'\D', '', phone)
        
        # Basic validation - too short or too long probably not a phone number
        if len(digits) < 7 or len(digits) > 15:
            return False
        
        # If country codes specified, check if phone matches
        if self.config['country_codes']:
            for code in self.config['country_codes']:
                if digits.startswith(str(code)):
                    return True
            return False
        
        # Default: remove all detected phones
        return True
    
    def _mask_phone(self, phone: str) -> str:
        """
        Mask a phone number preserving some structure.
        
        Args:
            phone: Phone number to mask
            
        Returns:
            Masked phone number
        """
        try:
            # Preserve original format structure
            masked = ""
            digits_count = 0
            total_digits = len(re.sub(r'\D', '', phone))
            
            for char in phone:
                if char.isdigit():
                    digits_count += 1
                    # Keep first and last digit, mask middle ones
                    if digits_count == 1 or digits_count == total_digits:
                        masked += char
                    else:
                        masked += '*'
                else:
                    masked += char
            
            return masked
            
        except Exception:
            # Fallback to simple masking
            return '***-***-****'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'phone_numbers_removed': self.stats['phone_numbers_removed'],
            'phone_numbers_masked': self.stats['phone_numbers_masked'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 