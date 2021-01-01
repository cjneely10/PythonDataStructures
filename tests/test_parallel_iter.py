import random
from unittest import TestCase
from data_structures.parallel_iter import parallelize


class Test(TestCase):
    def test_parallelize(self):

        async def monte_carlo():
            threshold = random.randint(1000, 10000)
            rand_val = random.randint(1, 10000)
            while rand_val < threshold:
                rand_val = random.randint(1, 10000)
            return rand_val

        @parallelize({"start_pos": [10, 20, 30, 40], "end_pos": [100, 110, 120, 130]})
        async def out(start_pos: int, end_pos: int):
            print("searching", start_pos, end_pos)
            x = await monte_carlo()
            print("done", start_pos, end_pos, x)

        out()
        self.assertTrue(True)
