"""
Micro-ops module initialization

This module provides various micro-operations for text processing.
All classes can be imported directly from this module.

@author: rookielittleblack
@date:   2025-08-12
"""
from .remove_emoji_microops import RemoveEmojiMicroops
from .remove_emoticons_microops import RemoveEmoticonsMicroops
from .remove_extra_spaces_microops import RemoveExtraSpacesMicroops

# Text cleaning micro-operations (new)
from .remove_urls_microops import RemoveURLsMicroops
from .remove_emails_microops import RemoveEmailsMicroops
from .remove_html_tags_microops import RemoveHTMLTagsMicroops
from .remove_phone_numbers_microops import RemovePhoneNumbersMicroops
from .remove_special_chars_microops import RemoveSpecialCharsMicroops
from .remove_non_printable_microops import RemoveNonPrintableMicroops
from .remove_footer_header_microops import RemoveFooterHeaderMicroops


# Export all classes for easy importing
__all__ = [
    # Original micro-operations
    'RemoveEmoticonsMicroops',
    'RemoveEmojiMicroops', 
    'RemoveExtraSpacesMicroops',
    
    # Text cleaning micro-operations
    'RemoveHTMLTagsMicroops',
    'RemoveURLsMicroops',
    'RemoveEmailsMicroops',
    'RemovePhoneNumbersMicroops',
    'RemoveSpecialCharsMicroops',
    'RemoveNonPrintableMicroops',
    'RemoveFooterHeaderMicroops',
]
