import unittest
import device
import host

class TestCases(unittest.TestCase):
    
    def setUp(self):
        self.dev = device.Device(host.Host(hostname="localhost"), "U123-U456-I789-D012", "ext4")

    def test_device_file_path(self):
        self.assertRegexpMatches(self.dev.get_device_file_path(), '(/.*?)+')
