"""
This script is used to generate llm training corpus.

Usage:
    python -m xpertcorpus.main --input ./data/raw_content_test_1.jsonl --output ./output --max_workers 1

@author: rookielittleblack
@date:   2025-08-11
"""
import argparse

from xpertcorpus.utils import xlogger
from xpertcorpus.modules.frameworks.xframe_pt import XFramework_PT

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=str, default="./data/20250710-1750_raw_content_test_1.jsonl", help="The input file path, or the raw files directory path.")
    parser.add_argument("--output", "-o", type=str, default="./output", help="The output directory path.")
    parser.add_argument("--max_workers", "-m", type=int, default=1, help="The number of workers.")
    parser.add_argument("--limit", "-l", type=int, default=0, help="The number of limit, 0 means no limit.")
    args = parser.parse_args()

    # Initialize framework
    framework = XFramework_PT(
        input_file=args.input,
        output_dir=args.output,
        max_workers=args.max_workers,
        limit=args.limit
    )

    # Run framework
    framework.run()

    # Get framework info
    xlogger.debug(f"framework_info: {framework.get_pipeline_info()}")


if __name__ == "__main__":
    main()
