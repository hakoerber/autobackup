import unittest
from host import Host

class TestCases(unittest.TestCase):
    def setUp(self):
        self.localhost_ip        = Host(ip="127.54.78.124")
        self.localhost_hostname  = Host(hostname="localhost")
        self.remotehost_ip       = Host(ip="192.0.0.1")
        self.remotehost_hostname = Host(hostname="www.google.com")

    def test_unknown_hostname(self):
        self.assertRaises(ValueError, Host, hostname="unknownhostname")
        
    def test_wrong_args(self):
        #self.assertRaises(ValueError, Host, ip=None, hostname=None)
        with self.assertRaises(ValueError):
            Host(ip=None, hostname=None)
        
    def test_localhost(self):
        self.assertTrue(self.localhost_ip.is_localhost())
        self.assertTrue(self.localhost_hostname.is_localhost())

    def test_remote_hosts(self):
        self.assertFalse(self.remotehost_ip.is_localhost())
        self.assertFalse(self.remotehost_hostname.is_localhost())

    def test_localhost_equality(self):
        self.assertEqual(Host(ip="127.0.0.1"), Host(ip="127.53.1.245"))

    def test_get_real_ip(self):
        #self.assertFalse(Host(ip=self.localhost_ip.get_real_ip()).is_localhost())
        self.assertRaises(NotImplementedError, self.localhost_ip.get_real_ip)
        self.assertEqual(self.remotehost_ip.ip, self.remotehost_ip.get_real_ip())
