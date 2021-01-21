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

    def test_parse_line_with_internal_sep(self):
        parser = TokenParser("$val:str'-$value:float|$val2:str'-$value2:float", "\t")

        self.assertEqual(
            {"val": "sep", "value": 1.0, "val2": "sep", "value2": 2.0},
            parser.parse("sep-1.0\tsep-2.0")
        )
