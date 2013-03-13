import unittest
import datetime

import backupRepository

class Tests(unittest.TestCase):

    def setUp(self):
        self.backup1 = backupRepository.Backup("2010-12-15T21:13:02.bak")
        self.backup2 = backupRepository.Backup("2011-03-23T13:59:45.bak")
        self.backup3 = backupRepository.Backup("2005-10-01T01:10:30.bak")

    def test_backup_date(self):
        self.assertEqual(self.backup1.birth, datetime.datetime(2010,12,15,21,13,02))
        self.assertEqual(self.backup2.birth, datetime.datetime(2011,03,23,13,59,45))
        self.assertEqual(self.backup3.birth, datetime.datetime(2005,10,01,01,10,30))

    def test_wrong_time_format(self):
        self.assertRaises(ValueError, backupRepository.Backup, "wrongformat1234.bak")

    def test_wrong_suffix(self):
        self.assertRaises(ValueError, backupRepository.Backup, "2012-07-30T11:59:14.wrongsuffix")
        self.assertRaises(ValueError, backupRepository.Backup, "2012-07-30T11:59:14bak")

    def test_wrong_dirname(self):
        self.assertRaises(ValueError, backupRepository.Backup, "error@wrong_in_every_possible_way:fail")
