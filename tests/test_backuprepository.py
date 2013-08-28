import unittest
import datetime

import backuprepository
import filesystem
import path


class Tests(unittest.TestCase):

    def setUp(self):
        self.backup1 = backuprepository.Backup(path.FullLocation(
            None, None, "/whatevsz/2010-12-15T21:13:02.bak", None))
        self.backup2 = backuprepository.Backup(path.FullLocation(
            None, None, "/whatevsz/2011-03-23T13:59:45.bak", None))
        self.backup3 = backuprepository.Backup(path.FullLocation(
            None, None, "/whatevsz/2005-10-01T01:10:30.bak", None))

    def test_backup_date(self):
        self.assertEqual(
            self.backup1.birth, datetime.datetime(2010,12,15,21,13,02))
        self.assertEqual(
            self.backup2.birth, datetime.datetime(2011,03,23,13,59,45))
        self.assertEqual(
            self.backup3.birth, datetime.datetime(2005,10,01,01,10,30))

    def test_wrong_time_format(self):
        self.assertRaises(ValueError,
                          backuprepository.Backup, path.FullLocation(
                              None, None,
                              "wrongformat1234.bak", None))

    def test_wrong_suffix(self):
        self.assertRaises(ValueError,
                          backuprepository.Backup, path.FullLocation(
                              None, None,
                              "2012-07-30T11:59:14.wrongsuffix", None))

        self.assertRaises(ValueError,
                          backuprepository.Backup, path.FullLocation(
                              None, None,
                              "2012-07-30T11:59:14bak", None))

    def test_wrong_dirname(self):
        self.assertRaises(ValueError,
                          backuprepository.Backup,
                          path.FullLocation(
                              None, None,
                              "error@wrong_in_every_way:fail", None))
