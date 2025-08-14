"""
Micro-ops: remove HTML tags

@author: rookielittleblack
@date:   2025-08-13
"""
import re
from typing import Dict, Any, Optional
from html import unescape

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_html_tags")
class RemoveHTMLTagsMicroops(OperatorABC):
    """
    HTML tags removal micro-operation with comprehensive tag detection
    and unified error handling.
    
    Features:
    - Removes HTML and XML tags while preserving text content
    - Handles nested tags and malformed HTML
    - Configurable replacement options
    - Preserves whitespace structure optionally
    - Supports custom tag whitelist/blacklist
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the HTML tags removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - preserve_formatting: Keep basic text formatting (default: False)
                - replace_with_space: Replace tags with space instead of empty (default: True)
                - decode_entities: Decode HTML entities like &amp; (default: True)
                - remove_style_script: Remove <style> and <script> content (default: True)
                - whitelist_tags: List of tags to preserve (default: [])
                - preserve_links: Convert <a> tags to plain URLs (default: False)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'preserve_formatting': False,
            'replace_with_space': True,
            'decode_entities': True,
            'remove_style_script': True,
            'whitelist_tags': [],
            'preserve_links': False
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'tags_removed': 0,
            'entities_decoded': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for HTML processing."""
        # Basic HTML tag pattern (matches opening and closing tags)
        self.html_tag_pattern = re.compile(
            r'<[^>]*>', 
            re.IGNORECASE | re.DOTALL
        )
        
        # Style and script content removal
        self.style_script_pattern = re.compile(
            r'<(style|script)[^>]*>.*?</\1>',
            re.IGNORECASE | re.DOTALL
        )
        
        # HTML comments removal
        self.comment_pattern = re.compile(
            r'<!--.*?-->',
            re.DOTALL
        )
        
        # Link extraction pattern
        self.link_pattern = re.compile(
            r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL
        )
        
        # Whitelist tag pattern (if specified)
        if self.config['whitelist_tags']:
            whitelist = '|'.join(re.escape(tag) for tag in self.config['whitelist_tags'])
            self.whitelist_pattern = re.compile(
                f'</?({whitelist})(?:[^>]*)>',
                re.IGNORECASE
            )
        else:
            self.whitelist_pattern = None
        
        # Multiple whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
        
        # HTML entity pattern for manual decoding if needed
        self.entity_pattern = re.compile(r'&[a-zA-Z0-9#][a-zA-Z0-9]{1,7};')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "移除文本中的HTML标签，保留纯文本内容"
        elif lang == "en":
            return "Remove HTML tags from text while preserving plain text content"
        else:
            return "HTML tags removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove HTML tags from the input string.
        
        Args:
            input_string: Input text containing HTML tags
            
        Returns:
            Cleaned text with HTML tags removed
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_html_tags,
            args=(input_string,),
            max_retries=2,
            operation_name="HTML tags removal"
        )
    
    def _remove_html_tags(self, text: str) -> str:
        """
        Internal method to remove HTML tags from text.
        
        Args:
            text: Input text with HTML tags
            
        Returns:
            Cleaned text without HTML tags
        """
        try:
            original_text = text
            
            # 1. Remove comments first
            text = self.comment_pattern.sub('', text)
            
            # 2. Remove style and script content if configured
            if self.config['remove_style_script']:
                text = self.style_script_pattern.sub('', text)
            
            # 3. Handle links specially if preserve_links is enabled
            if self.config['preserve_links']:
                def replace_link(match):
                    url = match.group(1)
                    link_text = match.group(2)
                    # Return format: "link_text (url)" or just url if no text
                    if link_text.strip() and link_text.strip() != url:
                        return f"{link_text.strip()} ({url})"
                    return url
                
                text = self.link_pattern.sub(replace_link, text)
            
            # 4. Handle whitelist tags (preserve them)
            preserved_tags = []
            if self.whitelist_pattern:
                preserved_tags = self.whitelist_pattern.findall(text)
                # Temporarily replace whitelist tags with placeholders
                for i, tag_match in enumerate(self.whitelist_pattern.finditer(text)):
                    text = text.replace(tag_match.group(0), f"__PRESERVE_TAG_{i}__")
            
            # 5. Remove all remaining HTML tags
            tags_before = len(self.html_tag_pattern.findall(text))
            text = self.html_tag_pattern.sub(
                ' ' if self.config['replace_with_space'] else '', 
                text
            )
            self.stats['tags_removed'] += tags_before
            
            # 6. Restore whitelist tags if any
            if preserved_tags:
                for i, tag in enumerate(preserved_tags):
                    text = text.replace(f"__PRESERVE_TAG_{i}__", tag)
            
            # 7. Decode HTML entities if configured
            if self.config['decode_entities']:
                entities_before = len(self.entity_pattern.findall(text))
                text = unescape(text)
                self.stats['entities_decoded'] += entities_before
            
            # 8. Normalize whitespace unless preserving formatting
            if not self.config['preserve_formatting']:
                text = self.whitespace_pattern.sub(' ', text)
                text = text.strip()
            
            # Log statistics periodically
            if self.stats['tags_removed'] % 1000 == 0 and self.stats['tags_removed'] > 0:
                xlogger.debug(f"HTML cleaning stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"HTML tag removal failed for text sample: {text[:100]}... Error: {e}")
            # Return original text on failure
            return original_text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'tags_removed': self.stats['tags_removed'],
            'entities_decoded': self.stats['entities_decoded'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 