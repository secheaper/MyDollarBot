"""
File: test_validate_date_formate.py
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


class TestValidateDateFormat(BaseCase):
    """
    Unit test for validate_date_format
    """

    def test_valid_date(self):
        """
        Given no transactions, the list should not change
        """
        date = datetime.today()
        # format it as a year
        dateFormat = '%d-%b-%Y'
        monthFormat = '%b-%Y'
        validated_d_m_y = self.user.validate_date_format(date.strftime(dateFormat), dateFormat)
        assert validated_d_m_y.month == date.month
        assert validated_d_m_y.day == date.day
        assert validated_d_m_y.year == date.year
        validated_m_y = self.user.validate_date_format(date.strftime(monthFormat), monthFormat)
        assert validated_m_y.month == date.month
        assert validated_m_y.year == date.year

    def test_invalid(self):
        """
        Given there is one user
        deleting a transaction
        should remove it
        """
        date = datetime.today()
        # invalid formats
        dateFormat = 'random'
        error = self.user.validate_date_format(date.strftime('%d-%b-%Y'), dateFormat)
        assert error is None
        # mismatched formats
        dateFormat = '%d-%b-%Y'
        monthFormat = '%b-%Y'
        validated_m_y = self.user.validate_date_format(date.strftime(dateFormat), monthFormat)
        assert validated_m_y is None
