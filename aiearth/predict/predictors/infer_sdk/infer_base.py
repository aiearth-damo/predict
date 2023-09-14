import numpy as np
from typing import Dict, List
from abc import ABC, abstractmethod


class InferBase(ABC):
    @abstractmethod
    def infer(self, inputs: List[np.ndarray]):
        raise NotImplementedError()
