import os
import glob
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from aiearth.predict.logging import root_logger as logger


def remove_files(files: Union[str, List[str]]):
    if isinstance(files, str):
        files = [files]
    for file_pattern in files:
        file_list = glob.glob(file_pattern)
        for file in file_list:
            try:
                os.remove(file)
            except:
                logger.warn("error while deleting file : ", file)
