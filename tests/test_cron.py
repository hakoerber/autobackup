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
