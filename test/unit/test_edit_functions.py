"""
File: test_edit_functions.py
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
from datetime import datetime, timedelta


class TestAddUserRecord(BaseCase):
    """
        Tests the edit series of functions in bot.py
    """

    def test_store_edit_transaction(self):
        """
        After user enters existing transaction and data is parsed from input
        user.edit_transaction should be that transaction
        user.edit_category should be the category of that transaction
        """
        # User enters the following date,category, value
        user_date = datetime.today()
        user_category = "Food"
        user_value = 10.00
        userid = "1"
        self.user.add_transaction(user_date, user_category, user_value, userid)
        transaction = {"Date": user_date, "Value": user_value}
        self.user.store_edit_transaction(transaction, user_category)
        assert transaction == self.user.edit_transactions
        assert user_category == self.user.edit_category

    def test_edit_date(self):
        # User enters the following date,category, value
        user_date = datetime.today()
        edit_date = datetime.today() - timedelta(days=1)
        user_category = "Groceries"
        user_value = 10.00
        userid = "1"
        self.user.add_transaction(user_date, user_category, user_value, userid)
        transaction = {"Date": user_date, "Value": user_value}
        self.user.store_edit_transaction(transaction, user_category)
        self.user.edit_transaction_date(edit_date)
        assert self.user.transactions["Groceries"][0]["Date"].date() == edit_date.date()

    def test_edit_transaction_category(self):
        # User enters the following date,category, value
        user_date = datetime.today()
        user_category = "Utilities"
        edit_category = "Transport"
        user_value = 10.00
        userid = "1"
        self.user.add_transaction(user_date, user_category, user_value, userid)
        transaction = {"Date": user_date, "Value": user_value}
        self.user.store_edit_transaction(transaction, user_category)
        self.user.edit_transaction_category(edit_category)
        assert self.user.transactions[edit_category][0] == transaction

    def test_edit_transaction_value(self):
        # User enters the following date,category, value
        user_date = datetime.today()
        user_category = "Shopping"
        user_value = 10.00
        edit_value = 20.00
        userid = "1"
        self.user.add_transaction(user_date, user_category, user_value, userid)
        transaction = {"Date": user_date, "Value": user_value}
        self.user.store_edit_transaction(transaction, user_category)
        self.user.edit_transaction_value(edit_value)
        assert self.user.transactions["Shopping"][0]["Value"] == edit_value
