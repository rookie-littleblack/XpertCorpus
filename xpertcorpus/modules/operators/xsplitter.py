"""
This operator is used to split text into chunks.

@author: rookielittleblack
@date:   2025-08-11
"""
import pandas as pd

from chonkie import (
    TokenChunker,
    SentenceChunker,
    SemanticChunker,
    RecursiveChunker
)
from xpertcorpus.utils import xlogger, xtokenizer, count_tokens, XpertCorpusStorage
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator


class LangchainMarkdownSplitter:
    """
    A text splitter for markdown files that uses langchain to split by headers
    and then recursively by characters, ensuring semantic completeness.
    """
    def __init__(self, chunk_size: int, chunk_overlap: int, min_tokens_per_chunk: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_tokens_per_chunk = min_tokens_per_chunk
        
        headers_to_split_on = [
            ("#", "H1"),
            ("##", "H2"),
            ("###", "H3"),
            ("####", "H4"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, return_each_line=False)
        
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=count_tokens,
        )

    def __call__(self, text: str):
        class SimpleChunk:
            def __init__(self, text):
                self.text = text

        md_header_splits = self.markdown_splitter.split_text(text)
        
        final_chunks = []
        for doc in md_header_splits:
            header_parts = []
            metadata = doc.metadata
            if 'H1' in metadata: header_parts.append(f"# {metadata['H1']}")
            if 'H2' in metadata: header_parts.append(f"## {metadata['H2']}")
            if 'H3' in metadata: header_parts.append(f"### {metadata['H3']}")
            if 'H4' in metadata: header_parts.append(f"#### {metadata['H4']}")
            header_str = "\n".join(header_parts) + "\n\n" if header_parts else ""

            content_with_header = header_str + doc.page_content.strip()
            
            if count_tokens(content_with_header) > self.chunk_size:
                # Content is too long, split it recursively
                splits = self.recursive_splitter.split_text(doc.page_content)
                for split in splits:
                    chunk_text = header_str + split.strip()
                    if count_tokens(chunk_text) >= self.min_tokens_per_chunk:
                        final_chunks.append(SimpleChunk(chunk_text))
            else:
                # Content is short enough
                if count_tokens(content_with_header) >= self.min_tokens_per_chunk:
                    final_chunks.append(SimpleChunk(content_with_header))
        return final_chunks


@register_operator("text_splitter")
class XTextSplitter(OperatorABC):
    def __init__(self, chunk_size: int = 8192, chunk_overlap: int = 200, split_method: str = "semantic", min_tokens_per_chunk: int = 100, limit: int = 0):
        """
        Initialize the XTextSplitter operator.

        Args:
            chunk_size: The size of each chunk.
            chunk_overlap: The overlap between chunks.
            split_method: The method to split the text.
            min_tokens_per_chunk: The minimum number of tokens per chunk.
            limit: The number of rows to process.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_method = split_method
        self.min_tokens_per_chunk = min_tokens_per_chunk
        self.limit = limit
        self.tokenizer = xtokenizer
        self.chunker = self._initialize_chunker()
        
    @staticmethod
    def get_desc(lang: str = "zh"):
        if(lang=="zh"):
            return (
                "XTextSplitter 是轻量级文本分割工具，",
                "支持词/句/语义/递归分块，",
                "可配置块大小、重叠和最小块长度",
            )
        elif(lang=="en"):
            return (
                "XTextSplitter is a lightweight text segmentation tool",
                "that supports multiple chunking methods",
                "(token/sentence/semantic/recursive) with configurable size and overlap,",
                "optimized for RAG applications."
            )

    def _initialize_chunker(self):
        """Initialize the appropriate chunker based on method"""
        if self.split_method == "token":
            return TokenChunker(  # Attention for the parameters
                tokenizer=self.tokenizer,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        elif self.split_method == "sentence":
            return SentenceChunker(  # Attention for the parameters
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        elif self.split_method == "semantic":
            return SemanticChunker(  # Attention for the parameters
                chunk_size=self.chunk_size,
                min_chunk_size=self.min_tokens_per_chunk
            )
        elif self.split_method == "recursive":
            return RecursiveChunker(  # Attention for the parameters
                chunk_size=self.chunk_size,
                min_characters_per_chunk=self.min_tokens_per_chunk
            )
        elif self.split_method == "markdown":
            return LangchainMarkdownSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                min_tokens_per_chunk=self.min_tokens_per_chunk
            )
        else:
            raise ValueError(f"Unsupported split method: {self.split_method}")

    def _validate_dataframe(self, dataframe: pd.DataFrame):
        forbidden_keys = [self.output_key]
        conflict = [k for k in forbidden_keys if k in dataframe.columns]
        if conflict:
            raise ValueError(f"The following column(s) already exist and would be overwritten: {conflict}")
        
    def _split_text(self, text: str):
        """Split the text into chunks"""
        # Calculate total tokens and max tokens
        total_tokens = count_tokens(text)
        max_tokens = self.tokenizer.model_max_length
        xlogger.info(f"max_tokens: {max_tokens}")

        # Split text by tokens
        if total_tokens <= self.chunk_size:
            # Create a simple chunk object that is compatible with the chunker return object
            class SimpleChunk:
                def __init__(self, text):
                    self.text = text
            
            chunks = [SimpleChunk(text)]
            xlogger.info(f"The input text is less than the chunk size, directly return the text.")
        elif total_tokens <= max_tokens:
            chunks = self.chunker(text)
            xlogger.info(f"Directly split, chunks number: `{len(chunks)}`")
        else:
            # Calculate the number of chunks to split
            x = (total_tokens + max_tokens - 1) // max_tokens
            
            # Split text by words (approximate split)
            words = text.split()  # Split by space
            words_per_chunk = (len(words) + x - 1) // x  # Number of words per chunk
            
            chunks = []
            for i in range(0, len(words), words_per_chunk):
                chunk_text = ' '.join(words[i:i+words_per_chunk])
                chunks.extend(self.chunker(chunk_text))

            xlogger.info(f"Split by words, chunks number: `{len(chunks)}`")

        # Return the chunks
        return chunks
        
    def run(self, storage: XpertCorpusStorage, input_key: str = "raw_content", output_key: str = None):
        """Perform text splitting and save results"""
        self.input_key, self.output_key = input_key, output_key
        xlogger.info(f"Running XTextSplitter: self.input_key: `{self.input_key}`, self.output_key: `{self.output_key}`...")

        # If the output key is not set, use the default output key
        if self.output_key is None:
            self.output_key = f"step{storage.operator_step + 1}_content"
        xlogger.info(f"===> XTextSplitter output key: `{self.output_key}`")

        # Load the raw dataframe from the input file
        dataframe = storage.read('dataframe')
        xlogger.info(f"Loading, total number of rows: {len(dataframe)}")

        # Check if limit is set
        if self.limit > 0:
            dataframe = dataframe.head(self.limit)
            xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")

        # Iterate over the dataframe and split the text into chunks
        new_dataframe = pd.DataFrame()
        for index, row in dataframe.iterrows():
            text = row[self.input_key]
            chunks = self._split_text(text)

            # Iterate over the chunks and generate new dataframe data for each chunk
            for chunk_index, chunk in enumerate(chunks):
                new_item = row.copy()
                new_item[f"{self.output_key}_last_step_index"] = index
                new_item[f"{self.output_key}_last_step_chunk_index"] = chunk_index
                new_item[self.output_key] = chunk.text
                new_item[f"{self.output_key}_tokens"] = count_tokens(chunk.text)
                new_item[f"{self.output_key}_tokens_changed"] = count_tokens(chunk.text) - count_tokens(text)
                new_dataframe = pd.concat([new_dataframe, pd.DataFrame([new_item])], ignore_index=True)

        # Save the new dataframe to the output file
        output_file = storage.write(new_dataframe)
        xlogger.info(f"Successfully split text. Saved to {output_file}")

        # Return the output key
        return self.output_key
