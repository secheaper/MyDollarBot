"""
File: test_delete_custom_category.py
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
import unittest
from BaseCase import BaseCase

class TestDeleteCustomCategory(BaseCase):
    """
    Unit test for deleting custom category
    """
    def test_delete_custom_category(self):
        """
        Deleting a custom category, the custom category then does not reflect in the category list
        """

        custom_category = "books"
        self.user.add_category(custom_category, 1)
        raw_content = self.user.transactions.keys()
        categories = []
        for category in raw_content:
            categories.append(category)
        assert custom_category in categories

        self.user.delete_category(custom_category, 1)
        content = self.user.transactions.keys()
        categories = []
        for category in content:
            categories.append(category)
        assert custom_category not in categories

if __name__ == '__main__':
    unittest.main()
