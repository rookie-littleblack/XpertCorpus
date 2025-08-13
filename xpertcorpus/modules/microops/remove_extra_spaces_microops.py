"""
Micro-ops: remove extra spaces

@author: rookielittleblack
@date:   2025-08-12
"""
import re
from typing import Dict, Any, Optional, List, Tuple

from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_extra_spaces")
class RemoveExtraSpacesMicroops(OperatorABC):
    """
    Enhanced extra spaces removal micro-operation with performance optimization
    and unified error handling.
    
    Optimizations:
    - Integrated unified error handling system
    - Improved code block detection performance
    - Added configuration parameters support
    - Better regex patterns compilation and caching
    - Enhanced processing logic with validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the spaces removal micro-operation.
        
        Args:
            config: Configuration dictionary with optional parameters:
                - max_indent_preservation: Maximum indentation to preserve (default: 4)
                - code_detection_threshold: Threshold for code detection (default: 0.3)
                - preserve_code_blocks: Whether to preserve code blocks (default: True)
                - remove_trailing_spaces: Whether to remove trailing spaces (default: True)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        self.retry_mechanism = XRetryMechanism(max_retries=2, base_delay=0.1)
        
        # Configuration parameters
        self.max_indent_preservation = self.config.get('max_indent_preservation', 4)
        self.code_detection_threshold = self.config.get('code_detection_threshold', 0.3)
        self.preserve_code_blocks = self.config.get('preserve_code_blocks', True)
        self.remove_trailing_spaces = self.config.get('remove_trailing_spaces', True)
        
        xlogger.info(f"Initializing {self.__class__.__name__} with config: {self.config}")
        
        # Pre-compiled regex patterns for better performance
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile and cache regex patterns for better performance."""
        # Code block detection patterns
        self.code_patterns = [
            # Fenced code blocks (``` or ~~~ delimited)
            re.compile(r'```[\s\S]*?```', re.MULTILINE),
            re.compile(r'~~~[\s\S]*?~~~', re.MULTILINE),
            # Indented code blocks (4+ spaces at line start)
            re.compile(r'^[ \t]{4,}.*$', re.MULTILINE),
            # Inline code (single backticks)
            re.compile(r'`[^`\n]+`'),
            # HTML pre/code tags
            re.compile(r'<pre[\s\S]*?</pre>', re.IGNORECASE),
            re.compile(r'<code[\s\S]*?</code>', re.IGNORECASE),
            # Common programming language patterns
            re.compile(r'^(def|function|class|public|private|protected)\s+\w+', re.MULTILINE),
            # Lines with programming characters
            re.compile(r'.*[{}();=><\[\]]+.*', re.MULTILINE),
        ]
        
        # Text cleaning patterns
        self.cleanup_patterns = {
            'carriage_return': re.compile(r'\r'),
            'multiple_newlines': re.compile(r'\n{3,}'),
            'multiple_spaces': re.compile(r' {2,}'),
            'trailing_spaces': re.compile(r' +$', re.MULTILINE),
            'mixed_whitespace': re.compile(r'[ \t]+'),
        }
        
        # Code detection keywords (compiled for faster lookup)
        self.code_keywords = {
            'def ', 'function ', 'class ', 'import ', 'from ', 'return ', 
            'if ', 'else:', 'for ', 'while ', 'try:', 'except:', 'var ',
            'let ', 'const ', 'public ', 'private ', 'protected '
        }

    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        return (
            "智能移除文本中的多余空格和换行符，保护代码块格式" 
            if lang == "zh" 
            else "Intelligently remove extra spaces and newlines while preserving code blocks."
        )
    
    def _is_likely_code(self, text: str) -> bool:
        """
        Enhanced code detection with better performance.
        
        Args:
            text: Text to analyze
            
        Returns:
            bool: True if text is likely code
        """
        if not text.strip():
            return False
            
        # Quick pattern matching first
        for pattern in self.code_patterns:
            if pattern.search(text):
                return True
        
        # Statistical analysis for borderline cases
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return False
        
        code_indicators = 0
        total_lines = len(lines)
        
        for line in lines:
            # Check for programming keywords (optimized with set lookup)
            if any(keyword in line.lower() for keyword in self.code_keywords):
                code_indicators += 1
                continue
                
            # Check for other code patterns
            if any([
                ' = ' in line and not line.startswith('#'),  # Assignment
                line.count('(') + line.count(')') >= 2,      # Function calls
                line.endswith(';') or line.endswith('{') or line.endswith('}'),  # Syntax
                line.startswith('    ') and len(line) > 4,   # Indentation
                '->' in line or '=>' in line or '::' in line # Language specific
            ]):
                code_indicators += 1
        
        return (code_indicators / total_lines) > self.code_detection_threshold
    
    def _preserve_code_blocks(self, text: str) -> Tuple[str, List[str], str]:
        """
        Preserve code blocks during processing.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (processed_text, code_blocks, placeholder_pattern)
        """
        if not self.preserve_code_blocks:
            return text, [], ""
            
        code_blocks = []
        placeholder_pattern = "___CODE_BLOCK_PLACEHOLDER_{}_END___"
        
        # Extract all code blocks (process in reverse to avoid index shifting)
        for pattern in self.code_patterns:
            matches = list(pattern.finditer(text))
            for match in reversed(matches):
                code_content = match.group()
                placeholder = placeholder_pattern.format(len(code_blocks))
                code_blocks.append(code_content)
                text = text[:match.start()] + placeholder + text[match.end():]
        
        return text, code_blocks, placeholder_pattern
    
    def _restore_code_blocks(self, text: str, code_blocks: List[str], placeholder_pattern: str) -> str:
        """
        Restore preserved code blocks.
        
        Args:
            text: Text with placeholders
            code_blocks: List of preserved code blocks
            placeholder_pattern: Pattern used for placeholders
            
        Returns:
            Text with restored code blocks
        """
        for i, code_block in enumerate(code_blocks):
            placeholder = placeholder_pattern.format(i)
            text = text.replace(placeholder, code_block)
        return text
    
    def _clean_text_content(self, text: str) -> str:
        """
        Clean text content with improved logic.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Step 1: Remove carriage returns
        text = self.cleanup_patterns['carriage_return'].sub('', text)
        
        # Step 2: Normalize multiple newlines
        text = self.cleanup_patterns['multiple_newlines'].sub('\n\n', text)
        
        # Step 3: Process paragraphs individually
        paragraphs = text.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                processed_paragraphs.append(paragraph)
                continue
                
            # Check if paragraph contains code
            if self._is_likely_code(paragraph):
                # Preserve code formatting
                processed_paragraphs.append(paragraph)
            else:
                # Clean regular text
                lines = paragraph.split('\n')
                processed_lines = []
                
                for line in lines:
                    if not line.strip():
                        processed_lines.append(line)
                        continue
                        
                    # Preserve reasonable indentation
                    leading_spaces = len(line) - len(line.lstrip())
                    content = line.strip()
                    
                    if content:
                        # Clean multiple spaces in content
                        cleaned_content = self.cleanup_patterns['multiple_spaces'].sub(' ', content)
                        
                        # Reconstruct with preserved indentation
                        if leading_spaces > 0:
                            indent = ' ' * min(leading_spaces, self.max_indent_preservation)
                            processed_line = indent + cleaned_content
                        else:
                            processed_line = cleaned_content
                    else:
                        processed_line = line
                    
                    processed_lines.append(processed_line)
                
                processed_paragraphs.append('\n'.join(processed_lines))
        
        text = '\n\n'.join(processed_paragraphs)
        
        # Step 4: Additional cleanup
        if self.remove_trailing_spaces:
            text = self.cleanup_patterns['trailing_spaces'].sub('', text)
        
        # Step 5: Normalize mixed whitespace (except in code)
        # Only apply to non-code segments
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if not self._is_likely_code(line):
                lines[i] = self.cleanup_patterns['mixed_whitespace'].sub(' ', line)
        text = '\n'.join(lines)
        
        # Step 6: Strip document-level whitespace
        text = text.strip()
        
        return text
    
    def run(self, input_string: str) -> str:
        """
        Enhanced run method with error handling and performance optimization.
        
        Args:
            input_string: Input text to process
            
        Returns:
            Processed text with extra spaces removed
        """
        if not input_string:
            return input_string

        def _process_text() -> str:
            # Step 1: Preserve code blocks
            output_string, code_blocks, placeholder_pattern = self._preserve_code_blocks(input_string)
            
            # Step 2: Clean text content
            output_string = self._clean_text_content(output_string)
            
            # Step 3: Restore code blocks
            if code_blocks:
                output_string = self._restore_code_blocks(output_string, code_blocks, placeholder_pattern)
            
            return output_string

        try:
            # Use retry mechanism for processing
            result = self.retry_mechanism.execute(_process_text)
            xlogger.debug(f"Successfully processed text: {len(input_string)} -> {len(result)} characters")
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                context=f"Processing text with length {len(input_string)}",
                operation="remove_extra_spaces"
            )
            xlogger.error(f"Error in removing extra spaces: {error_info}")
            return input_string  # Return original on error