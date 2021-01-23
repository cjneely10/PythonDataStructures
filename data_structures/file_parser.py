"""
Module holds class to parse data files into packaged struct for access
"""
import os
from enum import Enum
from pathlib import Path
from collections import defaultdict
from collections.abc import Mapping
from typing import Iterator, Optional, List, Dict, Tuple, KeysView, ItemsView, ValuesView


class TokenParser:
    """
    Struct will parse line_pattern for tokens and maintain two stacks - one of expressions and one of separators
    """
    class ParsePatternFail(IOError):
        """
        Wrapper error class for when parsing a line pattern fails
        """

    class ParseLineFail(IOError):
        """
        Wrapper error class for when parsing a line of file data fails
        """

    class Token(Enum):
        """
        Enum class holds supported token types for each line in file
        """
        EXP_START = "$"
        TYPE_START = ":"
        SEP = "|"
        SEP_INT = "'"
        STARRED = "*"
        COMPLEX = "#"

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

        def __eq__(self, other: "TokenParser.ParsedToken") -> bool:
            """ Comparison operator overload

            :param other: Other token to which to compare
            :return: Boolean if internals are the same
            """
            return self.token_name == other.token_name and self.token_type == other.token_type

        def __ne__(self, other):
            """
            Wrapper for not __eq__
            """
            return not self.__eq__(other)

    __slots__ = ["tokens", "separators", "created_ids", "user_data_types"]

    def __init__(self, line_pattern: str, sep: str, data_types=None):
        """
        Create empty tokens/separators stacks (stacks implemented as lists)
        """
        # Store tokens and separators encountered, assumed to be in alternating orders
        self.tokens: List[TokenParser.ParsedToken] = []
        self.separators: List[str] = []
        self.created_ids = set()
        # Build dict of searchable user types passed in at API level
        self.user_data_types = ({val.__name__: val for val in data_types} if data_types is not None else {})
        # Include all builtin types
        self.user_data_types.update(__builtins__)
        # Parse line pattern or raise error if issue
        self._parse_line_pattern(line_pattern, sep)

    def _parse_line_pattern(self, line_pattern: str, sep: str):
        """ Per line pattern provided in FileParser.__init__, parse into tokens and separators

        :param line_pattern:
        """
        i = 0
        while i < len(line_pattern):
            self._parse_standard_token(line_pattern, i, sep)
            i += 1
        if not self.has_pattern():
            raise TokenParser.ParsePatternFail()

    def _parse_standard_token(self, line_pattern: str, i: int, sep: str):
        """ Parse line pattern $expr:value|

        :param line_pattern: Line pattern being parsed
        :param i: Position within line pattern
        :param sep: Global line separator
        """
        if line_pattern[i] == TokenParser.Token.EXP_START.value:
            # Move over EXP_START token
            i += 1
            # Gather name to assign to data
            name_start_pos = i
            while i < len(line_pattern) and line_pattern[i] != TokenParser.Token.TYPE_START.value:
                i += 1
            name_end_pos = i
            i += 1
            token_name = line_pattern[name_start_pos: name_end_pos]
            if token_name in self.created_ids:
                raise TokenParser.ParsePatternFail("Repeated id found in line_pattern")
            self.created_ids.add(token_name)
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
            # Try create parsed token and store in queue
            try:
                self.tokens.append(
                    TokenParser.ParsedToken(
                        line_pattern[name_start_pos: name_end_pos],
                        self.user_data_types[line_pattern[type_start_pos: type_end_pos]]
                    )
                )
            # Conversion type not found
            except KeyError as err:
                # Failed to locate proper type
                raise TokenParser.ParsePatternFail("Unable to parse type") from err
            # Store separator character in queue
            if i < len(line_pattern):
                if line_pattern[sep_val] == TokenParser.Token.SEP_INT.value:
                    self.separators.append(line_pattern[sep_val + 1])
                else:
                    self.separators.append(sep)

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
                self._try_parse(out, tokens_pos, line[start_pos: i])
                tokens_pos += 1
            sep_pos += 1
            i += 1
        self._try_parse(out, tokens_pos, line[i:])
        return out

    def _try_parse(self, out: dict, tokens_pos: int, line: str):
        """ Attempt to convert line in file to type in collected pattern

        :param out: Output data dict being built
        :param tokens_pos: Position of token for parsing
        :param line: Generated line substring to convert
        """
        try:
            out[self.tokens[tokens_pos].token_name] = self.tokens[tokens_pos].token_type(line)
        except ValueError as err:
            raise TokenParser.ParseLineFail("Improper data type found: " + line) from err

    @property
    def pattern(self) -> Tuple[List["TokenParser.ParsedToken"], List[str]]:
        """ Get token/separator pattern generated from initial line_pattern provided

        :return: List of tokens and separators
        """
        return self.tokens, self.separators

    def has_pattern(self) -> bool:
        """ Check for pattern successfully parsing after reading in line_pattern

        :return: Boolean for if pattern loaded successfully
        """
        return len(self.tokens) > 0


