import random
from unittest import TestCase
from data_structures.type_checking import TypeChecker
from data_structures.parallel_iter import iter_async, iter_threaded


class Test(TestCase):
    def test_parallelize(self):

        @iter_async(start_pos=(10, 20, 30, 40), end_pos=(100, 110, 120, 130))
        async def out(start_pos: int, end_pos: int):
            threshold = random.randint(1000, 10000)
            rand_val = random.randint(1, 10000)
            while rand_val < threshold:
                rand_val = random.randint(1, 10000)
            return start_pos, end_pos

        self.assertTrue([(10, 100), (20, 110), (30, 120), (40, 130)], out())

    def test_improper_args(self):

        with self.assertRaises(AttributeError):

            @iter_async(start_pos=(10, 20, 30), end_pos=(100, 110, 120, 130))
            async def out(start_pos: int, end_pos: int):
                pass

            out()

    def test_threading(self):

        @iter_threaded(3, start_pos=(10, 20, 30, 40), end_pos=(100, 110, 120, 130))
        @TypeChecker()
        def out(start_pos: int, end_pos: int):
            threshold = random.randint(1000, 10000)
            rand_val = random.randint(1, 10000)
            while rand_val < threshold:
                rand_val = random.randint(1, 10000)
            return start_pos, end_pos

        self.assertEqual([(10, 100), (20, 110), (30, 120), (40, 130)], list(out()))

    def test_malformed_threading(self):

        with self.assertRaises(TypeError):

            @iter_threaded(-1)
            def out(start_pos: int, end_pos: int):
                pass

            out()

    def test_filter_output(self):

        @iter_threaded(3, ignore_types=(ArithmeticError,), value=[1, 2, 3])
        def issue(value: int):
            if value == 2:
                raise ArithmeticError
            return value

        self.assertEqual([1, 3], list(issue()))

    def test_raises_error(self):

        with self.assertRaises(ArithmeticError):
            @iter_threaded(3, value=[1, 2, 3])
            def issue(value: int):
                if value == 2:
                    raise ArithmeticError
                return value

            list(issue())

    def test_ignore_type(self):

        @iter_threaded(3, ignore_types=(None, str), value=[1, 2, 3])
        def issue(value: int):
            if value == 2:
                return None
            if value == 3:
                return ""
            return value

        self.assertEqual([1], list(issue()))
