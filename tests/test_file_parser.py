from unittest import TestCase
from data_structures.file_parser import TokenParser


class TestTokenParser(TestCase):
    def test_parse_line_pattern(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str", "\t")

        self.assertEqual(
            (
                [
                    TokenParser.ParsedToken("val", float),
                    TokenParser.ParsedToken("val2", int),
                    TokenParser.ParsedToken("val3", str)
                ],
                ["\t", "\t"]
            ),
            parser.pattern
        )

    def test_parse_line_to_pattern(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str", "\t")

        self.assertEqual(
            {"val": 1.0, "val2": 2, "val3": "3"},
            parser.parse("1.0\t2\t3")
        )
