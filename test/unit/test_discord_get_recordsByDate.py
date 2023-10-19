"""
File: test_discord_get_recordsByData.py
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

from datetime import datetime

from discord_BaseCase import discord_BaseCase


class TestGetRecordsByDate(discord_BaseCase):
    """
    Unit test for deleteHistory
    def get_records_by_date(date, chat_id, is_month):

    By this method, tests have been completed that the user is present
    Thus, there are no tests for user not present
    """

    def add_expected(self):

        self.oct_01 = {"Date": datetime(month=10, day=1, year=2021), "Value": 10.00}
        self.oct_10 = {"Date": datetime(month=10, day=10, year=2021), "Value": 15.00}
        self.nov_01 = {"Date": datetime(month=11, day=1, year=2021), "Value": 5.00}
        self.add_record(self.user.spend_categories[0], self.oct_01)
        self.add_record(self.user.spend_categories[0], self.oct_10)
        self.add_record(self.user.spend_categories[0], self.nov_01)

    def test_user_date_not_present(self):
        """
        Given there is one user
        calling get_records_by_date with a non-present date
        should return []
        """
        self.add_expected()
        wrong_date = datetime.now()
        # make the date year 1, month 1, day 1
        wrong_date = wrong_date.replace(1, 1, 1)
        # given the user_list
        self.user.transactions = self.expected_list
        user_history = self.user.get_records_by_date(wrong_date, False)
        # there should be no records
        assert user_history == self.create_transaction()
        user_history = self.user.get_records_by_date(wrong_date, True)
        # there should be no records
        assert user_history == self.create_transaction()

    def test_get_by_month(self):
        """
        Given there is one user
        calling get_records_by_date by month
        """
        self.add_expected()
        # given the user_list
        self.user.transactions = self.expected_list

        october = datetime.now()
        # make the date match october 2021
        october = october.replace(year=2021, month=10).date()
        user_history = self.user.get_records_by_date(october, True)
        # the records should match october 2021
        expected_transactions = self.create_transaction()
        # filter everything that is Oct-2021
        expected_transactions[self.user.spend_categories[0]] = [self.oct_01, self.oct_10]
        assert user_history == expected_transactions

    def test_get_by_day(self):
        """
        Given there is one user
        calling get_records_by_date with a valid date
        """

        self.add_expected()
        # given the user_list
        self.user.transactions = self.expected_list

        october = datetime.now()
        # make the date match october 2021
        october = october.replace(year=2021, month=10, day=1).date()
        user_history = self.user.get_records_by_date(october, False)
        # the records should match october 2021
        expected_transactions = self.create_transaction()
        # filter everything that is Oct-2021
        expected_transactions[self.user.spend_categories[0]] = [self.oct_01]
        assert user_history == expected_transactions

    def test_get_by_all(self):
        """
        Given there is one user
        calling all
        """
        self.add_expected()
        # given the user_list
        self.user.transactions = self.expected_list

        user_history = self.user.get_records_by_date("all", True)
        # there should all
        assert user_history == self.expected_list
