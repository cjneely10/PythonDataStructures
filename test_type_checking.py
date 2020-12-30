from typing import Optional
from unittest import TestCase
from type_checking import TypeChecker
from mutable_string import Str


class Test(TestCase):
    def test_check_proper_types(self):
        @TypeChecker.check_types
        def simple(val5: int, val2: float, val3: Optional[str]):
            pass

        simple(1, 2.0, None)
        simple(1, 2.0, None)
        simple(1, 4.0, None)

        self.assertTrue(True)

    def test_check_improper_types(self):
        @TypeChecker.check_types
        def simple(val: int, val2: float, val3: str):
            pass

        with self.assertRaises(TypeError):
            simple("one", 2.0, 3)

    def test_user_class(self):
        @TypeChecker.check_types
        def simple(val: Str):
            pass

        simple(Str("val"))

        self.assertTrue(True)
