"""
Module holds class functionality for mutable strings
"""
import copy
from typing import List, Union, Iterator, Callable, Type
from type_checking import TypeChecker


def handle_const(func: Callable):
    """ Decorator checks if Str object is non-const reference

    :param func: Str method to call
    :return: Wrapped method that has first checked if Str is mutable
    """
    def fxn(self, *args, **kwargs):
        if self.const:
            raise TypeError("'Str' const object cannot be modified")
        return func(self, *args, **kwargs)

    return fxn


def check_types(value: object, types: List[Type]):
    """ Simple type checking function against list of possible types

    :param value: Object to check
    :param types: List of acceptable types
    :return:
    """
    if not isinstance(value, tuple(types)):
        raise TypeError("Data <{}> must be of type {}".format(value, " or ".join(list(map(str, types)))))


class Str:
    """ Mutable string class, pass-by-reference internal data

    Pass by "const reference" ensures that inner data is not mutated, but does no further
    optimization than the standard Python pass-by-reference

    Constructor inherently is deep copy-constructor

    """
    ERR_STRING = "Input string must be python native `str` type or another `Str` object"

    @TypeChecker.check_types
    def __init__(self, string: Union[str, "Str"], const: bool = False):
        """ Create a Str object from a python str or another Str object
        :param string: Str/str object to use to create Str, default None
        """
        if isinstance(string, (str, Str)):
            self._data: List[str] = []
            self._pos = 0
            for char in string:
                self._data.append(char)
            self._const = const
        else:
            raise TypeError(Str.ERR_STRING)

    @property
    def const(self) -> bool:
        """ Check if Str is const or non-const reference

        :return: bool of const status
        """
        return self._const

    @handle_const
    @TypeChecker.check_types
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
    @TypeChecker.check_types
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
    @TypeChecker.check_types
    def remove(self, index: Union[int, slice]):
        """ Remove index/slice of string

        :param index: int/slice to remove from current string
        """
        del self._data[index]

    @TypeChecker.check_types
    def copy(self, const: bool = False) -> "Str":
        """ Create deep copy of current string and returns new Str object
        Assigns const status to newly created string

        :return: Deep copy of Str object
        """
        prior = self._const
        self._const = const
        data_copy = copy.deepcopy(self)
        self._const = prior
        return data_copy

    @handle_const
    @TypeChecker.check_types
    def insert(self, i: int, string: Union[str, "Str"]):
        """ Insert string contents at position. Does not support negative indexing

        :param i: Position to insert at, must be less than current size and >= 0
        :param string: str/Str to insert
        :return:
        """
        assert 0 <= i < len(self._data)
        original_pos = len(self._data) - 1
        # Make space for new string
        for _ in range(len(string)):
            self._data.append("")
        # Copy over contents from original string to make space
        new_string_pos = len(self._data) - 1
        while original_pos >= i:
            tmp = self._data[original_pos]
            self._data[new_string_pos] = tmp
            new_string_pos -= 1
            original_pos -= 1
        # Insert new contents
        for char in string:
            self._data[i] = char
            i += 1

    def split(self, *args, **kwargs) -> List[str]:
        """ Split contents into python's str type

        :param args: str.split() args
        :param kwargs: str.split() kwargs
        :return: List of split strings
        """
        return str(self).split(*args, **kwargs)

    def set_const(self):
        """ Sets const status of owned object to True

        """
        self._const = True

    def format(self, *args, **kwargs) -> "Str":
        """ Mimic str class format function

        :param args: kwargs to format
        :param kwargs: kwargs to format
        :return: Formatted Str object
        """
        return Str("".join(self._data).format(*args, **kwargs))

    def __str__(self) -> str:
        """ Get Str as str

        :return: Contents as str
        """
        return "".join(self._data)

    def __repr__(self) -> str:
        """ Class representation of string for repl

        :return: Contents for REPL
        """
        return "".join(self._data)

    def __len__(self) -> int:
        """ Length of string

        :return: Length as int
        """
        return len(self._data)

    @handle_const
    @TypeChecker.check_types
    def __iadd__(self, other: Union[str, "Str"]) -> "Str":
        """ Add str/Str contents to current string

        :param other: Contents to add
        :return: self
        """
        self.append(other)
        return self

    @handle_const
    @TypeChecker.check_types
    def __add__(self, other: Union[str, "Str"]) -> "Str":
        """ Add str/Str contents to current string

        :param other: Contents to add
        :return: self
        """
        out = Str(self)
        out.append(other)
        return out

    @TypeChecker.check_types
    def __getitem__(self, i: Union[int, slice]) -> str:
        """ Get data stored at position/slice

        :param i: position
        :return: Contents at index/slice
        """
        return "".join(self._data[i])

    @handle_const
    @TypeChecker.check_types
    def __setitem__(self, i: Union[int, slice], string: Union[str, "Str"]):
        """ Set contents of string at position/slice

        Will extend size of container is `string` extends past current string boundary

        :param i: Position/slice to set, 0 : len(self)
        :param string: Value to update using
        """
        if isinstance(i, slice):
            self._data[i] = string.split()
            return
        assert 0 <= i < len(self._data)
        pos = 0
        for j in range(min(len(string), len(self._data))):
            if j + i >= len(self._data):
                break
            self._data[j + i] = string[pos]
            pos += 1
        if pos < len(string):
            self.append(string[pos:])

    @handle_const
    @TypeChecker.check_types
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

    @TypeChecker.check_types
    def __eq__(self, other: Union[str, "Str"]) -> bool:
        """ Compares if two Str objects contain the same data

        :param other: Other Str
        :return: Comparison if contents are identical
        """
        if len(self) != len(other):
            return False
        for char_i, char_j in zip(self, other):
            if char_i != char_j:
                return False
        return True

    @TypeChecker.check_types
    def __ne__(self, other: Union[str, "Str"]) -> bool:
        """ Compares if two Str objects don't contain the same data

        :param other: Other Str/str
        :return: Comparison if contents are not identical
        """
        return not self.__eq__(other)

    @TypeChecker.check_types
    def __lt__(self, other: Union[str, "Str"]) -> bool:
        """ Compare strings for lexicographically smaller value

        :param other: Other Str/str to compare
        :return: Comparison if self is less than other
        """
        if len(self) < len(other):
            return True
        elif len(self) >= len(other):
            return False
        for char_i, char_j in zip(self, other):
            if char_i != char_j:
                if char_i < char_j:
                    return True
                else:
                    return False
        return False

    def __hash__(self) -> id:
        """ Provide hash overload

        :return: Hashed Str object
        """
        return hash("".join(self._data))
