from typing import Optional, Union
from unittest import TestCase
from mutable_string import Str
from type_checking import TypeChecker


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

    def test_union(self):

        @TypeChecker.check_types
        def simple(val: Union[str, Str]):
            pass

        with self.assertRaises(TypeError):
            simple([Str("val")])

    def test_bad_return(self):

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> str:
            return int(val)

        with self.assertRaises(TypeError):
            simple("1")

    def test_good_return(self):

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> str:
            return val

        simple("1")
        self.assertTrue(True)

    def test_return_union(self):

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> Optional[str]:
            return val

        simple("1")
        self.assertTrue(True)

    def test_return_bad_union(self):

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> Union[str, float]:
            return int(val)

        with self.assertRaises(TypeError):
            simple("1")

    def test_cache(self):
        TypeChecker.clear_cache()

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> Union[str, int]:
            if isinstance(val, Str):
                return int(str(val))
            return int(val)

        simple("1")
        simple(Str("1"))
        simple("2")
        simple(Str("2"))

        self.assertEqual(2, TypeChecker.current_cache_size())

    def test_cache_rollover(self):
        TypeChecker.clear_cache()

        @TypeChecker.check_types
        def simple(val: Union[str, Str]) -> Union[str, int]:
            if isinstance(val, Str):
                return int(str(val))
            return int(val)

        for _ in range(256):
            simple("1")

        self.assertEqual(1, TypeChecker.current_cache_size())
