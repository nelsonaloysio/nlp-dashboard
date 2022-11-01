from abc import ABCMeta, abstractmethod


class Transformer(metaclass=ABCMeta):
    """
    Asbtract base transformer class.
    """
    def __init__(self, **kwargs):
        """ Initializes class. """

    def fit(self, X, y=None):
        """ Just returns class, if nothing to fit. """
        return self

    @abstractmethod
    def transform(self, X):
        """ Abstract method for "DIY" transformations. """


class Object(dict):
    """
    Base object dictionary class.
    """
    def __init__(self, *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)
        self.__dict__ = self
