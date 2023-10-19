"""
File: test_validate_entered_amount.py
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


class TestValidateEnteredAmount(BaseCase):
    """
    Unit test for get user history
    """

    def test_validate_entered_amount_empty(self):
        """
        Asserts when validate_entered_amount is given an empty string,
        0 is returned

        """
        # given an empty string for amount entered, 0 should be returned
        assert self.user.validate_entered_amount("") == 0

    def test_validate_entered_amount_string(self):
        """
        Asserts when validate_entered_amount is given a string
        0 is returned
        """
        # given an string, 0 should be returned
        assert self.user.validate_entered_amount("Test") == 0
        # given a string that contains numbers and a string
        assert self.user.validate_entered_amount("000t") == 0

    def test_validate_entered_amount_nan(self):
        """
        Asserts when validate_entered_amount is given an invalid
        number, 0 is returned
        """
        # given a negative number
        assert self.user.validate_entered_amount("-1") == 0
        # given 0
        assert self.user.validate_entered_amount("0") == 0
        # given a number with dollar sign
        assert self.user.validate_entered_amount("$10") == 0
        # given a number with 2 decimals
        assert self.user.validate_entered_amount("10..0") == 0

    def test_validate_entered_amount_valid(self):
        """
        Asserts when validate_entered_amount is given an valid
        number, the number is returned
        """
        # given a positive number
        assert self.user.validate_entered_amount("1") == 1.00
        # given a positive number with decimals
        assert self.user.validate_entered_amount("10.10") == 10.10
        # given a number with 14 digits
        assert self.user.validate_entered_amount("1000000000.00") == 1000000000.00
