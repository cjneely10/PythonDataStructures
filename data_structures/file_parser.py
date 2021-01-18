"""
Module holds class to parse data files into packaged struct for access
"""
from pathlib import Path
from typing import Iterator, Optional, List


class FileParser:
    """
    FileParser will open a file and act as an iterator over the file's contained data
    """
    class LineParser:
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
            return self._data[item]

    def __init__(self, file: str, line_pattern: str, has_header: bool, sep="\t", comment: Optional[str] = "#"):
        """

        :param file:
        :param line_pattern:
        :param has_header:
        :param sep:
        :param comment:
        """
        self.comment_char = comment
        self.file_ptr = open(str(Path(file).resolve()), "r")
        self.sep_char = sep
        self.header: Optional[List[str]] = None
        if has_header:
            self.header = next(self.file_ptr).split(sep)

    def __iter__(self) -> Iterator:
        """
        Create iterator over file
        """
        return self

    def __next__(self):
        """ Get next parsed line in file

        :return: Line parsed into LineParser object
        """
        return FileParser.LineParser()

    def __enter__(self):
        """ Context manager creation for ease in use

        :return: Iterator over self
        """
        return self.__iter__()

    def __exit__(self):
        """
        Close context manager and stored file
        """
        self.file_ptr.close()

    def _parse_line_pattern(self, line_pattern: str):
        pass
