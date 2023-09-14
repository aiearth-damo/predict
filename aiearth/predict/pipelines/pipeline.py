from abc import ABCMeta, abstractmethod


class Pipeline(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError()

    @abstractmethod
    def __call__(self):
        raise NotImplementedError()
