"""
Micro-ops: remove footer and header

@author: rookielittleblack
@date:   2025-08-13
"""
import re
from typing import Dict, Any, Optional, List

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_footer_header")
class RemoveFooterHeaderMicroops(OperatorABC):
    """
    Footer and header removal micro-operation with intelligent pattern detection
    and unified error handling.
    
    Features:
    - Detects common footer/header patterns
    - Removes page numbers and navigation elements
    - Configurable pattern customization
    - Preserves main content structure
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the footer/header removal micro-operation.
        
        Args:
            config: Configuration dictionary with options:
                - remove_page_numbers: Remove page number patterns (default: True)
                - remove_copyright: Remove copyright notices (default: True)
                - remove_navigation: Remove navigation text (default: True)
                - custom_patterns: Additional regex patterns to remove (default: [])
                - min_line_length: Minimum line length to preserve (default: 10)
                - max_header_lines: Maximum lines to check at start (default: 5)
                - max_footer_lines: Maximum lines to check at end (default: 5)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        
        # Default configuration
        default_config = {
            'remove_page_numbers': True,
            'remove_copyright': True,
            'remove_navigation': True,
            'custom_patterns': [],
            'min_line_length': 10,
            'max_header_lines': 5,
            'max_footer_lines': 5
        }
        
        # Merge with provided config
        self.config.update(default_config)
        if config:
            self.config.update(config)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        
        # Statistics
        self.stats = {
            'headers_removed': 0,
            'footers_removed': 0,
            'page_numbers_removed': 0,
            'copyright_removed': 0,
            'processing_errors': 0
        }
        
        xlogger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    def _compile_patterns(self):
        """Compile regex patterns for footer/header detection."""
        patterns = []
        
        # Page number patterns
        if self.config['remove_page_numbers']:
            page_patterns = [
                r'^page\s+\d+\s*$',
                r'^\d+\s*$',
                r'^-\s*\d+\s*-\s*$',
                r'^\[\s*\d+\s*\]$',
                r'^\d+\s*/\s*\d+$',
                r'^\d+\s+of\s+\d+$',
            ]
            patterns.extend(page_patterns)
        
        # Copyright patterns
        if self.config['remove_copyright']:
            copyright_patterns = [
                r'^\s*©.*\d{4}.*$',
                r'^\s*copyright.*\d{4}.*$',
                r'^\s*\(c\).*\d{4}.*$',
                r'^\s*all rights reserved.*$',
                r'^\s*proprietary and confidential.*$',
            ]
            patterns.extend(copyright_patterns)
        
        # Navigation patterns
        if self.config['remove_navigation']:
            nav_patterns = [
                r'^\s*next\s*\|\s*previous\s*$',
                r'^\s*home\s*\|\s*back\s*\|\s*forward\s*$',
                r'^\s*click here.*$',
                r'^\s*continue reading.*$',
                r'^\s*read more.*$',
                r'^\s*back to top.*$',
                r'^\s*table of contents.*$',
                r'^\s*index\s*$',
            ]
            patterns.extend(nav_patterns)
        
        # Common header/footer patterns
        common_patterns = [
            r'^\s*printed on.*\d{4}.*$',
            r'^\s*generated on.*\d{4}.*$',
            r'^\s*last updated.*\d{4}.*$',
            r'^\s*confidential.*$',
            r'^\s*draft.*$',
            r'^\s*version\s+\d+.*$',
            r'^\s*document\s+\d+.*$',
        ]
        patterns.extend(common_patterns)
        
        # Add custom patterns
        patterns.extend(self.config['custom_patterns'])
        
        # Compile all patterns
        self.removal_patterns = []
        for pattern in patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                self.removal_patterns.append(compiled)
            except re.error as e:
                xlogger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        # Line separator detection
        self.line_separator_pattern = re.compile(r'\r\n|\r|\n')
        
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        if lang == "zh":
            return "智能识别并移除文档的页眉页脚内容"
        elif lang == "en":
            return "Intelligently detect and remove document headers and footers"
        else:
            return "Footer and header removal micro-operation"
    
    def run(self, input_string: str) -> str:
        """
        Remove footer and header from the input string.
        
        Args:
            input_string: Input text containing headers/footers
            
        Returns:
            Cleaned text with headers/footers removed
        """
        if not input_string or not isinstance(input_string, str):
            return input_string or ""
        
        return self.error_handler.execute_with_retry(
            func=self._remove_footer_header,
            args=(input_string,),
            max_retries=2,
            operation_name="Footer/header removal"
        )
    
    def _remove_footer_header(self, text: str) -> str:
        """
        Internal method to remove footers and headers from text.
        
        Args:
            text: Input text with headers/footers
            
        Returns:
            Cleaned text without headers/footers
        """
        try:
            original_text = text
            
            # Split text into lines
            lines = self.line_separator_pattern.split(text)
            if not lines:
                return text
            
            # Track removed lines
            headers_removed = 0
            footers_removed = 0
            
            # Process header lines (from start)
            start_idx = 0
            max_header = min(len(lines), self.config['max_header_lines'])
            
            for i in range(max_header):
                line = lines[i].strip()
                if self._should_remove_line(line):
                    start_idx = i + 1
                    headers_removed += 1
                elif line and len(line) >= self.config['min_line_length']:
                    # Found substantial content, stop header removal
                    break
            
            # Process footer lines (from end)
            end_idx = len(lines)
            max_footer = min(len(lines) - start_idx, self.config['max_footer_lines'])
            
            for i in range(1, max_footer + 1):
                line_idx = len(lines) - i
                if line_idx < start_idx:
                    break
                
                line = lines[line_idx].strip()
                if self._should_remove_line(line):
                    end_idx = line_idx
                    footers_removed += 1
                elif line and len(line) >= self.config['min_line_length']:
                    # Found substantial content, stop footer removal
                    break
            
            # Extract clean content
            cleaned_lines = lines[start_idx:end_idx]
            
            # Remove matching patterns from remaining lines
            final_lines = []
            for line in cleaned_lines:
                if not self._should_remove_line(line.strip()):
                    final_lines.append(line)
                else:
                    # Count specific pattern types
                    self._count_pattern_match(line.strip())
            
            # Reconstruct text
            text = '\n'.join(final_lines)
            
            # Clean up extra whitespace
            text = self.whitespace_pattern.sub(' ', text)
            text = text.strip()
            
            # Update statistics
            self.stats['headers_removed'] += headers_removed
            self.stats['footers_removed'] += footers_removed
            
            # Log statistics periodically
            total_removed = self.stats['headers_removed'] + self.stats['footers_removed']
            if total_removed % 100 == 0 and total_removed > 0:
                xlogger.debug(f"Footer/header removal stats: {self.stats}")
            
            return text
            
        except Exception as e:
            self.stats['processing_errors'] += 1
            xlogger.warning(f"Footer/header removal failed for text sample: {text[:100]}... Error: {e}")
            return original_text
    
    def _should_remove_line(self, line: str) -> bool:
        """
        Check if a line should be removed based on patterns.
        
        Args:
            line: Line to check
            
        Returns:
            True if line should be removed, False otherwise
        """
        if not line:
            return False
        
        # Too short lines are likely not main content
        if len(line) < self.config['min_line_length']:
            # But check if it's just a page number or similar
            if re.match(r'^\d+$', line.strip()):
                return True
        
        # Check against all patterns
        for pattern in self.removal_patterns:
            if pattern.match(line):
                return True
        
        return False
    
    def _count_pattern_match(self, line: str) -> None:
        """
        Count specific types of pattern matches for statistics.
        
        Args:
            line: Line that matched a pattern
        """
        # Check for page numbers
        if re.match(r'^\d+$|^page\s+\d+|^\d+\s*/\s*\d+$', line, re.IGNORECASE):
            self.stats['page_numbers_removed'] += 1
        
        # Check for copyright
        elif re.match(r'.*copyright.*|.*©.*|\(c\).*|.*all rights reserved.*', line, re.IGNORECASE):
            self.stats['copyright_removed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'microop_name': self.__class__.__name__,
            'headers_removed': self.stats['headers_removed'],
            'footers_removed': self.stats['footers_removed'],
            'page_numbers_removed': self.stats['page_numbers_removed'],
            'copyright_removed': self.stats['copyright_removed'],
            'processing_errors': self.stats['processing_errors'],
            'config': self.config
        } 