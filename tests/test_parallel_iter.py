import random
from unittest import TestCase
from data_structures.parallel_iter import parallelize
from data_structures.type_checking import TypeChecker


class Test(TestCase):
    def test_parallelize(self):

        @parallelize({"start_pos": [10, 20, 30, 40], "end_pos": [100, 110, 120, 130]})
        @TypeChecker.check_types
        async def out(start_pos: int, end_pos: int):
            threshold = random.randint(1000, 10000)
            rand_val = random.randint(1, 10000)
            while rand_val < threshold:
                rand_val = random.randint(1, 10000)
            return start_pos, end_pos

        self.assertTrue([(10, 100), (20, 110), (30, 120), (40, 130)], out())

    def test_improper_args(self):

        with self.assertRaises(AttributeError):

            @parallelize({"start_pos": [20, 30, 40], "end_pos": [100, 110, 120, 130]})
            @TypeChecker.check_types
            async def out(start_pos: int, end_pos: int):
                pass

            out()

    def test_no_parallelize_options(self):

        with self.assertRaises(AttributeError):

            @parallelize({})
            @TypeChecker.check_types
            async def out(start_pos: int, end_pos: int):
                pass

            out()

    def test_improper_input(self):

        with self.assertRaises(AttributeError):

            @parallelize("")
            @TypeChecker.check_types
            async def out(start_pos: int, end_pos: int):
                pass

            out()
