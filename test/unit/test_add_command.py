"""
File: test_add_command.py
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

import logging
import os
import pathlib
import unittest
from datetime import datetime
from importlib import reload

from telebot import types

import teleBot
from teleUser import User

CHAT_ID = os.environ['CHAT_ID'] if 'CHAT_ID' in os.environ else 1
TOKEN = os.environ['API_TOKEN'] if 'API_TOKEN' in os.environ else 0


class BotTest(unittest.TestCase):
    """
    Base test class for Bot Tests
    """

    def setUp(self) -> None:
        """
        Creates a new user and ensures no data was left over
        :return: None
        """
        abspath = pathlib.Path("data").absolute()
        if not os.path.exists(abspath):
            os.mkdir(abspath)
        reload(teleBot.bot)
        teleBot.bot.api_token = os.environ['API_TOKEN']
        self.bot = teleBot.bot.bot
        self.user = User(str(CHAT_ID))
        self.user.save_user(str(CHAT_ID))
        self.chat_id = CHAT_ID
        # reloads the user list
        teleBot.bot.user_list = teleBot.bot.get_users()
        # asserts the current user has no data
        assert self.user.get_number_of_transactions() == 0

    def tearDown(self) -> None:
        # Clearing out next step handlers
        self.bot.next_step_backend.handlers = {}
        path = f"data/{CHAT_ID}.pickle"
        abspath = pathlib.Path(path).absolute()
        if os.path.exists(abspath):
            os.remove(path)
        # verifying all old info was deleted
        self.user = User(CHAT_ID)
        assert self.user.get_number_of_transactions() == 0

    def create_record(self, amount: float) -> None:
        """
        Creates a record in the user list for the given amount
        :param amount: amount to add
        :return: None
        """
        self.user.add_transaction(datetime.now(), self.user.spend_categories[0], amount, CHAT_ID)
        self.user.save_user(CHAT_ID)
        teleBot.bot.user_list = teleBot.bot.get_users()
        assert CHAT_ID in teleBot.bot.user_list.keys()

    def create_text_message(self, text: str) -> types.Message:
        """
        Creates a text message
        :param text: text of the message
        :return: The created message to be sent
        """
        params = {'text': text}
        chat = types.User(int(CHAT_ID), False, 'test')
        return types.Message(1, None, None, chat, 'text', params, "")

    def create_callback_query(self, data: str, message: types.Message) -> types.CallbackQuery:
        """
        Creates a text message
        :param text: text of the message
        :return: The created message to be sent
        """
        chat = types.User(int(CHAT_ID), False, 'test')
        return types.CallbackQuery(1, CHAT_ID, data, chat, message)
