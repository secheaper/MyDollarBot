"""
File: test_add_cmd_custom_category.py
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
from unittest.mock import Mock, patch
import teleBot

class TestAddCustomCategory(unittest.TestCase):
    def test_add_custom_category_command(self):
        # Mock the necessary dependencies
        with patch.object(teleBot.bot, 'process_new_messages') as mock_process_messages:
            with patch.object(teleBot.bot, 'next_step_backend', Mock()) as mock_next_step_backend:
                msg = Mock()
                msg.chat.id = "12345"
                msg.text = "/categoryAdd"
                custom_category = "travel"

                # Simulate bot's behavior
                teleBot.bot.process_new_messages.return_value = [msg]
                teleBot.bot.next_step_backend.handlers = []

                # Trigger the command
                teleBot.bot.process_new_messages([msg])

                # Add the custom category
                reply = Mock()
                reply.chat.id = "12345"
                reply.text = custom_category
                teleBot.bot.process_new_messages([reply])

                # Add your assertions here
                # Assert that the custom category was added to the user, possibly by checking bot.user_list

if __name__ == '__main__':
    unittest.main()