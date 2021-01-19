"""
Module holds class to parse data files into packaged struct for access
"""
import os
from pathlib import Path
from enum import Enum, auto
from collections import namedtuple
from typing import Iterator, Optional, List


class FileParser:
    """
    FileParser will open a file and act as an iterator over the file's contained data
    """
    class TokenParser:
        """
        Struct will parse line_pattern for tokens and maintain two stacks - one of expressions and one of separators
        """
        class Tokens(Enum):
            """
            Enum class holds supported token types for each line in file
            """
            EXP_START = "$"
            TYPE_START = ":"
            SEP = "|"
            SEP_INT = "'"

        __slots__ = ["tokens", "separators", "pos", "token_types"]
        # Results tuple type to return from each successful iteration
        Token = namedtuple("Token", ["token", "type"])

        def __init__(self, line_pattern: str):
            """
            Create empty tokens/separators stacks (stacks implemented as lists)
            """
            # Function to parse each specified supported token
            self.token_types = {
                FileParser.TokenParser.Tokens.EXP_START: (lambda _: _),
                FileParser.TokenParser.Tokens.TYPE_START: (lambda _: _),
                FileParser.TokenParser.Tokens.SEP: (lambda _: _),
                FileParser.TokenParser.Tokens.SEP_INT: (lambda _: _),
            }
            self.tokens: List[FileParser.TokenParser.Token] = []
            self.separators: List[str] = []
            self.pos = -1
            self._parse(line_pattern)

        def _parse(self, line_pattern: str):
            """ Per line pattern provided in FileParser.__init__, parse into tokens and separators

            :param line_pattern:
            """
            tokens = set(FileParser.TokenParser.token_types.keys())
            for i, char in enumerate(line_pattern):
                token_type = self.token_types.get(char)
            self.tokens.reverse()
            self.separators.reverse()

        def __iter__(self) -> Iterator:
            """ Parser will be iterable that returns parsed token tuples

            :return: Parser as iterator
            """
            self.pos = -1
            return self

        def __next__(self) -> "FileParser.TokenParser.Token":
            """ Get next expected token within line

            :raises: StopIteration at end of tokens list
            :return: Token tuple consisting of token name and type
            """
            self.pos += 1
            if len(self.tokens) == self.pos:
                raise StopIteration
            return self.tokens[self.pos]

    class Parsed:
        """
        Struct returned as iterator is consumed, consists of packaged line data using keys
        referenced in initial FileParser construction
        """
        __slots__ = ["_data"]

        def __init__(self):
            """
            Create empty stored data
            """
            self._data = {}

        def __getitem__(self, item: str) -> Optional[object]:
            """ Get value of item from line

            :param item: Initial name assigned to data at position in line in file
            :return: Parsed input data
            """
            return self._data.get(item, None)

        @property
        def data(self) -> dict:
            """ Get readable reference to internally stored data

            :return: Internal data parsed to proper types
            """
            return self._data

    def __init__(self, file: str, line_pattern: str, has_header: bool, sep="\t", comment: Optional[str] = "#",
                 raise_on_fail: bool = True):
        """ Create FileParser with specified file. Use the provided line_pattern to parse each line into proper types

        Examples:

        1.0,1,meow   ==>   $val:float|$val2:int|$val3:str (sep=",")

        remove_str-1   ==>   $val:str|$val2:int (sep="-")

        remove_str-1,remove_str-2   ==>   $val:str'-'$val2:int|$val3:str'-'$val4:int (sep=",", internal="-")

        1.0,2.0,...(a bunch of times)   ==>   $val:float|* (sep=",")

        The final line will generate val0-val(n-1) data accessors

        :param file: File to parse, must exist
        :param line_pattern: Pattern to use in parsing each line.
        :param has_header: Store header if found
        :param sep: Separator used across file (if a header line is present, must also be in header)
        :param comment: Character beginning line that signifies it as a comment
        :param raise_on_fail: If pattern fails to parse line, will throw error or continue based on value
        :raises: FileNotFoundError
        """
        file = str(Path(file).resolve())
        if not os.path.exists(file):
            raise FileNotFoundError
        self.comment_char = comment
        self.file_ptr = open(file, "r")
        self.sep_char = sep
        self.header: Optional[List[str]] = None
        if has_header:
            self.header = next(self.file_ptr).split(sep)
        self.comments = []
        self.raise_on_fail = raise_on_fail
        self.parser = FileParser.TokenParser(line_pattern)

    def __iter__(self) -> Iterator:
        """ Create iterator over file

        :return: Iterator
        """
        return self

    def __next__(self) -> "FileParser.Parsed":
        """ Get next parsed line in file

        :return: Line parsed into Parsed object
        """
        return self.Parsed()

    def __enter__(self):
        """ Context manager creation for ease in use

        :return: Iterator over self
        """
        return self.__iter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close context manager and stored file
        """
        self.file_ptr.close()
