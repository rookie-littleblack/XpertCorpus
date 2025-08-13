"""
This operator is used to limit the number of rows in the dataframe.

@author: rookielittleblack
@date:   2025-08-11
"""
from xpertcorpus.utils import xlogger, XpertCorpusStorage
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


@OPERATOR_REGISTRY.register()
class XLimitor(OperatorABC):
    def __init__(self, limit: int = 0):
        """
        Initialize the XLimitor operator.

        Args:
            limit: The number of rows to process.
        """
        self.limit = limit
        
    @staticmethod
    def get_desc(lang: str = "zh"):
        if(lang=="zh"):
            return (
                "XLimitor 是轻量级数据限制工具，",
                "可配置限制数量，用于快速测试",
            )
        elif(lang=="en"):
            return (
                "XLimitor is a lightweight data limitor tool",
                "that supports configurable limit number, for quick testing"
            )
        
    def run(self, storage: XpertCorpusStorage):
        """Perform data limiting and save results"""
        xlogger.info("Running XLimitor...")

        # Load the raw dataframe from the input file
        dataframe = storage.read('dataframe')
        xlogger.info(f"Loading, total number of rows: {len(dataframe)}")

        # Check if limit is set
        if self.limit > 0:
            dataframe = dataframe.head(self.limit)
            xlogger.info(f"Limit is set, number of rows after limit applied: {len(dataframe)}")

        # Save the new dataframe to the output file
        output_file = storage.write(dataframe)
        xlogger.info(f"Successfully limited data. Saved to {output_file}")
        return output_file
