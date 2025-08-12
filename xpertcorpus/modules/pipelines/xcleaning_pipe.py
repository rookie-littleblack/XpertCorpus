"""
This pipeline is used for text cleaning.

@author: rookielittleblack
@date:   2025-08-12
"""
from concurrent.futures import ThreadPoolExecutor
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xstorage import XpertCorpusStorage
from xpertcorpus.modules.microops import RemoveEmoticonsMicroops, RemoveEmojiMicroops
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


@OPERATOR_REGISTRY.register()
class XCleaningPipe(OperatorABC):
    def __init__(self, max_workers: int = 4, limit: int = 0):
        """
        Initialize the XCleaningPipe.
        
        Args:
            max_workers: The number of worker threads for parallel processing.
            limit: The number of limit, 0 means no limit.
        """
        self.max_workers = max_workers
        self.limit = limit

        self.remove_emoticons_microops = RemoveEmoticonsMicroops()
        self.remove_emoji_microops = RemoveEmojiMicroops()
        
    @staticmethod
    def get_desc(lang: str = "zh"):
        if(lang=="zh"):
            return (
                "XCleaningPipe 是文本清洗工作流",
            )
        elif(lang=="en"):
            return (
                "XCleaningPipe is a text cleaning pipeline."
            )
        
    def run(self, storage: XpertCorpusStorage, input_key: str = "raw_content", output_key: str = None):
        self.input_key, self.output_key = input_key, output_key
        """Perform data limiting and save results"""
        xlogger.info(f"Running XCleaningPipe: self.input_key: `{self.input_key}`, self.output_key: `{self.output_key}`...")

        # If the output key is not set, use the default output key
        if self.output_key is None:
            self.output_key = f"step{storage.operator_step + 1}_content"
        xlogger.info(f"===> XCleaningPipe output key: `{self.output_key}`")

        # Load the raw dataframe from the input file
        dataframe = storage.read('dataframe')
        xlogger.info(f"Loading, total number of rows: {len(dataframe)}")

        # Check if limit is set
        if self.limit > 0:
            dataframe = dataframe.head(self.limit)
            xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")

        # Text cleaning
        xlogger.info("Starting text cleaning process...")
        
        # Prepare data for parallel processing
        items = list(dataframe.iterrows())
        
        def clean_text(row):
            """
            Clean text for a single row using emoticon and emoji removal microops.
            This function extracts the raw content, applies cleaning operations,
            and returns the cleaned text.
            """
            try:
                raw_content = row[1].get(self.input_key, '')
                if not raw_content:
                    return raw_content
                
                # Apply text cleaning operations sequentially
                cleaned_text = raw_content
                
                # Remove emoticons
                cleaned_text = self.remove_emoticons_microops.run(cleaned_text)
                
                # Remove emojis
                cleaned_text = self.remove_emoji_microops.run(cleaned_text)
                
                return cleaned_text
                
            except Exception as e:
                xlogger.error(f"Error cleaning text for row {row[0]}: {e}")
                return raw_content  # Return original content if cleaning fails
        
        # Use ThreadPoolExecutor to parallelize text cleaning
        xlogger.info(f"Using {self.max_workers} worker threads for parallel text cleaning...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            cleaned_texts = list(executor.map(clean_text, items))
        
        # Add the cleaned content back to the dataframe
        dataframe[self.output_key] = cleaned_texts
        xlogger.info("Text cleaning completed successfully.")

        # Save the new dataframe to the output file
        output_file = storage.write(dataframe)
        xlogger.info(f"Successfully cleaned text data. Saved to {output_file}")
        
        # Return the output key
        return self.output_key
