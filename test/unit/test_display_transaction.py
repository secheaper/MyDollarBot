"""
File: test_display_transactions.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: File contains Test cases.

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from BaseCase import BaseCase
from datetime import datetime


class TestDisplayTransaction(BaseCase):
    """
    Unit test for display_transaction
    """

    def test_display_one_cat(self):
        """
        Given one category, we expect one row
        """
        # only 1 row
        date = datetime.today()
        transaction = {self.user.spend_categories[0]: [{"Date": date, "Value": 10.00}]}
        expected_str = f'{self.user.spend_categories[0]}, {date.date()}, 10.00\n'
        assert self.user.display_transaction(transaction) == expected_str

    def test_display_two_cat(self):
        """
        Given multiple categories, it should have the
        categories on separate lines
        """
        # 2 rows
        date = datetime.today()
        transaction = {self.user.spend_categories[0]: [{"Date": date, "Value": 10.00}],
                       self.user.spend_categories[1]: [{"Date": date, "Value": 15.00}]}
        expected_str = f'{self.user.spend_categories[0]}, {date.date()}, 10.00\n' \
                       f'{self.user.spend_categories[1]}, {date.date()}, 15.00\n'
        assert self.user.display_transaction(transaction) == expected_str

    def test_display_multiple_row(self):
        """
        Given multiple purchases in same category
        """
        date = datetime.today()
        transaction = {self.user.spend_categories[0]: [{"Date": date, "Value": 10.00},
                                                       {"Date": date, "Value": 15.00}]}
        expected_str = f'{self.user.spend_categories[0]}, {date.date()}, 10.00\n' \
                       f'{self.user.spend_categories[0]}, {date.date()}, 15.00\n'
        assert self.user.display_transaction(transaction) == expected_str

    def test_display_spending_multiple_all(self):
        """
        Given multiple categories with multiple spending's
        """
        date = datetime.today()
        transaction = {self.user.spend_categories[0]: [{"Date": date, "Value": 10.00},
                                                       {"Date": date, "Value": 15.00}],
                       self.user.spend_categories[1]: [{"Date": date, "Value": 5}]}
        expected_str = f'{self.user.spend_categories[0]}, {date.date()}, 10.00\n' \
                       f'{self.user.spend_categories[0]}, {date.date()}, 15.00\n' \
                       f'{self.user.spend_categories[1]}, {date.date()}, 5.00\n'
        ret = self.user.display_transaction(transaction)
        assert ret == expected_str
