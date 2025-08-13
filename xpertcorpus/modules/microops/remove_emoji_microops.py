"""
Micro-ops: remove emoji

@author: rookielittleblack
@date:   2025-08-12
"""
import re

from xpertcorpus.utils import xlogger
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


@OPERATOR_REGISTRY.register()
class RemoveEmojiMicroops(OperatorABC):
    def __init__(self):
        xlogger.info(f"Initializing {self.__class__.__name__} ...")

        # Emoji pattern for matching emojis in the text
        self.emoji_pattern = re.compile(
            "[" 
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U0001F300-\U0001F5FF"  # Miscellaneous symbols and pictographs
            u"\U0001F680-\U0001F6FF"  # Transport and map symbols
            u"\U0001F1E0-\U0001F1FF"  # Flags
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"  # Enclosed characters
            "]+", 
            flags=re.UNICODE
        )

    @staticmethod
    def get_desc(lang: str = "zh"):
        return "去除文本中的表情符号" if lang == "zh" else "Remove emojis from the text."
    
    def run(self, input_string: str):
        if not input_string:
            return input_string
            
        try:
            
            return self.emoji_pattern.sub(r'', input_string)
        except Exception as e:
            return input_string