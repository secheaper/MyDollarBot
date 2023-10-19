"""
File: BaseCase.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: File contains Helper functions for Test classes.

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

import os.path
import pathlib
import unittest

try:
    from src import teleUser
    import src.teleUser as teleUser
    from src.teleUser import User
except:
    from teleUser import User

class BaseCase(unittest.TestCase):
    """
    Base case class for all other unit tests to inherit from
    """
    def setUp(self) -> None:
        """
        Creates a new user
        """
        # os.chdir("test")
        abspath = pathlib.Path("teleData").absolute()
        print(abspath, "abs path")
        if not os.path.exists(abspath):
            os.mkdir(abspath)

        # print(os.getcwd())
        self.user = User("1")
        self.expected_list = self.create_transaction()

    def tearDown(self) -> None:
        """
        Removes the user pickle
        """
        abspath = pathlib.Path("teleData").absolute()
        if not os.path.exists(abspath):
            os.mkdir(abspath)

    def create_transaction(self):
        """
        Creates the dictionary of transactions
        """
        transaction = {}
        for category in self.user.spend_categories:
            transaction[category] = []
        return transaction

    def add_record(self, category, record):
        """
        Adds a record to the internal expected transactions
        """
        self.expected_list[category].append(record)


if __name__ == '__main__':
    unittest.main()
