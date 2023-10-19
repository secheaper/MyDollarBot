"""
File: test_display.py
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


class TestDisplay(BotTest):
    """
    Test file for display
    """

    def test_display_command(self):
        """
        Tests the display command
        """
        msg = self.create_text_message('/display')
        self.bot.process_new_messages([msg])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/display'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 0, \
            "For the /display command without records, there should not be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None

    def test_display_command_records(self):
        """
        Tests the display command
        """
        self.create_record(10.00)
        msg = self.create_text_message('/display')
        self.bot.process_new_messages([msg])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/display'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 1, \
            "For the /display command with records, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None
        reply = self.create_text_message("Day")
        self.bot.process_new_messages([reply])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert reply.chat.id is not None
        assert reply.text == "Day"
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 0, \
            "For the  reply to /display, there should not be a next step"


    def test_display_command_records(self):
        """
        Tests the display command with Month
        """
        self.create_record(10.00)
        msg = self.create_text_message('/display')
        self.bot.process_new_messages([msg])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert msg.chat.id is not None
        assert msg.text == '/display'
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 1, \
            "For the /display command with records, there should be a next step"
        # there should not be any exceptions
        assert self.bot.worker_pool.exception_info is None
        reply = self.create_text_message("Month")
        self.bot.process_new_messages([reply])
        time.sleep(3)

        # assert the message was sent, and text was not changed
        assert reply.chat.id is not None
        assert reply.text == "Month"
        # there should be a next step handler
        assert len(self.bot.next_step_backend.handlers) == 0, \
            "For the  reply to /display, there should not be a next step"




if __name__ == '__main__':
    unittest.main()