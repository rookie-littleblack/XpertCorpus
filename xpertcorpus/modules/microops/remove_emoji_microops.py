"""
Micro-ops: remove emoji

@author: rookielittleblack
@date:   2025-08-12
"""
import re

from typing import Dict, Any, Optional
from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


@register_operator("remove_emoji")
class RemoveEmojiMicroops(OperatorABC):
    """
    Enhanced emoji removal micro-operation with comprehensive emoji detection
    and unified error handling.
    
    Improvements:
    - Expanded emoji pattern coverage (Unicode 15.0 support)
    - Performance optimization with compiled patterns
    - Configurable replacement options (remove vs substitute)
    - Integrated unified error handling system
    - Support for skin tone modifiers and zero-width joiners
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the emoji removal micro-operation.
        
        Args:
            config: Configuration dictionary with optional parameters:
                - replacement_text: Text to replace emojis with (default: '')
                - preserve_text_emoji: Whether to preserve text-based emoticons (default: True)
                - remove_skin_tones: Whether to remove skin tone modifiers (default: True)
                - remove_zwj_sequences: Whether to remove ZWJ sequences (default: True)
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        self.retry_mechanism = XRetryMechanism(max_retries=2, base_delay=0.1)
        
        # Configuration parameters
        self.replacement_text = self.config.get('replacement_text', '')
        self.preserve_text_emoji = self.config.get('preserve_text_emoji', True)
        self.remove_skin_tones = self.config.get('remove_skin_tones', True)
        self.remove_zwj_sequences = self.config.get('remove_zwj_sequences', True)
        
        xlogger.info(f"Initializing {self.__class__.__name__} with config: {self.config}")
        
        # Compile comprehensive emoji patterns
        self._compile_emoji_patterns()

    def _compile_emoji_patterns(self) -> None:
        """Compile comprehensive emoji detection patterns for better performance."""
        
        # Main emoji pattern with Unicode 15.0 support
        emoji_ranges = [
            # Basic emoji blocks
            r'\U0001F600-\U0001F64F',  # Emoticons
            r'\U0001F300-\U0001F5FF',  # Miscellaneous Symbols and Pictographs
            r'\U0001F680-\U0001F6FF',  # Transport and Map Symbols
            r'\U0001F1E0-\U0001F1FF',  # Regional Indicator Symbols (flags)
            
            # Extended emoji blocks
            r'\U0001F700-\U0001F77F',  # Alchemical Symbols
            r'\U0001F780-\U0001F7FF',  # Geometric Shapes Extended
            r'\U0001F800-\U0001F8FF',  # Supplemental Arrows-C
            r'\U0001F900-\U0001F9FF',  # Supplemental Symbols and Pictographs
            r'\U0001FA00-\U0001FA6F',  # Chess Symbols
            r'\U0001FA70-\U0001FAFF',  # Symbols and Pictographs Extended-A
            
            # Additional Unicode blocks with emoji
            r'\U00002600-\U000026FF',  # Miscellaneous Symbols
            r'\U00002700-\U000027BF',  # Dingbats
            r'\U0001F000-\U0001F02F',  # Mahjong Tiles
            r'\U0001F0A0-\U0001F0FF',  # Playing Cards
            
            # Enclosed characters that might be emojis
            r'\U000024C2-\U0001F251',  # Enclosed characters
            r'\U0001F100-\U0001F1FF',  # Enclosed Alphanumeric Supplement
        ]
        
        # Skin tone modifiers
        skin_tone_pattern = r'[\U0001F3FB-\U0001F3FF]'
        
        # Zero Width Joiner (ZWJ) sequences pattern
        zwj_pattern = r'\u200D'
        
        # Variation selectors (emoji vs text presentation)
        variation_selectors = r'[\uFE00-\uFE0F]'
        
        # Combine all emoji ranges
        emoji_base_pattern = f'[{"".join(emoji_ranges)}]'
        
        # Build comprehensive pattern
        if self.remove_skin_tones and self.remove_zwj_sequences:
            # Pattern that matches emoji with optional skin tones, ZWJ sequences, and variation selectors
            emoji_pattern = (
                f'(?:{emoji_base_pattern}'
                f'(?:{skin_tone_pattern})?'
                f'(?:{variation_selectors})?'
                f'(?:{zwj_pattern}{emoji_base_pattern}(?:{skin_tone_pattern})?(?:{variation_selectors})?)*'
                f')'
            )
        elif self.remove_skin_tones:
            # Pattern without ZWJ but with skin tones
            emoji_pattern = f'{emoji_base_pattern}(?:{skin_tone_pattern})?(?:{variation_selectors})?'
        elif self.remove_zwj_sequences:
            # Pattern with ZWJ but without skin tone consideration
            emoji_pattern = f'(?:{emoji_base_pattern}(?:{variation_selectors})?(?:{zwj_pattern}{emoji_base_pattern}(?:{variation_selectors})?)*)'
        else:
            # Basic pattern without special handling
            emoji_pattern = f'{emoji_base_pattern}(?:{variation_selectors})?'
        
        # Compile the main emoji pattern
        self.emoji_pattern = re.compile(emoji_pattern, flags=re.UNICODE)
        
        # Additional patterns for edge cases
        self.edge_case_patterns = [
            # Keycap sequences (like 1️⃣, 2️⃣, etc.)
            re.compile(r'[0-9#*]\uFE0F?\u20E3', re.UNICODE),
            # Tag sequences for subdivision flags
            re.compile(r'\U0001F3F4[\U000E0060-\U000E007F]+\U000E007F', re.UNICODE),
            # Fitzpatrick skin tone modifiers standalone
            re.compile(r'[\U0001F3FB-\U0001F3FF]', re.UNICODE),
        ]
        
        # Text-based emoticons pattern (if preservation is disabled)
        if not self.preserve_text_emoji:
            # Common text emoticons pattern
            self.text_emoticon_pattern = re.compile(
                r'(?:[:;=8][\'\-]?[)\](}>|DdPp\\\/\[]|'  # Basic emoticons
                r'[)\]}>|DdPp\\\/\[]\s*[:;=8]|'         # Reverse emoticons
                r'<3|</3|<\\3|\\o/|o_O|O_o|'           # Special cases
                r'\^\^|\^_\^|>_<|ಠ_ಠ|¯\\_(ツ)_/¯)',     # Unicode emoticons
                re.UNICODE
            )
        else:
            self.text_emoticon_pattern = None

    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        return (
            "全面移除文本中的 Unicode 表情符号，支持肤色修饰符和 ZWJ 序列" 
            if lang == "zh" 
            else "Comprehensively remove Unicode emojis including skin tone modifiers and ZWJ sequences."
        )
    
    def _remove_emojis(self, text: str) -> str:
        """
        Remove emojis from text using compiled patterns.
        
        Args:
            text: Input text
            
        Returns:
            Text with emojis removed
        """
        # Remove main emoji patterns
        text = self.emoji_pattern.sub(self.replacement_text, text)
        
        # Remove edge case patterns
        for pattern in self.edge_case_patterns:
            text = pattern.sub(self.replacement_text, text)
        
        # Remove text emoticons if configured
        if self.text_emoticon_pattern:
            text = self.text_emoticon_pattern.sub(self.replacement_text, text)
        
        # Clean up multiple consecutive spaces that might result from removal
        if self.replacement_text == '':
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    def run(self, input_string: str) -> str:
        """
        Enhanced emoji removal with error handling and performance optimization.
        
        Args:
            input_string: Input text to process
            
        Returns:
            Text with emojis removed
        """
        if not input_string:
            return input_string

        def _process_text() -> str:
            return self._remove_emojis(input_string)

        try:
            # Use retry mechanism for processing
            result = self.retry_mechanism.execute(_process_text)
            
            # Log processing statistics
            original_length = len(input_string)
            processed_length = len(result)
            if original_length != processed_length:
                xlogger.debug(
                    f"Emoji removal: {original_length} -> {processed_length} characters "
                    f"({original_length - processed_length} characters removed)"
                )
            
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e,
                context=f"Processing text with length {len(input_string)}",
                operation="remove_emoji"
            )
            xlogger.error(f"Error in emoji removal: {error_info}")
            return input_string  # Return original on error