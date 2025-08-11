"""
XXXXXX

@author: rookielittleblack
@date:   2025-08-11
"""
from abc import ABC, abstractmethod
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


class OperatorABC(ABC):

    @abstractmethod
    def run(self) -> None:
        """
        Main function to run the operator.
        """
        pass

def get_operator(operator_name, args) -> OperatorABC:
    xlogger.info(f"get_operator: operator_name: '{operator_name}', args: '{args}'..")

    # Get operator
    operator = OPERATOR_REGISTRY.get(operator_name)(args)
    if operator is not None:
        xlogger.info(f"Successfully get operator {operator_name}, args {args}")
    else:
        xlogger.error(f"operator {operator_name} is not found")
    assert operator is not None
    xlogger.info(f"get_operator: operator: '{operator}'")
    return operator
