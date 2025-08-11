"""
This script is used to define the framework of generating pretraining data.

Usage:
    python -m xpertcorpus.main --input ./data/raw_content_test_1.jsonl --output ./output --max_workers 1

@author: rookielittleblack
@date:   2025-08-11
"""
import os
import json

from datetime import datetime
from xpertcorpus.utils.xutils import count_tokens
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xstorage import FileStorage
from xpertcorpus.modules.others.xlimitor import XLimitor
from xpertcorpus.modules.operators.xplitter import XTextSplitter
from xpertcorpus.modules.pipelines.xpipe_pt import XPipeline_PT


class XFramework_PT():
    """
    XFramework_PT is a framework for generating pretrain data.
    """

    def __init__(self, input_file: str, output_dir: str = "./output", max_workers: int = 1, limit: int = 0):
        """
        Initialize the XFramework_PT.

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

        # Check paths
        self._check_paths()

        # Print log
        xlogger.info("XFramework_PT is initializing: input_file=`{}`, output_dir=`{}`, max_workers=`{}`, limit=`{}`".format(self.input_file, self.output_dir, self.max_workers, self.limit))

        # Process raw corpus
        if self.is_raw_corpus:
            self.process_raw_corpus()
            return None  # Stop here
        
        # Initialize limitor
        self.limitor = XLimitor(limit=self.limit)

        # Initialize storage
        self.storage = FileStorage(first_entry_file_name=self.input_file, cache_path=self.output_dir)

        # Initialize operators
        self.pt_generator = XPipeline_PT(max_workers=self.max_workers)

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
        # Check output directory (if it is ./output, then add timestamp to the directory name)
        if self.output_dir == "./output":
            self.output_dir = os.path.join(self.output_dir, datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(self.output_dir, exist_ok=True)

        # Check input file (or directory)
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"===> Input file not found: `{self.input_file}`")
        else:
            if os.path.isdir(self.input_file):
                xlogger.info(f"===> Input path is a directory (not a file): `{self.input_file}`, will be processed as raw text/markdown corpus to generate cleaned JSONL corpus.")
                self.is_raw_corpus = True  # Set flag to True
            else:
                xlogger.info(f"===> Input path is a file: `{self.input_file}`, will be processed as potential cleaned corpus.")
                self.is_raw_corpus = False  # Keep flag as False

    def process_raw_corpus(self):
        """
        Process raw corpus: from raw text/markdown corpus to cleaned JSONL corpus.
        """
        xlogger.info("===> Processing raw corpus...")
        
        # Get all .txt/.md files in the directory and the subdirectories
        files_list = []
        for root, _, filenames in os.walk(self.input_file):
            for file in filenames:
                abs_file_path = os.path.join(root, file)
                if ".bak" not in abs_file_path and (file.endswith(".txt") or file.endswith(".md")):
                    files_list.append(abs_file_path)
        
        # Check if any files were found
        if not files_list:
            xlogger.warning(f"No .txt or .md files found in `{self.input_file}`")
            self.input_file = None
            return
        else:
            xlogger.info(f"===> Found {len(files_list)} files in the directory: `{self.input_file}`")

        # Process each file
        i = 0
        total_tokens = 0
        preprocessed_raw_file_list = os.path.join(self.output_dir, "preprocess_raw_corpus_files_list.tsv")
        preprocessed_jsonl_file = os.path.join(self.output_dir, "preprocess_raw_corpus.jsonl")
        with open(preprocessed_raw_file_list, "w", encoding="utf-8") as outfile1:
            with open(preprocessed_jsonl_file, "w", encoding="utf-8") as outfile2:
                for file in files_list:
                    i = i + 1
                    xlogger.info(f"===> Processing file {str(i)}: `{file}`")

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
        xlogger.info(f"===> Raw corpus processing done: processed {i} files, total tokens: `{total_tokens}`...")

        # Update input file path to the new one
        xlogger.info(f"===> Update input file path `{self.input_file}` to the new one: `{preprocessed_jsonl_file}`...")
        self.input_file = preprocessed_jsonl_file

    def forward(self):
        """
        Run the pipeline.
        """
        # Check if input file is None
        if self.input_file is None:
            xlogger.warning("===> Input file is None, stop running.")
            return None
        
        # Check file type is jsonl
        if not self.input_file.endswith(".jsonl"):
            xlogger.warning("===> Input file is not a jsonl file, stop running.")
            return None

        # Reset token usage
        self.pt_generator.xapi.reset_token_counts()
        xlogger.info(f"===> Token usage have been reset.")

        # Start pipeline
        xlogger.info("===> Starting running XFramework_PT...")
        xlogger.info("======================================================")

        # Run limitor
        if self.limit > 0:
            xlogger.info(self.limitor.get_desc(lang="en"))
            self.limitor.run(self.storage.step())

        # Run pt generator
        xlogger.info(self.pt_generator.get_desc(lang="en"))
        pt_generator_output_key = self.pt_generator.run(
            self.storage.step(),
            input_key="raw_content"
        )
        xlogger.info(f"===> PT generator output key: `{pt_generator_output_key}`")

        # Run corpus text splitter
        xlogger.info(self.corpus_text_splitter.get_desc(lang="en"))
        corpus_text_splitter_output_key = self.corpus_text_splitter.run(
            self.storage.step(),
            input_key=pt_generator_output_key
        )
        xlogger.info(f"===> Corpus text splitter output key: `{corpus_text_splitter_output_key}`")












        # Print final output path
        xlogger.info(f"===> Output path: `{self.storage.cache_path}`")

        # Print token usage
        xlogger.info(f"===> Token usage: {self.pt_generator.xapi.get_token_counts()}")