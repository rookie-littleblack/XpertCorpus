"""
Micro-ops: remove URLs

@author: rookielittleblack
@date:   2025-08-13
"""
import re
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_urls")
class RemoveURLsMicroops(OperatorABC):
    """
    URL removal micro-operation with comprehensive URL detection
    and unified error handling.
    
    Features:
    - Detects and removes various URL formats (http, https, ftp, etc.)
    - Supports domain-specific filtering
    - Configurable replacement options  
    - Preserves URL text or domain optionally
    - Handles malformed and partial URLs
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the URL removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - replacement_text: Text to replace URLs with (default: '')
                - preserve_domains: Keep domain names when removing URLs (default: False)
                - whitelist_domains: List of domains to preserve (default: [])
                - blacklist_domains: List of domains to force remove (default: [])
                - remove_partial_urls: Remove incomplete URLs like www.example (default: True)
                - preserve_email_domains: Don't remove URLs that look like email domains (default: True)
                - case_sensitive: Case sensitive domain matching (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'replacement_text': '',
            'preserve_domains': False,
            'whitelist_domains': [],
            'blacklist_domains': [],
            'remove_partial_urls': True,
            'preserve_email_domains': True,
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
            'urls_removed': 0,
            'domains_preserved': 0,
            'partial_urls_removed': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for URL detection and processing."""
        # Comprehensive URL pattern with various schemes
        url_schemes = r'(?:https?|ftp|ftps|sftp|ssh|file|data|mailto|tel|sms)://'
        
        # Domain pattern - matches domain names with TLDs
        domain_part = r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'
        
        # Full URL pattern with optional scheme
        self.full_url_pattern = re.compile(
            rf'(?:{url_schemes})?(?:www\.)?{domain_part}(?::[0-9]{{1,5}})?(?:/[^\s]*)?',
            re.IGNORECASE if not self.config['case_sensitive'] else 0
        )
        
        # Scheme-based URLs (more strict)
        self.scheme_url_pattern = re.compile(
            rf'{url_schemes}[^\s<>"{{}}|\\^`\[\]]+',
            re.IGNORECASE if not self.config['case_sensitive'] else 0
        )
        
        # Partial URLs (www.example.com, example.com)
        if self.config['remove_partial_urls']:
            # Common TLDs for partial URL detection
            common_tlds = r'(?:com|org|net|edu|gov|mil|int|co|io|me|tv|cc|to|ly|be|it|de|fr|uk|cn|jp|au|ca|us|ru|br|in|mx|nl|se|no|dk|fi|pl|cz|sk|hu|ro|bg|hr|si|ee|lv|lt|es|pt|gr|tr|il|ae|sa|za|eg|ma|ng|ke|gh|tz|ug|zm|zw|mw|bw|na|sz|ls|mg|mu|sc|km|dj|so|et|er|sd|ly|tn|dz|ma|mr|ml|bf|ne|td|cf|cm|gq|ga|cg|cd|ao|zm|mw|mz|mg|mu|re|yt|sc|km|dj|so|et|er|sd|ss|ly|tn|dz|ma|eh)'
            
            self.partial_url_pattern = re.compile(
                rf'\b(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{{0,61}}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{{0,61}}[a-zA-Z0-9])?)*\.(?:{common_tlds})\b(?:/[^\s]*)?',
                re.IGNORECASE if not self.config['case_sensitive'] else 0
            )
        else:
            self.partial_url_pattern = None
        
        # Email domain pattern (to avoid removing email-like domains)
        if self.config['preserve_email_domains']:
            self.email_domain_pattern = re.compile(
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
                re.IGNORECASE
            )
        else:
            self.email_domain_pattern = None
        
        # Domain extraction pattern for preservation
        self.domain_extraction_pattern = re.compile(
            rf'(?:{url_schemes})?(?:www\.)?([a-zA-Z0-9.-]+)',
            re.IGNORECASE if not self.config['case_sensitive'] else 0
        )
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除文本中的URL链接，支持多种URL格式和配置选项"
        elif lang == "en":
            return "Remove URLs from text with support for various formats and configuration options"
        else:
            return "URL removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove URLs from the input string.
        
        Args:
            input_string: Input text containing URLs
            
        Returns:
            Cleaned text with URLs removed or replaced
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_urls,
            args=(input_string,),
            max_retries=2,
            operation_name="URL removal"
        )
    
    def _remove_urls(self, text: str) -> str:
        """
        Internal method to remove URLs from text.
        
        Args:
            text: Input text with URLs
            
        Returns:
            Cleaned text without URLs
        """
        try:
            original_text = text
            
            # 1. Find and preserve email addresses if configured
            preserved_emails = []
            if self.email_domain_pattern:
                emails = self.email_domain_pattern.findall(text)
                for i, email in enumerate(emails):
                    text = text.replace(email, f"__PRESERVE_EMAIL_{i}__", 1)
                    preserved_emails.append(email)
            
            # 2. Handle scheme-based URLs first (most reliable)
            urls_found = self.scheme_url_pattern.findall(text)
            for url in urls_found:
                if self._should_remove_url(url):
                    replacement = self._get_url_replacement(url)
                    text = text.replace(url, replacement, 1)
                    self.stats['urls_removed'] += 1
            
            # 3. Handle full URLs (with or without scheme)
            def replace_full_url(match):
                url = match.group(0)
                if self._should_remove_url(url):
                    self.stats['urls_removed'] += 1
                    return self._get_url_replacement(url)
                return url
            
            text = self.full_url_pattern.sub(replace_full_url, text)
            
            # 4. Handle partial URLs if configured
            if self.partial_url_pattern:
                def replace_partial_url(match):
                    url = match.group(0)
                    if self._should_remove_url(url):
                        self.stats['partial_urls_removed'] += 1
                        return self._get_url_replacement(url)
                    return url
                
                text = self.partial_url_pattern.sub(replace_partial_url, text)
            
            # 5. Restore preserved emails
            for i, email in enumerate(preserved_emails):
                text = text.replace(f"__PRESERVE_EMAIL_{i}__", email)
            
            # 6. Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Log statistics periodically
            if self.stats['urls_removed'] % 500 == 0 and self.stats['urls_removed'] > 0:
                xlogger.debug(f"URL removal stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"URL removal failed for text sample: {text[:100]}... Error: {e}")
            # Return original text on failure
            return original_text
    
    def _should_remove_url(self, url: str) -> bool:
        """
        Determine if a URL should be removed based on configuration.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL should be removed, False otherwise
        """
        try:
            # Extract domain from URL
            domain = self._extract_domain(url)
            if not domain:
                return True  # Remove malformed URLs
            
            # Check case sensitivity
            check_domain = domain if self.config['case_sensitive'] else domain.lower()
            
            # Check blacklist first (takes precedence)
            blacklist = [d if self.config['case_sensitive'] else d.lower() 
                        for d in self.config['blacklist_domains']]
            if any(check_domain == bd or check_domain.endswith('.' + bd) for bd in blacklist):
                return True
            
            # Check whitelist
            whitelist = [d if self.config['case_sensitive'] else d.lower() 
                        for d in self.config['whitelist_domains']]
            if whitelist:
                # Only remove if not in whitelist
                return not any(check_domain == wd or check_domain.endswith('.' + wd) for wd in whitelist)
            
            # Default: remove URLs
            return True
            
        except Exception:
            # On error, default to removing
            return True
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain name or None if extraction fails
        """
        try:
            # Add scheme if missing for urlparse
            if not url.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
                url = 'http://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            
            # Remove port if present
            domain = domain.split(':')[0]
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
            
        except Exception:
            # Fallback to regex extraction
            match = self.domain_extraction_pattern.search(url)
            return match.group(1) if match else None
    
    def _get_url_replacement(self, url: str) -> str:
        """
        Get replacement text for a URL based on configuration.
        
        Args:
            url: URL to replace
            
        Returns:
            Replacement text
        """
        if self.config['preserve_domains']:
            domain = self._extract_domain(url)
            if domain:
                self.stats['domains_preserved'] += 1
                return domain
        
        return self.config['replacement_text']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'urls_removed': self.stats['urls_removed'],
            'domains_preserved': self.stats['domains_preserved'], 
            'partial_urls_removed': self.stats['partial_urls_removed'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 