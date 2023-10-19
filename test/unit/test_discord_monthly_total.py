"""
File: test_discord_monthly_total.py
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

from discord_BaseCase import discord_BaseCase
from datetime import datetime

class TestMonthlyTotal(discord_BaseCase):
    """
    Unit test for monthly total
    """
    def test_one_transaction(self):
        """
        Given one transaction, we expect total to be the value of that transaction
        """
        date = datetime.today()
        value = 12.00
        transaction = self.create_transaction()
        date = datetime.today()
        record = {"Date": date, "Value": value}
        transaction[self.user.spend_categories[0]].append(record)
        for category in transaction:
            # for each record to add
            for record in transaction[category]:
                self.user.add_transaction(record['Date'], category, record['Value'], 2)
        assert self.user.monthly_total() == value

    def test_multiple_transaction_same_cat(self):
        """
        Given multiple transactions of same category, we expect total to be the sum of all the transactions
        """
        date = datetime.today()
        value = [12.00, 11.00]
        transaction = self.create_transaction()
        date = datetime.today()
        records = [{"Date": date, "Value": value[0]}, {"Date": date, "Value": value[1]}]
        for record in records:
            transaction[self.user.spend_categories[0]].append(record)
        for category in transaction:
            # for each record to add
            for record in transaction[category]:
                self.user.add_transaction(record['Date'], category, record['Value'], 2)
        assert self.user.monthly_total() == sum(value)

    def test_multiple_transaction_multiple_cat(self):
        """
        Given multiple transactions of different categories, we expect total to be the sum of all the transactions
        """
        date = datetime.today()
        value = [12.00, 11.00, 21.50, 14.25]
        transaction = self.create_transaction()
        date = datetime.today()
        transaction[self.user.spend_categories[0]].append({"Date": date, "Value": value[0]})
        transaction[self.user.spend_categories[0]].append({"Date": date, "Value": value[1]})
        transaction[self.user.spend_categories[1]].append({"Date": date, "Value": value[2]})
        transaction[self.user.spend_categories[1]].append({"Date": date, "Value": value[3]})
        for category in transaction:
            # for each record to add
            for record in transaction[category]:
                self.user.add_transaction(record['Date'], category, record['Value'], 2)
        assert self.user.monthly_total() == sum(value)


if __name__ == '__main__':
    unittest.main()
