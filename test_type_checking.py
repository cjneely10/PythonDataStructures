from typing import Optional, Union, List
from unittest import TestCase
from type_checking import TypeChecker


class Test(TestCase):
    def test_check_types(self):

        @TypeChecker.check_types
        def simple(val5: int, val2: float, val3: Optional[str]):
            pass

        simple(1, 2.0, None)
        simple(1, 2.0, None)
        simple(1, 4.0, None)

        self.assertTrue(True)
