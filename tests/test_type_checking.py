from typing import Optional, Union
from unittest import TestCase
from type_checking import TypeChecker
from mutable_string import Str


class Test(TestCase):
    def test_check_proper_types(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val5: int, val2: float, val3: Optional[str]):
            pass

        simple(1, 2.0, None)
        simple(1, 2.0, None)
        simple(1, 4.0, None)

        self.assertTrue(True)

    def test_check_improper_types(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: int, val2: float, val3: str):
            pass

        with self.assertRaises(TypeError):
            simple("one", 2.0, 3)

    def test_user_class(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Str):
            pass

        simple(Str("val"))

        self.assertTrue(True)

    def test_union(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Union[str, Str]):
            pass

        with self.assertRaises(TypeError):
            simple([Str("val")])

    def test_bad_return(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Union[str, Str]) -> str:
            return int(val)

        with self.assertRaises(TypeError):
            simple("1")

    def test_good_return(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Union[str, Str]) -> str:
            return val

        simple("1")
        self.assertTrue(True)

    def test_return_union(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Union[str, Str]) -> Optional[str]:
            return val

        simple("1")
        self.assertTrue(True)

    def test_return_bad_union(self):
        checker = TypeChecker()

        @checker.check_types
        def simple(val: Union[str, Str]) -> Union[str, float]:
            return int(val)

        with self.assertRaises(TypeError):
            simple("1")