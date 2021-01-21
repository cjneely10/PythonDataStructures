from unittest import TestCase
from data_structures.file_parser import TokenParser


class TestTokenParser(TestCase):
    def test_parse_proper_line_pattern(self):
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

    def test_parse_line_pattern_missing_sep_end(self):
        parser = TokenParser("$val:float", "\t")

        self.assertEqual(
            (
                [TokenParser.ParsedToken("val", float)],
                []
            ),
            parser.pattern
        )

    def test_parse_improper_line_pattern_missing_exp_start(self):

        with self.assertRaises(TokenParser.ParserFail):
            TokenParser("val:float", "\t")

    def test_parse_improper_line_pattern_missing_type_start(self):
        self.fail()

    def test_parse_improper_line_pattern_invalid_type_signatures(self):
        self.fail()

    def test_parse_improper_line_pattern_repeated_exp_names(self):
        self.fail()

    def test_parse_proper_line(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str", "\t")

        self.assertEqual(
            {"val": 1.0, "val2": 2, "val3": "3"},
            parser.parse("1.0\t2\t3")
        )

    # # All improper line tests assume a correctly-parsed line_pattern

    def test_parse_improper_line_type_mismatch(self):
        self.fail()

    def test_parse_improper_line_length(self):
        self.fail()

    def test_parse_improper_line_wrong_sep(self):
        self.fail()

    def test_parse_improper_line_missing_sep_int(self):
        self.fail()

    def test_parse_improper_line_wrong_sep_int(self):
        self.fail()

    def test_parse_proper_line_with_internal_sep(self):
        parser = TokenParser("$val:str'-$value:float|$val2:str'-$value2:float", "\t")

        self.assertEqual(
            {"val": "sep", "value": 1.0, "val2": "sep", "value2": 2.0},
            parser.parse("sep-1.0\tsep-2.0")
        )
