"""
Micro-ops module initialization

This module provides various micro-operations for text processing.
All classes can be imported directly from this module.

@author: rookielittleblack
@date:   2025-08-12
"""
from .remove_emoticons_microops import RemoveEmoticonsMicroops
from .remove_emoji_microops import RemoveEmojiMicroops

# Version information
__version__ = '1.0.0'
__author__ = 'rookielittleblack' 

# Export all classes for easy importing
__all__ = [
    'RemoveEmoticonsMicroops',
    'RemoveEmojiMicroops',
]