class FileParser:
    """
    FileParser will open a file and act as an iterator over the file's contained data
    """
    class Parsed(Mapping):
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

        def __iter__(self) -> Iterator:
            """ Create iterator over data

            :return: Internal data dict returned as iterator
            """
            return iter(self._data)

        def __len__(self) -> int:
            """ Length of parsed line data dict

            :return: Length of parsed line data
            """
            return len(self._data)

        def __getitem__(self, item: str) -> Optional[object]:
            """ Get value of item from line

            :param item: Initial name assigned to data at position in line in file
            :return: Parsed input data
            """
            return self._data.get(item, None)

        def keys(self) -> KeysView:
            """
            Wrapper .keys()
            """
            return self._data.keys()

        def values(self) -> ValuesView:
            """
            Wrapper .values()
            """
            return self._data.values()

        def items(self) -> ItemsView:
            """
            Wrapper .items()
            """
            return self._data.items()

    def __init__(self, file: str, line_pattern: str, has_header: bool = False, sep: str = "\t",
                 comment: Optional[str] = "#"):
        """ Create FileParser with specified file. Use the provided line_pattern to parse each line into proper types

        Examples:

        1.0,1,meow   ==>   $val:float|$val2:int|$val3:str (sep=",")

        remove_str-1   ==>   $val:str|$val2:int (sep="-")

        remove_str-1,remove_str-2   ==>   $val:str'-'$val2:int|$val3:str'-'$val4:int (sep=",", internal="-")

        1.0,2.0,...(a bunch of times)   ==>   $val:float|* (sep=",")

        The final line will generate val0-val(n-1) data accessors

        Mixture:

        1.0,2.0,3.0,4.0,1,2,3,4   ==>   $fval:float|#4|$ival:int|#4 (sep=",")

        :param file: File to parse, must exist
        :param line_pattern: Pattern to use in parsing each line.
        :param has_header: Store header if found
        :param sep: Separator used across file (if a header line is present, must also be in header)
        :param comment: Character beginning line that signifies it as a comment
        :raises: FileNotFoundError
        """
        # Confirm file exists
        file = str(Path(file).resolve())
        if not os.path.exists(file):
            raise FileNotFoundError
        # Store relevant parsing instructions
        self._comments = []
        self._comment_char = comment
        self._sep_char = sep
        self._header: Optional[List[str]] = None
        # Open file and gather any comments
        self._file = file
        # Gather header if requested
        if has_header:
            self._file = open(file, "r")
            self._header = next(self._file).rstrip("\r\n").split(sep)
        # Generate parser from provided line_pattern
        self._parser = TokenParser(line_pattern, sep)
        self._size = 0

    def _get_comments(self):
        """
        Gather all comments until no longer have lines to read, or a non-comment line is encountered
        """
        if isinstance(self._file, str):
            self._file = open(self._file, "r")
        line = next(self._file).rstrip("\r\n")
        while line and (self._comment_char is not None and line.startswith(self._comment_char)):
            self._comments.append(line)
            line = next(self._file).rstrip("\r\n")
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
        self._size += 1
        return FileParser.Parsed(self._parser.parse(line))

    def collect(self) -> Dict[str, list]:
        """ Read through entire file and gather contents into dictionary

        :return: Collected data from input file
        """
        out = defaultdict(list)
        for data in self:
            for key, value in data.items():
                out[key].append(value)
        return dict(out)

    @property
    def comments(self) -> List[str]:
        """ Get list of all comment lines found

        :return: List of all comment lines found
        """
        return self._comments

    @property
    def header(self) -> List[str]:
        """ Get header values split by initial separator

        :return: List of header values
        """
        return self._header

    def __len__(self) -> int:
        """ Get number of data lines encountered by parser

        :return: Number of data lines in original file
        """
        return self._size
