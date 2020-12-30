from unittest import TestCase
from mutable_string import Str


class TestStr(TestCase):
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
        data_string = "Hello world!"
        val = Str(data_string)
        complete = data_string + " one more time"
        val.extend(" one more time")
        self.assertEqual(complete, str(val))

    def test_pop(self):
        data_string = "Hello world!"
        val = Str(data_string)
        self.assertEqual(data_string[-1], val.pop())
        self.assertEqual(len(val), len(data_string) - 1)

    def test_remove(self):
        data_string = "Hello world!"
        val = Str(data_string)
        val.remove(1)
        self.assertEqual(str(val), "Hllo world!")
        val.remove(slice(1, 3))
        self.assertEqual(str(val), "Ho world!")
        del val[0:3]
        self.assertEqual(str(val), "world!")

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
        self.assertEqual(str(data), "aello world!")

    def test_setitem(self):
        data = Str("Hello world!")
        data[4] = "meow"
        self.assertEqual("Hellmeowrld!", str(data))

    def test_setitem_end(self):
        data = Str("Hello world!")
        data[10] = "meow"
        self.assertEqual("Hello worlmeow", str(data))

    def test_delete(self):
        val = "Hello world!"
        data = Str(val)
        del data[1]
        self.assertEqual(str(data), val[0] + val[2:])
        self.assertEqual(len(data), len(val) - 1)

    def test_add(self):
        data = Str("Hello")
        new_data = data + " " + Str("world!")
        self.assertEqual("Hello world!", str(new_data))

    def test_get(self):
        data = Str("Hello")
        self.assertEqual(data[0], "H")
        self.assertEqual(data[1:3], "el")
        with self.assertRaises(TypeError):
            data["k"]

    def test_clone(self):
        data = Str("Hello")
        data_cpy = data.copy()
        self.assertNotEqual(id(data), id(data_cpy))
        self.assertEqual(str(data), str(data_cpy))

    def test_const_attribute(self):
        data = Str("Hello", const=True)
        with self.assertRaises(TypeError):
            data[0] = "a"
        data_cpy = data.copy()
        data_cpy[0] = "a"
        self.assertEqual(str(data_cpy), "aello")

    def test_insert(self):
        data = Str("Hello")
        data.insert(1, "xy")
        self.assertEqual("Hxyello", str(data))

    def test_split(self):
        data = Str("Hello world!")
        self.assertEqual(["Hello", "world!"], data.split(" "))

    def test_insert_slice(self):
        data = Str("Hello world!")
        data[3:3] = "one"
        self.assertEqual("Helonelo world!", str(data))

    def test_copy_constructor(self):
        data = Str("Hello world!")
        data2 = Str(data)
        self.assertNotEqual(id(data), id(data2))
