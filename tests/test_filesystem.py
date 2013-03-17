import unittest
import filesystem
import host
import getpass

class TestCases(unittest.TestCase):
    
    def setUp(self):
        self.dev = filesystem.Device(host.Host(hostname="localhost"),
                                     "U123-U456-I789-D012", "ext4",
                                     getpass.getuser())

    def test_device_file_path(self):
        self.assertRegexpMatches(self.dev.get_device_file_path(), '(/.*?)+')
