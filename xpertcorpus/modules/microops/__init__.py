"""
Micro-ops module initialization

This module provides various micro-operations for text processing.
All classes can be imported directly from this module.

@author: rookielittleblack
@date:   2025-08-12
"""
from .remove_emoticons_microops import RemoveEmoticonsMicroops
from .remove_emoji_microops import RemoveEmojiMicroops
from .remove_extra_spaces_microops import RemoveExtraSpacesMicroops


# Export all classes for easy importing
__all__ = [
    'RemoveEmoticonsMicroops',
    'RemoveEmojiMicroops', 
    'RemoveExtraSpacesMicroops',
]
