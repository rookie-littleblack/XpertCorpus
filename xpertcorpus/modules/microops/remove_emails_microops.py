"""
Micro-ops: remove emails

@author: rookielittleblack
@date:   2025-08-13
"""
import re
from typing import Dict, Any, Optional

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_emails")
class RemoveEmailsMicroops(OperatorABC):
    """
    Email address removal micro-operation with comprehensive email detection
    and unified error handling.
    
    Features:
    - Detects various email formats including international domains
    - Supports domain-specific filtering
    - Configurable masking vs complete removal
    - Preserves context optionally
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - replacement_text: Text to replace emails with (default: '')
                - mask_instead_remove: Replace with masked format like u***@***.com (default: False)
                - preserve_domains: Keep domain parts when masking (default: False)
                - whitelist_domains: List of domains to preserve (default: [])
                - case_sensitive: Case sensitive domain matching (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'replacement_text': '',
            'mask_instead_remove': False,
            'preserve_domains': False,
            'whitelist_domains': [],
            'case_sensitive': False
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'emails_removed': 0,
            'emails_masked': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for email detection."""
        # Comprehensive email pattern
        self.email_pattern = re.compile(
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            re.IGNORECASE if not self.config['case_sensitive'] else 0
        )
        
        # More strict email pattern for validation
        self.strict_email_pattern = re.compile(
            r'\b[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]{0,62}[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+\b',
            re.IGNORECASE if not self.config['case_sensitive'] else 0
        )
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除或脱敏文本中的邮箱地址"
        elif lang == "en":
            return "Remove or mask email addresses in text"
        else:
            return "Email removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove or mask emails from the input string.
        
        Args:
            input_string: Input text containing emails
            
        Returns:
            Cleaned text with emails removed or masked
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_emails,
            args=(input_string,),
            max_retries=2,
            operation_name="Email removal"
        )
    
    def _remove_emails(self, text: str) -> str:
        """
        Internal method to remove emails from text.
        
        Args:
            text: Input text with emails
            
        Returns:
            Cleaned text without emails
        """
        try:
            original_text = text
            
            def replace_email(match):
                email = match.group(0)
                
                if self._should_remove_email(email):
                    if self.config['mask_instead_remove']:
                        masked = self._mask_email(email)
                        self.stats['emails_masked'] += 1
                        return masked
                    else:
                        self.stats['emails_removed'] += 1
                        return self.config['replacement_text']
                
                return email
            
            # Apply email replacement
            text = self.email_pattern.sub(replace_email, text)
            
            # Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Log statistics periodically
            total_processed = self.stats['emails_removed'] + self.stats['emails_masked']
            if total_processed % 500 == 0 and total_processed > 0:
                xlogger.debug(f"Email processing stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"Email removal failed for text sample: {text[:100]}... Error: {e}")
            return original_text
    
    def _should_remove_email(self, email: str) -> bool:
        """
        Determine if an email should be removed based on configuration.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email should be removed, False otherwise
        """
        try:
            # Extract domain
            domain = email.split('@')[-1]
            
            # Check case sensitivity
            check_domain = domain if self.config['case_sensitive'] else domain.lower()
            
            # Check whitelist
            whitelist = [d if self.config['case_sensitive'] else d.lower() 
                        for d in self.config['whitelist_domains']]
            
            if whitelist:
                # Only remove if not in whitelist
                return not any(check_domain == wd or check_domain.endswith('.' + wd) for wd in whitelist)
            
            # Default: remove emails
            return True
            
        except Exception:
            # On error, default to removing
            return True
    
    def _mask_email(self, email: str) -> str:
        """
        Mask an email address preserving some structure.
        
        Args:
            email: Email address to mask
            
        Returns:
            Masked email address
        """
        try:
            local, domain = email.split('@', 1)
            
            # Mask local part
            if len(local) <= 2:
                masked_local = '*' * len(local)
            else:
                masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
            
            # Mask domain if not preserving
            if self.config['preserve_domains']:
                masked_domain = domain
            else:
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    # Mask domain name but keep TLD
                    masked_name = '*' * len(domain_parts[0])
                    masked_domain = masked_name + '.' + '.'.join(domain_parts[1:])
                else:
                    masked_domain = '*' * len(domain)
            
            return f"{masked_local}@{masked_domain}"
            
        except Exception:
            # Fallback to simple masking
            return '***@***.***'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'emails_removed': self.stats['emails_removed'],
            'emails_masked': self.stats['emails_masked'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 