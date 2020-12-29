"""
Module holds class functionality for mutable strings
"""

from typing import List, Union, Optional


class Str:
    """

    """
    ERR_STRING = "Input string must be python native `str` type or another `Str` object"

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
            raise TypeError(Str.ERR_STRING)

    def append(self, value: Union[str, "Str"]):
        for char in value:
            self._data.append(char)

    def reverse(self):
        self._data.reverse()

    def extend(self, value: Union[str, "Str"]):
        if isinstance(value, str):
            self._data.extend(list(value))
        else:
            self.append(value)

    def pop(self) -> str:
        return self._data.pop()

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
        return self

    def __getitem__(self, i: int) -> str:
        assert i < len(self._data)
        return self._data[i]

    def __setitem__(self, i: int, string: Union[str, "Str"]):
        assert i < len(self._data)
        pos = 0
        for j in range(min(len(string), len(self._data))):
            if j + i >= len(self._data):
                break
            self._data[j + i] = string[pos]
            pos += 1
        if pos < len(string):
            self.append(string[pos:])

    def __delitem__(self, i: Union[int, slice]):
        assert i < len(self._data)
        del self._data[i]

    def __iter__(self):
        self._pos = 0
        return self

    def __next__(self):
        if self._pos < len(self._data):
            self._pos += 1
            return self._data[self._pos - 1]
        raise StopIteration
