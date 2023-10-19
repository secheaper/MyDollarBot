"""
File: test_add.py
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

class TestAdd(unittest.TestCase):

    @patch('teleBot.User', return_value=Mock(spec=teleBot.User))
    @patch('teleBot.bot.send_message')
    @patch('teleBot.bot.process_new_callback_query')
    @patch('teleBot.bot.process_new_messages')
    def test_add_command(self, mock_process_messages, mock_process_callback, mock_send_message, mock_user):
        bot = teleBot.bot
        user_instance = mock_user.return_value
        msg = Mock()
        msg.chat.id = "12345"
        msg.text = "/add"
        query = Mock()
        query.chat_instance.id = "12345"
        query.data = "2021,11,01"
        reply = Mock()
        reply.text = "1.00"
        user_instance.spend_categories = ["Category1"]

        bot.process_new_messages([msg])
        bot.process_new_callback_query([query])
        bot.process_new_messages([reply])

        # Add your assertions here

    @patch('teleBot.User', return_value=Mock(spec=teleBot.User))
    @patch('teleBot.bot.send_message')
    @patch('teleBot.bot.process_new_callback_query')
    @patch('teleBot.bot.process_new_messages')
    def test_add_wrong_date(self, mock_process_messages, mock_process_callback, mock_send_message, mock_user):
        bot = teleBot.bot
        user_instance = mock_user.return_value
        msg = Mock()
        msg.chat.id = "12345"
        msg.text = "/add"
        query = Mock()
        query.chat_instance.id = "12345"
        query.data = "invalid_date"

        bot.process_new_messages([msg])
        bot.process_new_callback_query([query])

        # Add your assertions for the incorrect date scenario

    @patch('teleBot.User', return_value=Mock(spec=teleBot.User))
    @patch('teleBot.bot.send_message')
    @patch('teleBot.bot.process_new_callback_query')
    @patch('teleBot.bot.process_new_messages')
    def test_add_wrong_cat(self, mock_process_messages, mock_process_callback, mock_send_message, mock_user):
        bot = teleBot.bot
        user_instance = mock_user.return_value
        msg = Mock()
        msg.chat.id = "12345"
        msg.text = "/add"
        query = Mock()
        query.chat_instance.id = "12345"
        query.data = "2021,11,01"
        reply = Mock()
        reply.text = "INVALID"
        user_instance.spend_categories = ["Category1"]

        bot.process_new_messages([msg])
        bot.process_new_callback_query([query])
        bot.process_new_messages([reply])

        # Add your assertions for the incorrect category scenario

    @patch('teleBot.User', return_value=Mock(spec=teleBot.User))
    @patch('teleBot.bot.send_message')
    @patch('teleBot.bot.process_new_callback_query')
    @patch('teleBot.bot.process_new_messages')
    def test_add_wrong_num(self, mock_process_messages, mock_process_callback, mock_send_message, mock_user):
        bot = teleBot.bot
        user_instance = mock_user.return_value
        msg = Mock()
        msg.chat.id = "12345"
        msg.text = "/add"
        query = Mock()
        query.chat_instance.id = "12345"
        query.data = "2021,11,01"
        reply = Mock()
        reply.text = "-1"
        user_instance.spend_categories = ["Category1"]

        bot.process_new_messages([msg])
        bot.process_new_callback_query([query])
        bot.process_new_messages([reply])

        # Add your assertions for the incorrect amount scenario

if __name__ == '__main__':
    unittest.main()