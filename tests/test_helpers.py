import unittest
from datetime import datetime

import helpers


class MyTestCase(unittest.TestCase):

    def test_get_date_jan(self):
        self.assertEqual(helpers.get_date("Jan. 12"), datetime(2023, 1, 12, 0, 0, 0))  # add assertion here

    def test_get_date_may(self):
        self.assertEqual(helpers.get_date("May 12"), datetime(2023, 5, 12, 0, 0, 0))  # add assertion here

    def test_get_date_sep(self):
        self.assertEqual(helpers.get_date("Sept. 12"), datetime(2023, 9, 12, 0, 0, 0))  # add assertion here

    def test_get_date_wrong_date(self):
        self.assertRaises(ValueError, helpers.get_date, "Dec. 33")

    def test_get_date_sep_with_year(self):
        self.assertEqual(helpers.get_date("Sept. 12, 2001"), datetime(2001, 9, 12, 0, 0, 0))  # add assertion here

    def test_get_date_may_with_year(self):
        self.assertEqual(helpers.get_date("May 12, 1991"), datetime(1991, 5, 12, 0, 0, 0))  # add assertion here

    def test_add_date_plus_one_month(self):
        self.assertEqual(helpers.add_months(datetime(1991, 5, 12), 1), datetime(1991, 6, 12))  # add assertion here

    def test_add_date_minus_one_month(self):
        self.assertEqual(helpers.add_months(datetime(1991, 5, 12), -1), datetime(1991, 4, 12))  # add assertion here

    def test_add_date_feb(self):
        self.assertEqual(helpers.add_months(datetime(1991, 3, 30), -1), datetime(1991, 2, 28))  # add assertion here


if __name__ == '__main__':
    unittest.main()
