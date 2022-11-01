from abc import ABCMeta, abstractmethod


class BaseTransformer(metaclass=ABCMeta):
    """
    Asbtract base transformer class.
    """
    def __init__(self, **kwargs):
        """ Initializes class. """

    def fit(self, X, y=None):
        """ Just returns class, if nothing to fit. """
        return self

    def fit_transform(self, X, y=None, **kwargs):
        return self.fit(X, y, **kwargs).transform(X)

    @abstractmethod
    def transform(self, X):
        """ Abstract method for "DIY" transformations. """


class BaseObject(dict):
    """
    Base object dictionary class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
