from Str import Str
from unittest import TestCase


class TestStr(TestCase):
    def test_insert(self):
        self.fail()

    def test_append(self):
        data_string = "Hello world!"
        val = Str(data_string)
        complete = data_string + " one more time"
        val += " one more time"
        self.assertEqual(complete, str(val))

    def test_reverse(self):
        data_string = "Hello world!"
        val = Str(data_string)
        val.reverse()
        self.assertEqual(str(val), str(data_string[::-1]))

    def test_extend(self):
        self.fail()

    def test_pop(self):
        self.fail()

    def test_remove(self):
        self.fail()

    def test_improper_type(self):
        with self.assertRaises(TypeError):
            Str(["abc"])

    def test_iterator(self):
        data_string = "Hello world!"
        val = Str(data_string)
        for data_char, val_char in zip(data_string, val):
            self.assertEqual(data_char, val_char)

    def test_mutable(self):
        data = Str("Hello world!")

        def simple(d: Str):
            d[0] = "a"
            return d

        self.assertEqual(id(data), id(simple(data)))
        self.assertEqual(data[0], 'a')
