"""
Module holds class to parse data files into packaged struct for access
"""
import os
from enum import Enum
from pathlib import Path
from collections import namedtuple
from typing import Iterator, Optional, List, Generator


class TokenParser:
    """
    Struct will parse line_pattern for tokens and maintain two stacks - one of expressions and one of separators
    """

    class Token(Enum):
        """
        Enum class holds supported token types for each line in file
        """
        EXP_START = "$"
        TYPE_START = ":"
        SEP = "|"
        SEP_INT = "'"

    # Results tuple type to return from each successful iteration
    ParsedToken = namedtuple("Token", ["token", "type"])

    __slots__ = ["tokens", "separators", "pos", "token_types"]

    def __init__(self, line_pattern: str):
        """
        Create empty tokens/separators stacks (stacks implemented as lists)
        """
        # Function to parse each specified supported token
        self.token_types = {
            TokenParser.Token.EXP_START: (lambda i: _),
            TokenParser.Token.TYPE_START: (lambda i: _),
            TokenParser.Token.SEP: (lambda i: _),
            TokenParser.Token.SEP_INT: (lambda i: _),
        }
        self.tokens: List[TokenParser.ParsedToken] = []
        self.separators: List[str] = []
        self.pos = -1
        self._parse_line_pattern(line_pattern)

    def _parse_line_pattern(self, line_pattern: str):
        """ Per line pattern provided in FileParser.__init__, parse into tokens and separators

        :param line_pattern:
        """
        token_as_strings = {token.value for token in TokenParser.Token}
        tokens_dict = {token.value: token for token in TokenParser.Token}
        start_pos = {"i": 0}
        for char in line_pattern:
            if char in token_as_strings:
                token_parsing_function = self.token_types.get(TokenParser.Token(tokens_dict[char]), None)
                if token_parsing_function is not None:
                    token_parsing_function(start_pos)

            start_pos["i"] += 1

        # Reverse results for iteration
        self.tokens.reverse()
        self.separators.reverse()

    def __iter__(self) -> Iterator:
        """ Parser will be iterable that returns parsed token tuples

        :return: Parser as iterator
        """
        self.pos = -1
        return self

    def __next__(self) -> "TokenParser.ParsedToken":
        """ Get next expected token within line

        :raises: StopIteration at end of tokens list
        :return: Token tuple consisting of token name and type
        """
        self.pos += 1
        if len(self.tokens) == self.pos:
            raise StopIteration
        return self.tokens[self.pos]

    def parse(self, line: str) -> Generator:
        pass


class FileParser:
    """
    FileParser will open a file and act as an iterator over the file's contained data
    """
    class Parsed:
        """
        Struct returned as iterator is consumed, consists of packaged line data using keys
        referenced in initial FileParser construction
        """
        __slots__ = ["_data"]

        def __init__(self, data: dict):
            """
            Create object using data dict, assumed at this point to be properly parsed to expected types
            """
            self._data = data

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
        self.parser = TokenParser(line_pattern)

    def __iter__(self) -> Iterator:
        """ Create iterator over file

        :return: Iterator
        """
        return self

    def __next__(self) -> "FileParser.Parsed":
        """ Get next parsed line in file

        :return: Line parsed into Parsed object
        """
        line = next(self.file_ptr)
        if line.startswith(self.comment_char):
            self.comments.append(line)
        else:
            return FileParser.Parsed({val_name: value for val_name, value in self.parser.parse()})

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
