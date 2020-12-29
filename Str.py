"""
Module holds class functionality for mutable strings
"""

from typing import List, Union, Optional


class Str:
    """

    """
    def __init__(self, string: Optional[Union[str, "Str"]]):
        """ Create a Str object from a python str or another Str object
        :param string: Str/str object to use to create Str, default None
        """
        self._data: List[str] = []
        self._pos = 0
        if isinstance(string, str) or isinstance(string, Str):
            for char in string:
                self._data.append(char)
        else:
            raise ValueError("Input string must be python native `str` type or another `Str` object")

    def insert(self, index: Union[int, slice], value: str) -> None:
        assert index < len(self._data)
        self._data[index] = value.split()

    def append(self, value: Union[str, "Str"]):
        for char in value:
            self._data.append(char)

    def reverse(self):
        self._data.reverse()

    def extend(self, value: Union[str, "Str"]):
        self._data.extend(value.split())

    def pop(self):
        self._data.pop()

    def remove(self, index: Union[int, slice]):
        del self._data[index]

    def __str__(self) -> str:
        return "".join(self._data)

    def __repr__(self):
        return str(self)

    def __len__(self) -> int:
        """ Length of string

        :return: Length as int
        """
        return len(self._data)

    def __iadd__(self, other: Union[str, "Str"]):
        self.append(other)
        return self

    def __add__(self, other: Union[str, "Str"]):
        self.append(other)

    def __getitem__(self, i: int) -> str:
        assert i < len(self._data)
        return self._data[i]

    def __setitem__(self, i: Union[int, slice], string: str):
        assert i < len(self._data)
        self._data[i] = string.split()

    def __delitem__(self, i: Union[int, slice]):
        assert i < len(self._data)
        del self._data[i]

    def __iter__(self):
        return self

    def __next__(self):
        self._pos += 1
        if self._pos < len(self._data):
            return self._data[self._pos]
        self._pos = 0
        raise StopIteration
