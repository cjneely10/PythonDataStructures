from unittest import TestCase
from data_structures.file_parser import TokenParser


class TestTokenParser(TestCase):
    def test_parse_line_pattern(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str")

        self.assertEqual(
            (
                [
                    TokenParser.ParsedToken("val", float),
                    TokenParser.ParsedToken("val2", int),
                    TokenParser.ParsedToken("val3", str)
                ],
                ["|", "|"]
            ),
            parser.pattern
        )
