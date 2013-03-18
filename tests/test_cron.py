import unittest
import datetime

import cron

class Tests(unittest.TestCase):
    
    def setUp(self):
        self.c1 = cron.Cronjob("1 10-15 5 6,7,8,11 2012-2015 *")

    def test_matching(self):
        d_in_lo    = datetime.datetime(2012,  6,  5, 10,  1)
        d_out_lo_1 = datetime.datetime(2011,  6,  5, 10,  1)
        d_out_lo_2 = datetime.datetime(2012,  5,  5, 10,  1)
        d_out_lo_3 = datetime.datetime(2012,  6,  4, 10,  1)
        d_out_lo_4 = datetime.datetime(2012,  6,  5,  9,  1)
        d_out_lo_5 = datetime.datetime(2012,  6,  5, 10,  0)

        d_in_hi    = datetime.datetime(2015, 11,  5, 15,  1)
        d_out_hi_1 = datetime.datetime(2016, 11,  5, 15,  1)
        d_out_hi_2 = datetime.datetime(2015, 12,  5, 15,  1)
        d_out_hi_3 = datetime.datetime(2015, 11,  6, 15,  1)
        d_out_hi_4 = datetime.datetime(2015, 11,  5, 16,  1)
        d_out_hi_5 = datetime.datetime(2015, 11,  5, 15,  2)

        self.assertTrue(self.c1.matches(d_in_lo))
        self.assertFalse(self.c1.matches(d_out_lo_1))
        self.assertFalse(self.c1.matches(d_out_lo_2))
        self.assertFalse(self.c1.matches(d_out_lo_3))
        self.assertFalse(self.c1.matches(d_out_lo_4))
        self.assertFalse(self.c1.matches(d_out_lo_5))

        self.assertTrue(self.c1.matches(d_in_hi))
        self.assertFalse(self.c1.matches(d_out_hi_1))
        self.assertFalse(self.c1.matches(d_out_hi_2))
        self.assertFalse(self.c1.matches(d_out_hi_3))
        self.assertFalse(self.c1.matches(d_out_hi_4))
        self.assertFalse(self.c1.matches(d_out_hi_5))

    def test_latest_occurence(self):
        d1 = datetime.datetime(2014, 8, 7, 23, 12)
        occurence = self.c1.get_most_recent_occurence(d1)
        dr = datetime.datetime(2014, 8, 5, 15, 1)
        self.assertEqual(occurence, dr)

    def test_latest_occurence_exact(self):
        d1 = datetime.datetime(2013, 8, 5, 13, 1)
        self.assertEqual(self.c1.get_most_recent_occurence(d1), d1)
        
        
    def test_latest_occurence_fails_when_too_old(self):
        d1 = datetime.datetime(1999, 8, 5, 13, 1)
        self.assertRaises(ValueError, self.c1.get_most_recent_occurence, d1)

    def test_latest_occurence_max(self):
        d1 = datetime.datetime(2023, 5, 24, 2, 54)
        dr = datetime.datetime(2015, 11, 5, 15, 1)
        self.assertEqual(self.c1.get_most_recent_occurence(d1), dr)
        
    def test_max_time(self):
        dr = datetime.datetime(2015, 11, 5, 15, 1)
        self.assertEqual(self.c1.get_max_time(), dr)

    def test_min_time(self):
        dr = datetime.datetime(2012, 6, 5, 10, 1)
        self.assertEqual(self.c1.get_min_time(), dr)
        
    def test_has_occured_since(self):
        d1 = datetime.datetime(1999, 8, 5, 13, 1)
        self.assertEqual(self.c1.has_occured_since(d1),
                         self.c1.has_occured_between(d1, 
                                                     datetime.datetime.now()))
                                                     
    def test_has_occured_between(self):
        d_older   = datetime.datetime(2013,  9, 23, 10, 59)
        d_younger = datetime.datetime(2014, 12,  1,  8, 23)
        self.assertRaises(ValueError, self.c1.has_occured_between, 
                          d_younger, d_older)
        self.c1.has_occured_between(d_older, d_younger)
        self.assertTrue(self.c1.has_occured_between(d_older, d_younger))
