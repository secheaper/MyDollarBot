"""
File: test_delete_history.py
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
from BaseCase import BaseCase


class TestDeleteHistory(BaseCase):
    """
    Unit test for deleteHistory
    """

    def test_delete_history_none(self):
        """
        Given no transactions, the list should not change
        """
        # given no history
        assert self.user.get_number_of_transactions() == 0
        # doing deleteHistory
        self.user.deleteHistory()
        # should not do anything
        assert self.user.get_number_of_transactions() == 0

    def test_delete(self):
        """
        Given there is one user
        deleting a transaction
        should remove it
        """
        # given adding one user
        date = datetime.today()
        transaction = self.create_transaction()
        record = {"Date": date, "Value": 10.00}
        transaction[self.user.spend_categories[0]].append(record)
        self.user.transactions[self.user.spend_categories[0]].append(record)
        # delete the transaction
        self.user.deleteHistory(transaction)
        assert self.user.get_number_of_transactions() == 0
        assert self.user.transactions[self.user.spend_categories[0]] == []

    def test_delete_multiple(self):
        """
        Given there is multiple transactions
        deleting one should work
        """
        # given adding one user
        date = datetime.today()
        transaction = self.create_transaction()
        record = {"Date": date, "Value": 10.00}
        # appending the transaction
        self.user.transactions[self.user.spend_categories[0]].append(record)
        # creating a record to delete
        to_delete = {"Date": date, "Value": 15.00}
        transaction[self.user.spend_categories[0]].append(to_delete)
        self.user.transactions[self.user.spend_categories[0]].append(to_delete)
        # delete the transaction
        self.user.deleteHistory(transaction)
        assert self.user.get_number_of_transactions() == 1
        assert self.user.transactions[self.user.spend_categories[0]] == [record]

    def test_delete_multiple_record(self):
        """
        Given there is one user
        deleting one record from the user
        should remove it from the user list
        """
        # given adding one user
        date = datetime.today()
        transaction = self.create_transaction()
        record = {"Date": date, "Value": 10.00}
        # appending the transaction
        self.user.transactions[self.user.spend_categories[0]].append(record)
        # creating a record to delete
        to_delete = {"Date": date, "Value": 15.00}
        transaction[self.user.spend_categories[0]].append(to_delete)
        self.user.transactions[self.user.spend_categories[0]].append(to_delete)
        # delete the transaction
        self.user.deleteHistory(transaction)
        assert self.user.get_number_of_transactions() == 1
        assert self.user.transactions[self.user.spend_categories[0]] == [record]

        # delete the last record
        transaction = self.create_transaction()
        transaction[self.user.spend_categories[0]].append(record)
        self.user.deleteHistory(transaction)
        assert self.user.get_number_of_transactions() == 0
        assert self.user.transactions[self.user.spend_categories[0]] == []
