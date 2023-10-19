"""
File: test_edit.py
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

import time
import unittest
from bot_utils import BotTest


class TestEdit(BotTest):
    """
    Test file for edit
    """

    def test_edit_command(self):
        """
        Tests the edit command
        """

        msg = self.create_text_message('/edit')
        self.bot.process_new_messages([msg])
        time.sleep(5)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/edit'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 1, \
            "For the /edit command with no records, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None

    def test_edit_command_records(self):
        """
        Tests the edit command with records
        """
        self.create_record(10.00)
        msg = self.create_text_message('/edit')
        self.bot.process_new_messages([msg])
        time.sleep(5)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/edit'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 1, \
            "For the /edit command with records, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None

        # processing a reply
        category = self.user.spend_categories[0]
        date = self.user.transactions[category][0]['Date'].date()
        value = self.user.transactions[category][0]['Value']
        msg_text = f"{date.strftime('%m/%d/%Y')},{category},{value}"
        msg = self.create_text_message(msg_text)
        self.bot.process_new_messages([msg])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == msg_text
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 1, \
            "For the /edit command with records, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None



if __name__ == '__main__':
    unittest.main()