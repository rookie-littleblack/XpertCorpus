import os

from transformers import AutoTokenizer
from xpertcorpus.utils.xlogger import xlogger


def get_xtokenizer():
    """
    Get XTokenizer

    Remarks: using ​​Qwen3-8B-tokenizer​​ as the default tokenizer for approximate token counting
    """
    # Use internal tokenizer
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))
    tokenizer_dir = os.path.join(project_root, "xpertcorpus/resources/tokenizers/qwen3-8b-tokenizer")
    xlogger.debug(f"tokenizer_dir: `{tokenizer_dir}`")
    
    # Check whether tokenizer_dir exists
    if not os.path.exists(tokenizer_dir):
        raise FileNotFoundError(f"Tokenizer directory not found: `{tokenizer_dir}`")
    
    # Tokenizer
    xtokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, trust_remote_code=True)

    # Return
    return xtokenizer

def count_tokens(text: str) -> int:
    """
    Calculate the number of tokens in a string.
    
    Args:
        text (str): Input text to count tokens from
        
    Returns:
        int: Number of tokens in the text
    """
    try:
        return len(get_xtokenizer().encode(text))
    except ImportError:
        xlogger.error("Something wrong with transformer tokenizer, falling back to simple tokenization")
        return len(text.split())


# Run as a script to check the functions: `python -m xpertcorpus.utils.xutils`
if __name__ == "__main__":

    # Test count_tokens
    xlogger.info(f"count_tokens('Hello, world! I am XpertCorpus!'): `{count_tokens('Hello, world! I am XpertCorpus!')}`")
    xlogger.info(f"count_tokens('你好啊，我是XpertCorpus！'): `{count_tokens('你好啊，我是XpertCorpus！')}`")