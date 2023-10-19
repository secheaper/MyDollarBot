"""
File: test_get_number_of_transactions.py
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


class TestNumberOfTransactions(BaseCase):
    """
    Unit test for display_transaction
    """
    def test_get_none(self):
        """
        Given one category, we expect one row
        """
        assert self.user.get_number_of_transactions() == 0

    def test_get_one(self):
        """
        Given one category, we expect one row
        """
        # only 1 row
        date = datetime.today()
        self.user.transactions[self.user.spend_categories[0]].append({"Date": date, "Value": 10.00})
        assert self.user.get_number_of_transactions() == 1

    def test_get_two_cat(self):
        """
        Given multiple categories, it should have the
        categories on separate lines
        """
        # 2 rows
        date = datetime.today()
        self.user.transactions[self.user.spend_categories[0]].append({"Date": date, "Value": 10.00})
        self.user.transactions[self.user.spend_categories[1]].append({"Date": date, "Value": 15.00})
        assert self.user.get_number_of_transactions() == 2

    def test_get_same_cat(self):
        """
        Given multiple purchases in same category
        """
        # 2 rows
        date = datetime.today()
        self.user.transactions[self.user.spend_categories[0]].append({"Date": date, "Value": 10.00})
        self.user.transactions[self.user.spend_categories[0]].append({"Date": date, "Value": 15.00})
        assert self.user.get_number_of_transactions() == 2
