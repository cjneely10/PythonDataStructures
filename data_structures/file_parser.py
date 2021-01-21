"""
Module holds class to parse data files into packaged struct for access
"""
import os
from enum import Enum
from pathlib import Path
from typing import Iterator, Optional, List, Dict, Tuple


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

    class ParsedToken:
        """
        Struct holds token name assigned to data and the data type to which to parse the value
        """
        __slots__ = ["token_name", "token_type"]

        def __init__(self, token_name: str, token_type: type):
            """ Create struct with given name and type for conversion

            :param token_name: Name to pass to output dict
            :param token_type: Type to which to convert value
            """
            self.token_name: str = token_name
            self.token_type: type = token_type

        def __repr__(self) -> str:
            """ For REPL debug

            :return: String repr
            """
            return f"{self.token_name} {self.token_type}"

        def __eq__(self, other: "TokenParser.ParsedToken") -> bool:
            """ Comparison operator overload

            :param other: Other token to which to compare
            :return: Boolean if internals are the same
            """
            return self.token_name == other.token_name and self.token_type == other.token_type

    __slots__ = ["tokens", "separators"]

    def __init__(self, line_pattern: str, sep: str):
        """
        Create empty tokens/separators stacks (stacks implemented as lists)
        """
        # Store tokens and separators encountered, assumed to be in alternating orders
        self.tokens: List[TokenParser.ParsedToken] = []
        self.separators: List[str] = []
        # Parse line pattern or raise error if issue
        self._parse_line_pattern(line_pattern, sep)

    # TODO: Handle starred patterns
    def _parse_line_pattern(self, line_pattern: str, sep: str):
        """ Per line pattern provided in FileParser.__init__, parse into tokens and separators

        :param line_pattern:
        """
        i = 0
        while i < len(line_pattern):
            # Line pattern $expr:value|
            if line_pattern[i] == TokenParser.Token.EXP_START.value:
                # Gather name to assign to data
                i += 1
                name_start_pos = i
                while i < len(line_pattern) and line_pattern[i] != TokenParser.Token.TYPE_START.value:
                    i += 1
                name_end_pos = i
                i += 1
                # Gather type to assign
                type_start_pos = i
                while i < len(line_pattern) \
                        and line_pattern[i] not in (TokenParser.Token.SEP.value, TokenParser.Token.SEP_INT.value):
                    i += 1
                type_end_pos = i
                # Store position of separator character
                sep_val = i
                # Skip over added internal-separator character at end
                if i < len(line_pattern) and line_pattern[i] == TokenParser.Token.SEP_INT.value:
                    i += 1
                # Create parsed token and store in queue
                self.tokens.append(
                    TokenParser.ParsedToken(
                        line_pattern[name_start_pos: name_end_pos],
                        __builtins__[line_pattern[type_start_pos: type_end_pos]]
                    )
                )
                # Store separator character in queue
                if i < len(line_pattern):
                    if line_pattern[sep_val] == TokenParser.Token.SEP_INT.value:
                        self.separators.append(line_pattern[sep_val + 1])
                    else:
                        self.separators.append(sep)
            i += 1

    def parse(self, line: str) -> Dict[str, object]:
        """ Parse line using stored data from initially provided pattern

        :param line: Line of file to parse, including newline
        :return: Dictionary of parsed data using provided name and type
        """
        line = line.rstrip("\r\n")
        i = 0
        sep_pos = 0
        tokens_pos = 0
        out = {}
        while sep_pos < len(self.separators) and i < len(line):
            start_pos = i
            while i < len(line) and line[i] != self.separators[sep_pos]:
                i += 1
            if i < len(line):
                out[self.tokens[tokens_pos].token_name] = self.tokens[tokens_pos].token_type(line[start_pos: i])
                tokens_pos += 1
            sep_pos += 1
            i += 1
        out[self.tokens[tokens_pos].token_name] = self.tokens[tokens_pos].token_type(line[i:])
        return out

    @property
    def pattern(self) -> Tuple[List["TokenParser.ParsedToken"], List[str]]:
        """ Get token/separator pattern generated from initial line_pattern provided

        :return: List of tokens and separators
        """
        return self.tokens, self.separators


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
        # Confirm file exists
        file = str(Path(file).resolve())
        if not os.path.exists(file):
            raise FileNotFoundError
        # Store relevant parsing instructions
        self.comments = []
        self.comment_char = comment
        self.raise_on_fail = raise_on_fail
        self.sep_char = sep
        self.header: Optional[List[str]] = None
        # Open file and gather any comments
        self.file_ptr = open(file, "r")
        line = self._get_comments()
        # Gather header if requested
        if has_header:
            self.header = line.split(sep)
        # Generate parser from provided line_pattern
        self.parser = TokenParser(line_pattern, sep)

    def _get_comments(self):
        """
        Gather all comments until no longer have lines to read, or a non-comment line is encountered
        """
        line = next(self.file_ptr)
        while line and line.startswith(self.comment_char):
            self.comments.append(line)
            line = next(self.file_ptr)
        return line

    def __iter__(self) -> Iterator:
        """ Create iterator over file

        :return: Iterator
        """
        return self

    def __next__(self) -> "FileParser.Parsed":
        """ Get next parsed line in file

        :return: Line parsed into Parsed object
        """
        line = self._get_comments()
        return FileParser.Parsed(self.parser.parse(line))

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
