from abc import ABCMeta, abstractmethod

import streamlit as st

CACHE_DATA = {
    "ttl": 1800,
}

CACHE_RESOURCE = {
    "ttl": 1800,
}

CACHE_TO_DISK = {
    "max_entries": 100,
    "persist": "disk",
}


class BaseApp(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self):
        """ Initializes class. """

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def set(self, key, value):
        self.__setattr__(key, value)

    @staticmethod
    def title(title, h=0, spacing=True):
        st.write(
            "{}{} {}".format(
                ("#" * (h if spacing is True else (6 - spacing)) + "\n") if spacing else "",
                "#" * h,
                title,
            )
        )

    @staticmethod
    def error(text="", icon="❌"):
        return st.error(f"{icon} {text}")

    @staticmethod
    def info(text="", icon="ℹ️"):
        return st.info(f"{icon} {text}")

    @staticmethod
    def success(text="", icon="✔"):  # icon="✅"
        return st.success(f"{icon} {text}")

    @staticmethod
    def warning(text="", icon="⚠️"):
        return st.warning(f"{icon} {text}")

    @staticmethod
    @st.cache_data(**CACHE_DATA)
    def cache_data(_func, *args, **kwargs):
        return _func(*args, **kwargs)

    @staticmethod
    @st.cache_data(**CACHE_TO_DISK)
    def cache_to_disk(_func, *args, **kwargs):
        return _func(*args, **kwargs)

    @staticmethod
    @st.cache_resource(**CACHE_RESOURCE)
    def cache_resource(_func, *args, **kwargs):
        return _func(*args, **kwargs)

    cache = cache_data
