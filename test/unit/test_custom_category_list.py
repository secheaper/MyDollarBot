"""
File: test_custom_category_list.py
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

from bot_utils import BotTest
import unittest
import time
import teleBot


class TestListCustomCategory(BotTest):
    """
        Test file for add custom category
    """
    def test_list_custom_category_command(self):
        """
        Tests the add custom category command
        """

        # creation of mock data
        msg = self.create_text_message('/categoryAdd')
        self.bot.process_new_messages([msg])
        time.sleep(3)
        custom_category = "books"
        reply = self.create_text_message(custom_category)
        self.bot.process_new_messages([reply])
        time.sleep(3)

        # test for validating category list command
        msg = self.create_text_message('/categoryList')
        self.bot.process_new_messages([msg])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/categoryList'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 0, \
            "For the /categoryList command, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None

        # assert the custom category was added to the user
        chat_id = str(msg.chat.id)
        content = teleBot.user_list[chat_id].transactions
        categories = []
        for category in content:
            categories.append(category)
        assert custom_category in categories

if __name__ == '__main__':
    unittest.main()