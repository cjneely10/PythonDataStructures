"""
Module holds class functionality for mutable strings
"""
import copy
from typing import List, Union, Optional, Iterator, Callable


def handle_const(f: Callable):
    def fxn(self, *args, **kwargs):
        if self.const:
            raise AttributeError("Cannot modify a const string!")
        return f(self, *args, **kwargs)

    return fxn


class Str:
    """  Mutable string class, pass-by-reference internal data

    """
    ERR_STRING = "Input string must be python native `str` type or another `Str` object"

    def __init__(self, string: Optional[Union[str, "Str"]], const: bool = False):
        """ Create a Str object from a python str or another Str object
        :param string: Str/str object to use to create Str, default None
        """
        self._data: List[str] = []
        self._pos = 0
        if isinstance(string, (str, Str)):
            for char in string:
                self._data.append(char)
        else:
            raise TypeError(Str.ERR_STRING)
        self._const = const

    @property
    def const(self) -> bool:
        return self._const

    @handle_const
    def append(self, value: Union[str, "Str"]):
        """ Add str/Str contents to current string

        :param value: Contents to add
        """
        for char in value:
            self._data.append(char)

    @handle_const
    def reverse(self):
        """ Reverse contents of string

        """
        self._data.reverse()

    @handle_const
    def extend(self, value: Union[str, "Str"]):
        """ Add contents of str/Str to current string

        :param value: Contents to add
        """
        self.append(value)

    @handle_const
    def pop(self) -> str:
        """ Pop off and return last character in string

        :return: Last character in string after inner contents removed
        """
        return self._data.pop()

    @handle_const
    def remove(self, index: Union[int, slice]):
        """ Remove index/slice of string

        :param index: int/slice to remove from current string
        """
        del self._data[index]

    def __str__(self) -> str:
        """ Get Str as str

        :return: Contents as str
        """
        return "".join(self._data)

    def __repr__(self) -> str:
        """ Class representation of string for repl

        :return: Contents for REPL
        """
        return """<Str: '%s'>""" % str(self)

    def __len__(self) -> int:
        """ Length of string

        :return: Length as int
        """
        return len(self._data)

    @handle_const
    def __iadd__(self, other: Union[str, "Str"]) -> "Str":
        """ Add str/Str contents to current string

        :param other: Contents to add
        :return: self
        """
        self.append(other)
        return self

    @handle_const
    def __add__(self, other: Union[str, "Str"]) -> "Str":
        """ Add str/Str contents to current string

        :param other: Contents to add
        :return: self
        """
        self.append(other)
        return self

    def __getitem__(self, i: Union[int, slice]) -> str:
        """ Get data stored at position/slice

        :param i: position
        :return: Contents at index/slice
        """
        if isinstance(i, int):
            assert i < len(self._data)
            return self._data[i]
        if isinstance(i, slice):
            return "".join(self._data[i])
        raise TypeError(Str.ERR_STRING)

    @handle_const
    def __setitem__(self, i: int, string: Union[str, "Str"]):
        """ Set contents of string at position/slice

        Will extend size of container is `string` extends past current string boundary

        :param i: Position/slice to set
        :param string: Value to update using
        """
        assert i < len(self._data)
        pos = 0
        for j in range(min(len(string), len(self._data))):
            if j + i >= len(self._data):
                break
            self._data[j + i] = string[pos]
            pos += 1
        if pos < len(string):
            self.append(string[pos:])

    @handle_const
    def __delitem__(self, i: Union[int, slice]):
        """ Remove contents of string at position/slice

        :param i: Position/slice to remove
        """
        del self._data[i]

    def __iter__(self) -> Iterator:
        """ Iterate over current string

        :return: Iterator
        """
        self._pos = 0
        return self

    def __next__(self) -> str:
        """ Consume iterator to get next character in string

        Raises StopIteration error

        :return: Character in string
        """
        if self._pos < len(self._data):
            self._pos += 1
            return self._data[self._pos - 1]
        raise StopIteration

    def copy(self, const: bool = False) -> "Str":
        """ Create deep copy of current string and return

        :return: Deep copy of Str object
        """

        cp = copy.deepcopy(self)
        cp._const = const
        return cp
