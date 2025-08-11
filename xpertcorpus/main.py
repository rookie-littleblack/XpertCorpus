"""
This script is used to generate llm training corpus.

Usage:
    python -m xpertcorpus.main --input ./data/raw_content_test_1.jsonl --output ./cache_local --max_workers 1

@author: rookielittleblack
@date:   2025-08-11
"""
import os
import json
import argparse

from datetime import datetime
from xpertcorpus.utils.xutils import count_tokens
from xpertcorpus.utils.xlogger import get_logger
from xpertcorpus.utils.xstorage import FileStorage
from xpertcorpus.operators.generate.XGenertors import XGeneratorPT, XTextSplitter, XLimitor


class XPipeline():
    """
    XPipeline is a pipeline for generating pretrain data.
    """

    def __init__(self, input_file: str, output_dir: str = "./cache_local", max_workers: int = 1, limit: int = 0):
        """
        Initialize the XPipeline.

        Args:
            input_file: The input file path.
            output_dir: The output directory path.
            max_workers: The number of workers.
            limit: The number of limit, 0 means no limit.
        """
        # Parameters
        self.is_raw_corpus = False
        self.input_file = input_file
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.limit = limit

        # Set logger
        self.logger = get_logger()

        # Check paths
        self._check_paths()

        # Print log
        self.logger.info("XPipeline is initializing: input_file=`{}`, output_dir=`{}`, max_workers=`{}`, limit=`{}`".format(self.input_file, self.output_dir, self.max_workers, self.limit))

        # Process raw corpus
        if self.is_raw_corpus:
            self.process_raw_corpus()
            return None  # Stop here
        
        # Initialize limitor
        self.limitor = XLimitor(limit=self.limit)

        # Initialize storage
        self.storage = FileStorage(first_entry_file_name=self.input_file, cache_path=self.output_dir)

        # Initialize operators
        self.pt_generator = XGeneratorPT(max_workers=self.max_workers)

        # Initialize corpus text splitter
        self.corpus_text_splitter = XTextSplitter(
            #chunk_size=16*1024,
            chunk_size=512,
            chunk_overlap=200,

            # split_method="semantic",
            split_method="markdown",

            min_tokens_per_chunk=20
        )

    def _check_paths(self):
        """
        Check the paths.
        """
        # Check output directory (if it is ./cache or ./cache_local, then add timestamp to the directory name)
        if self.output_dir == "./cache" or self.output_dir == "./cache_local":
            self.output_dir = os.path.join(self.output_dir, datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(self.output_dir, exist_ok=True)

        # Check input file (or directory)
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"===> Input file not found: `{self.input_file}`")
        else:
            if os.path.isdir(self.input_file):
                self.logger.info(f"===> Input path is a directory (not a file): `{self.input_file}`, will be processed as raw text/markdown corpus to generate cleaned JSONL corpus.")
                self.is_raw_corpus = True  # Set flag to True
            else:
                self.logger.info(f"===> Input path is a file: `{self.input_file}`, will be processed as potential cleaned corpus.")
                self.is_raw_corpus = False  # Keep flag as False

    def process_raw_corpus(self):
        """
        Process raw corpus: from raw text/markdown corpus to cleaned JSONL corpus.
        """
        self.logger.info("===> Processing raw corpus...")
        
        # Get all .txt/.md files in the directory and the subdirectories
        files_list = []
        for root, _, filenames in os.walk(self.input_file):
            for file in filenames:
                abs_file_path = os.path.join(root, file)
                if ".bak" not in abs_file_path and (file.endswith(".txt") or file.endswith(".md")):
                    files_list.append(abs_file_path)
        
        # Check if any files were found
        if not files_list:
            self.logger.warning(f"No .txt or .md files found in `{self.input_file}`")
            self.input_file = None
            return
        else:
            self.logger.info(f"===> Found {len(files_list)} files in the directory: `{self.input_file}`")

        # Process each file
        i = 0
        total_tokens = 0
        preprocessed_raw_file_list = os.path.join(self.output_dir, "preprocess_raw_corpus_files_list.tsv")
        preprocessed_jsonl_file = os.path.join(self.output_dir, "preprocess_raw_corpus.jsonl")
        with open(preprocessed_raw_file_list, "w", encoding="utf-8") as outfile1:
            with open(preprocessed_jsonl_file, "w", encoding="utf-8") as outfile2:
                for file in files_list:
                    i = i + 1
                    self.logger.info(f"===> Processing file {str(i)}: `{file}`")

                    # Read file
                    with open(file, "r", encoding="utf-8") as infile:
                        content = infile.read()

                    # Count tokens
                    tokens = count_tokens(content)
                    total_tokens += tokens

                    # Write to jsonl file
                    outfile2.write(json.dumps({"file_path": file, "raw_content": content, "raw_content_tokens": tokens}, ensure_ascii=False) + "\n")

                    # Write to tsv file
                    outfile1.write(file + "\t" + str(tokens) + "\n")

        # Log
        self.logger.info(f"===> Raw corpus processing done: processed {i} files, total tokens: `{total_tokens}`...")

        # Update input file path to the new one
        self.logger.info(f"===> Update input file path `{self.input_file}` to the new one: `{preprocessed_jsonl_file}`...")
        self.input_file = preprocessed_jsonl_file

    def forward(self):
        """
        Run the pipeline.
        """
        # Check if input file is None
        if self.input_file is None:
            self.logger.warning("===> Input file is None, stop running.")
            return None
        
        # Check file type is jsonl
        if not self.input_file.endswith(".jsonl"):
            self.logger.warning("===> Input file is not a jsonl file, stop running.")
            return None

        # Reset token usage
        self.pt_generator.llm_serving.reset_token_counts()
        self.logger.info(f"===> Token usage have been reset.")

        # Start pipeline
        self.logger.info("===> Starting running XPipeline...")
        self.logger.info("======================================================")

        # Run limitor
        if self.limit > 0:
            self.logger.info(self.limitor.get_desc(lang="en"))
            self.limitor.run(self.storage.step())

        # Run pt generator
        self.logger.info(self.pt_generator.get_desc(lang="en"))
        pt_generator_output_key = self.pt_generator.run(
            self.storage.step(),
            input_key="raw_content"
        )
        self.logger.info(f"===> PT generator output key: `{pt_generator_output_key}`")

        # Run corpus text splitter
        self.logger.info(self.corpus_text_splitter.get_desc(lang="en"))
        corpus_text_splitter_output_key = self.corpus_text_splitter.run(
            self.storage.step(),
            input_key=pt_generator_output_key
        )
        self.logger.info(f"===> Corpus text splitter output key: `{corpus_text_splitter_output_key}`")












        # Print final output path
        self.logger.info(f"===> Output path: `{self.storage.cache_path}`")

        # Print token usage
        self.logger.info(f"===> Token usage: {self.pt_generator.llm_serving.get_token_counts()}")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=str, default="./data/20250710-1750_raw_content_test_1.jsonl", help="The input file path, or the raw files directory path.")
    parser.add_argument("--output", "-o", type=str, default="./cache_local", help="The output directory path.")
    parser.add_argument("--max_workers", "-m", type=int, default=1, help="The number of workers.")
    parser.add_argument("--limit", "-l", type=int, default=0, help="The number of limit, 0 means no limit.")
    args = parser.parse_args()

    # Initialize pipeline
    pipeline = XPipeline(
        input_file=args.input,
        output_dir=args.output,
        max_workers=args.max_workers,
        limit=args.limit
    )

    # Run pipeline
    pipeline.forward()


if __name__ == "__main__":
    main()
