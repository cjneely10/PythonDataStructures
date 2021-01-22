import tempfile
from unittest import TestCase
from data_structures.file_parser import TokenParser, FileParser


class TestTokenParser(TestCase):
    def test_parse_proper_pattern(self):
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

    def test_parse_proper_pattern_starred(self):
        self.fail()

    def test_parse_proper_pattern_complex(self):
        self.fail()

    def test_parse_proper_pattern_missing_sep_end(self):
        parser = TokenParser("$val:float", "\t")
        self.assertEqual(
            (
                [TokenParser.ParsedToken("val", float)],
                []
            ),
            parser.pattern
        )

    def test_parse_proper_user_type(self):
        class Str:
            def __init__(self, value):
                self.value = value

        parser = TokenParser("$val:Str", "\t", [Str])
        self.assertEqual(
            (
                [TokenParser.ParsedToken("val", Str)],
                []
            ),
            parser.pattern
        )

    def test_parse_improper_pattern_missing_exp_start(self):
        with self.assertRaises(TokenParser.ParsePatternFail):
            TokenParser("val:float", "\t")

    def test_parse_improper_pattern_missing_type_start(self):
        with self.assertRaises(TokenParser.ParsePatternFail):
            TokenParser("$valfloat", "\t")

    def test_parse_improper_pattern_invalid_type_signatures(self):
        with self.assertRaises(TokenParser.ParsePatternFail):
            TokenParser("$val:vroom", "\t")

    def test_parse_improper_pattern_invalid_sep_int(self):
        with self.assertRaises(TokenParser.ParsePatternFail):
            TokenParser("$val:int`_|$val2:int", "\t")

    def test_parse_improper_pattern_repeated_exp_names(self):
        with self.assertRaises(TokenParser.ParsePatternFail):
            TokenParser("$val:int|$val:float", "\t")

    def test_parse_proper_line(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str", "\t")
        self.assertEqual(
            {"val": 1.0, "val2": 2, "val3": "3"},
            parser.parse("1.0\t2\t3")
        )

    # # All line tests assume a correctly-parsed line_pattern

    def test_parse_proper_line_with_internal_sep(self):
        parser = TokenParser("$val:str'-$value:float|$val2:str'-$value2:float", "\t")
        self.assertEqual(
            {"val": "sep", "value": 1.0, "val2": "sep", "value2": 2.0},
            parser.parse("sep-1.0\tsep-2.0")
        )

    def test_parse_proper_line_starred(self):
        self.fail()

    def test_parse_proper_line_complex(self):
        self.fail()

    def test_parse_improper_line_type_mismatch(self):
        parser = TokenParser("$val:float|$val2:int|$val3:str", "\t")
        with self.assertRaises(TokenParser.ParseLineFail):
            parser.parse("1.0\t1.0\t1.0")

    def test_parse_improper_line_length(self):
        parser = TokenParser("$val:float|$val2:int", "\t")
        with self.assertRaises(TokenParser.ParseLineFail):
            parser.parse("1.0\t1.0\t1.0")

    def test_parse_improper_line_wrong_sep(self):
        parser = TokenParser("$val:float|$val2:int", "\t")
        with self.assertRaises(TokenParser.ParseLineFail):
            parser.parse("1.0,1.0,1.0")

    def test_parse_improper_line_missing_sep_int(self):
        parser = TokenParser("$val:str'-$value:float|$val2:str'-$value2:float", "\t")
        with self.assertRaises(TokenParser.ParseLineFail):
            parser.parse("sep1.0\tsep-2.0")

    def test_parse_improper_line_wrong_sep_int(self):
        parser = TokenParser("$val:str'-$value:float|$val2:str'-$value2:float", "\t")
        with self.assertRaises(TokenParser.ParseLineFail):
            parser.parse("sep_1.0\tsep-2.0")

    def test_read_file_simple(self):
        with tempfile.NamedTemporaryFile("w") as file:
            file.write("1,2,3,4,5\n6,7,8,9,10")
            file.flush()

            reader = FileParser(file.name, "$a:int|$b:int|$c:int|$d:int|$e:int", False, ",")
            self.assertEqual(1, next(reader)["a"])
            self.assertEqual(6, next(reader)["a"])
            file.close()

    def test_read_file_with_header(self):
        with tempfile.NamedTemporaryFile("w") as file:
            file.write("one,two,three,four,five\n1,2,3,4,5\n# comments line\n6,7,8,9,10")
            file.flush()

            reader = FileParser(file.name, "$a:int|$b:int|$c:int|$d:int|$e:int", True, ",")
            self.assertEqual(1, next(reader)["a"])
            self.assertEqual(6, next(reader)["a"])
            file.close()

    def test_collect(self):
        with tempfile.NamedTemporaryFile("w") as file:
            file.write("one,two,three,four,five\n1,2,3,4,5\n# comments line\n6,7,8,9,10")
            file.flush()

            reader = FileParser(file.name, "$a:int|$b:int|$c:int|$d:int|$e:int", True, ",")
            self.assertEqual(
                {"a": [1, 6], "b": [2, 7], "c": [3, 8], "d": [4, 9], "e": [5, 10],},
                reader.collect()
            )
            file.close()
