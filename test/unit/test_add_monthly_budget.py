"""
File: test_add_monthly_budget.py
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

class TestAddMonthlyBudget(discord_BaseCase):
    def test_add_monthly_budget_valid(self):
        """
        Asserts when add_monthly_budget is given a float value
        """
        assert self.user.monthly_budget == 0
        amount = 10.00
        self.user.add_monthly_budget(amount, 2)
        assert self.user.monthly_budget == amount

    def test_add_monthly_budget_invalid(self):
        """
        Asserts when add_monthly_budget is given 0
        """
        assert self.user.monthly_budget == 0
        amount_valid = 10.00
        self.user.add_monthly_budget(amount_valid, 2)
        assert self.user.monthly_budget == amount_valid
        amount = 0.00
        self.user.add_monthly_budget(amount, 2)
        assert self.user.monthly_budget == amount_valid
