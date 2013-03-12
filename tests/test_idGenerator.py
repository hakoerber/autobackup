import unittest
import idGenerator

class TestSequenceFunctions(unittest.TestCase):
    
    def test_length(self):
        self.assertTrue(len(idGenerator.generate_id(20)) == 20)


    def test_charset(self):
        self.assertTrue('a' in idGenerator.generate_id(1,"a"))
        id = idGenerator.generate_id(3,"xyz")
        self.assertTrue('x' in id or 'y' in id or 'z' in id and
                        len(id) == 3)

