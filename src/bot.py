"""
File contains bot message handlers and their associated functions
"""
import logging
import os
from calendar import monthrange
import pathlib
import pickle
import re
import time
import csv
import io
from datetime import datetime
from email.mime.application import MIMEApplication

from tabulate import tabulate
import sys
import telebot
from telebot import types
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from forex_python.converter import CurrencyRates

# sys.path.append("/Users/jayesh/Documents/GitHub/slashbot/src")
try:
    from user import User
except:
    from user import User

api_token = os.environ["API_TOKEN"]
commands = {
    "menu": "Display this menu",
    "add": "Record/Add a new spending",
    "display": "Show sum of expenditure for the current day/month",
    "history": "Display spending history",
    "delete": "Clear/Erase all your records",
    "edit": "Edit/Change spending details",
    "budget": "Set budget for the month",
    "chart": "See your expenditure in different charts",
    "categoryAdd": "Add a new custom category",
    "categoryList": "List all categories",
    "categoryDelete": "Delete a category",
    "download": "Download your history",
    "displayDifferentCurrency": "Display the sum of expenditures for the current day/month in another currency",
    "sendEmail": "Send an email with an attachment showing your history"
}

c = CurrencyRates()
DOLLARS_TO_RUPEES = c.get_rate('USD', 'INR')
DOLLARS_TO_EUROS = c.get_rate('USD', 'EUR')
DOLLARS_TO_SWISS_FRANC = c.get_rate('USD', 'CHF')

bot = telebot.TeleBot(api_token)
telebot.logger.setLevel(logging.INFO)
user_list = {}
option = {}
all_transactions = []
completeSpendings = 0

logger = logging.getLogger()


@bot.message_handler(commands=["start", "menu"])
def start_and_menu_command(m):
    """
    Handles the commands 'start' and 'menu'. Sends an intro text.

    :param m: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = m.chat.id
    print("*********************CHAT ID***************************", chat_id)
    text_intro = (
        "Welcome to SlashBot - a simple solution to track your expenses! \nHere is a list of available "
        "commands, please enter a command of your choice so that I can assist you further: \n\n "
    )
    for (
            c
    ) in (
            commands
    ):  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)


@bot.message_handler(commands=["budget"])
def command_budget(message):
    """
    Handles the commands 'budget'. Gets input for budget and stores it.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    option.pop(chat_id, None)
    if chat_id not in user_list.keys():
        user_list[chat_id] = User(chat_id)
    bot.send_message(
        chat_id,
        "Your current monthly budget is {}".format(user_list[chat_id].monthly_budget),
    )
    message = bot.send_message(
        chat_id,
        "Enter an amount to update your monthly budget. \n(Enter numeric values only)",
    )
    bot.register_next_step_handler(message, post_budget_input)


def post_budget_input(message):
    """
    Receives the amount entered by the user and then adds it to the monthly_budget attribute of the user object. An
    error is displayed if the entered amount is zero. Else, a message is shown that the budget has been added. :param
    message: telebot.types.Message object representing the message object.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        amount_entered = message.text
        amount_value = user_list[chat_id].validate_entered_amount(
            amount_entered
        )  # validate
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Budget amount has to be a positive number.")
        user_list[chat_id].add_monthly_budget(amount_value, chat_id)
        bot.send_message(
            chat_id,
            "The budget for this month has been set as ${}".format(
                format(amount_value, ".2f")
            ),
        )

    except Exception as ex:
        bot.reply_to(message, "Oh no. " + str(ex))


@bot.message_handler(commands=["add"])
def command_add(message):
    """
    Handles the command 'add'. Lists the categories from which the user can select. The function
    'post_category_selection' is called next. :param message: telebot.types.Message object representing the message
    object

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    option.pop(chat_id, None)
    if chat_id not in user_list.keys():
        user_list[chat_id] = User(chat_id)
    user = user_list[chat_id]
    try:
        markup = get_calendar_buttons(user)
        bot.send_message(chat_id, "Click the date of purchase:", reply_markup=markup)
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - \nError : " + str(ex))


def is_add_callback(query):
    return query.data != "none" and "/" not in query.data


@bot.callback_query_handler(func=is_add_callback, filter=None)
def post_date_selection(message):
    """
    Once a date is selected, this function is called and queries the user to enter a category

    :param message: the message sent after the user clicks a button
    :return: None
    """
    chat_id = str(message.message.chat.id)
    option.pop(chat_id, None)

    try:
        if chat_id not in user_list.keys():
            user_list[chat_id] = User(chat_id)
        user = user_list[chat_id]
        # if they want to go back/forward a month
        date_to_add = handler_callback(message.data, user)
        if date_to_add is None:
            # just edit the calendar
            bot.edit_message_reply_markup(
                chat_id=message.from_user.id,
                message_id=message.message.message_id,
                reply_markup=get_calendar_buttons(user),
            )
            return
        if date_to_add == -1:
            # invalid date
            fmt_min, fmt_max = user.min_date.strftime(
                "%m/%d/%Y"
            ), user.max_date.strftime("%m/%d/%Y")
            bot.send_message(
                chat_id, "Enter a date between {} and {}".format(fmt_min, fmt_max)
            )
            return
        spend_categories = user_list[chat_id].spend_categories
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for c in spend_categories:
            markup.add(c)
        msg = bot.reply_to(message.message, "Select Category", reply_markup=markup)
        bot.register_next_step_handler(msg, post_category_selection, date_to_add)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message.message, "Processing Failed - \nError : " + str(ex))


def post_category_selection(message, date_to_add):
    """
    Receives the category selected by the user and then asks for the amount spend. If an invalid category is given,
    an error message is displayed followed by command list. IF the category given is valid, 'post_amount_input' is
    called next.

    :param message: telebot.types.Message object representing the message object
    :param date_to_add: the date of the purchase
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    try:
        selected_category = message.text
        spend_categories = user_list[chat_id].spend_categories
        if selected_category not in spend_categories:
            bot.send_message(
                chat_id, "Invalid", reply_markup=types.ReplyKeyboardRemove()
            )
            raise Exception(
                'Sorry I don\'t recognise this category "{}"!'.format(selected_category)
            )

        option[chat_id] = selected_category
        message = bot.send_message(
            chat_id,
            "How much did you spend on {}? \n(Enter numeric values only)".format(
                str(option[chat_id])
            ),
        )
        bot.register_next_step_handler(message, post_amount_input, date_to_add)
    except Exception as ex:
        bot.reply_to(message, "Oh no! " + str(ex))
        display_text = ""
        for (
                c
        ) in (
                commands
        ):  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, "Please select a menu option from below:")
        bot.send_message(chat_id, display_text)


def post_amount_input(message, date_of_entry):
    """
    Receives the amount entered by the user and then adds to transaction history. An error is displayed if the entered
     amount is zero. Else, a message is shown that the transaction has been added.

    :param date_of_entry: user entered date
    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        amount_entered = message.text
        amount_value = user_list[chat_id].validate_entered_amount(
            amount_entered
        )  # validate
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        date_str, category_str, amount_str = (
            date_of_entry.strftime("%m/%d/%Y %H:%M:%S"),
            str(option[chat_id]),
            format(amount_value, ".2f"),
        )
        user_list[chat_id].add_transaction(
            date_of_entry, option[chat_id], amount_value, chat_id
        )
        total_value = user_list[chat_id].monthly_total()
        add_message = "The following expenditure has been recorded: You have spent ${} for {} on {}".format(
            amount_str, category_str, date_str
        )

        if user_list[chat_id].monthly_budget > 0:
            if total_value > user_list[chat_id].monthly_budget:
                bot.send_message(
                    chat_id,
                    text="*You have gone over the monthly budget*",
                    parse_mode="Markdown",
                )
            elif total_value == user_list[chat_id].monthly_budget:
                bot.send_message(
                    chat_id,
                    text="*You have exhausted your monthly budget. You can check/download history*",
                    parse_mode="Markdown",
                )
            elif total_value >= 0.8 * user_list[chat_id].monthly_budget:
                bot.send_message(
                    chat_id,
                    text="*You have used 80% of the monthly budget.*",
                    parse_mode="Markdown",
                )
        bot.send_message(chat_id, add_message)
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - \nError : " + str(ex))


@bot.message_handler(commands=["history"])
def show_history(message):
    """
    Handles the command 'history'. Lists the transaction history.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        spend_total_str = ""
        count = 0
        table = [["Category", "Date", "Amount in $", "Amount in Rs."]]
        if chat_id not in list(user_list.keys()):
            raise Exception("Sorry! No spending records found!")
        if len(user_list[chat_id].transactions) == 0:
            raise Exception("Sorry! No spending records found!")
        else:
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    count = count + 1
                    date = transaction["Date"].strftime("%m/%d/%y")
                    value = format(transaction["Value"], ".2f")
                    table.append([category, date, "$ " + value])
            if count == 0:
                raise Exception("Sorry! No spending records found!")
            spend_total_str = "<pre>" + tabulate(table, headers='firstrow', tablefmt="grid") + "</pre>"
            bot.send_message(chat_id, spend_total_str, parse_mode="HTML")

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


@bot.message_handler(commands=["download"])
def download_history(message):
    """
    Handles the command 'download'. Downloads a csv file.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        count = 0
        table = [["Category", "Date", "Amount in $"]]
        if chat_id not in list(user_list.keys()):
            raise Exception("Sorry! No spending records found!")
        if len(user_list[chat_id].transactions) == 0:
            raise Exception("Sorry! No spending records found!")
        else:
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    count = count + 1
                    date = transaction["Date"].strftime("%m/%d/%y")
                    value = format(transaction["Value"], ".2f")
                    table.append([date, category, "$" + value])
            if count == 0:
                raise Exception("Sorry! No spending records found!")

            s = io.StringIO()
            csv.writer(s).writerows(table)
            s.seek(0)
            buf = io.BytesIO()
            buf.write(s.getvalue().encode())
            buf.seek(0)
            buf.name = "history.csv"
            bot.send_document(chat_id, buf)


    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


@bot.message_handler(commands=["sendEmail"])
def send_email(message):
    """
    Handles the command 'sendEmail'. Sends and email with the csvFile.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        count = 0
        table = [["Category", "Date", "Amount in $"]]
        if chat_id not in list(user_list.keys()):
            raise Exception("Sorry! No spending records found!")
        if len(user_list[chat_id].transactions) == 0:
            raise Exception("Sorry! No spending records found!")
        else:
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    count = count + 1
                    date = transaction["Date"].strftime("%m/%d/%y")
                    value = format(transaction["Value"], ".2f")
                    table.append([date, category, "$" + value])
            if count == 0:
                raise Exception("Sorry! No spending records found!")

            s = io.StringIO()
            csv.writer(s).writerows(table)
            s.seek(0)
            buf = io.BytesIO()
            buf.write(s.getvalue().encode())
            buf.seek(0)
            buf.name = "history.csv"
            # bot.send_document(chat_id, buf)
            # category = bot.reply_to(message, "Enter category name")
            category = bot.send_message(message.chat.id, "Enter your email id")
            bot.register_next_step_handler(category, acceptEmailId)

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


def acceptEmailId(message):
    email = message.text
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.fullmatch(regex, email)):
        try:
            chat_id = str(message.chat.id)
            count = 0
            table = [["Category", "Date", "Amount in $"]]
            if chat_id not in list(user_list.keys()):
                raise Exception("Sorry! No spending records found!")
            if len(user_list[chat_id].transactions) == 0:
                raise Exception("Sorry! No spending records found!")
            else:
                for category in user_list[chat_id].transactions.keys():
                    for transaction in user_list[chat_id].transactions[category]:
                        count = count + 1
                        date = transaction["Date"].strftime("%m/%d/%y")
                        value = format(transaction["Value"], ".2f")
                        table.append([date, category, "$" + value])
                if count == 0:
                    raise Exception("Sorry! No spending records found!")

                with open('history.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(table)
                # s = io.StringIO()
                # csv.writer(s).writerows(table)
                # s.seek(0)
                # buf = io.StringIO()
                # buf.write(s.getvalue().encode())
                # buf.seek(0)
                # buf.name = "history.csv"
                # writer = csv.writer(buf, dialect='excel', delimiter = ',')
                # writer.writerow(u"date", u"category", u"cost")

                # bot.send_document(chat_id, buf)
                mail_content = '''Hello,
                This email has an attached copy of your expenditure history.
                Thank you!
                '''
                #The mail addresses and password
                sender_address = 'bucksbotncsu@gmail.com'
                sender_pass = 'eevyhyshokfrrvkc'
                receiver_address = email
                # Setup the MIME
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Spending History document'
                # The subject line
                # The body and the attachments for the mail
                message.attach(MIMEText(mail_content, 'plain'))
                attach_file_name = "history.csv"
                attach_file = open(attach_file_name, 'rb')
                payload = MIMEApplication(attach_file.read(), Name=attach_file_name)
                # payload.set_payload((attach_file).read())
                encoders.encode_base64(payload)  # encode the attachment
                # add payload header with filename
                payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
                message.attach(payload)
                # Create SMTP session for sending the mail
                session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
                session.starttls()  # enable security
                session.login(sender_address, sender_pass)  # login with mail_id and password
                text = message.as_string()
                session.sendmail(sender_address, receiver_address, text)
                session.quit()
                # bot.send_message(message.chat.id, 'Mail Sent')


        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            bot.reply_to(message, str(ex))
    else:
        bot.send_message(message.chat.id, 'incorrect email')


@bot.message_handler(commands=["display"])
def command_display(message):
    """
    Handles the command 'display'. If the user has no transaction history, a message is displayed. If there is
    transaction history, user is given choices of time periods to choose from. The function 'display_total' is called
    next.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    if chat_id not in user_list or user_list[chat_id].get_number_of_transactions() == 0:
        bot.send_message(
            chat_id, "Oops! Looks like you do not have any spending records!"
        )
    else:
        try:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.row_width = 2
            for mode in user_list[chat_id].spend_display_option:
                markup.add(mode)
            msg = bot.reply_to(
                message,
                "Please select a category to see the total expense",
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, display_total)

        except Exception as ex:
            print("Exception occurred : ")
            logger.error(str(ex), exc_info=True)
            bot.reply_to(message, "Oops! - \nError : " + str(ex))


def display_total(message):
    """
    Receives the input time period and displays the transaction summary for the corresponding time period.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    dateFormat = "%m/%d/%Y"
    try:
        chat_id = str(message.chat.id)
        day_week_month = message.text

        if day_week_month not in user_list[chat_id].spend_display_option:
            raise Exception(
                'Sorry I can\'t show spendings for "{}"!'.format(day_week_month)
            )

        if len(user_list[chat_id].transactions) == 0:
            raise Exception("Oops! Looks like you do not have any spending records!")

        bot.send_message(chat_id, "Hold on! Calculating...")

        if day_week_month == "Day":
            query = datetime.today()
            query_result = ""
            total_value = 0
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    if transaction["Date"].strftime("%d") == query.strftime("%d"):
                        query_result += "Category {} Date {} Value {:.2f} \n".format(
                            category,
                            transaction["Date"].strftime(dateFormat),
                            transaction["Value"],
                        )
                        total_value += transaction["Value"]
            total_spendings = "Here are your total spendings for the date {} \n".format(
                datetime.today().strftime("%m/%d/%Y")
            )
            total_spendings += query_result
            total_spendings += "Total Value {:.2f}".format(total_value)
            bot.send_message(chat_id, total_spendings)
        elif day_week_month == "Month":
            query = datetime.today()
            query_result = ""
            total_value = 0
            # print(user_list[chat_id].keys())
            budget_value = user_list[chat_id].monthly_budget
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    if transaction["Date"].strftime("%m") == query.strftime("%m"):
                        query_result += "Category {} Date {} Value {:.2f} \n".format(
                            category,
                            transaction["Date"].strftime(dateFormat),
                            transaction["Value"],
                        )
                        total_value += transaction["Value"]
            total_spendings = (
                "Here are your total spendings for the Month {} \n".format(
                    datetime.today().strftime("%B")
                )
            )
            total_spendings += query_result
            total_spendings += "Total Value {:.2f}\n".format(total_value)
            total_spendings += "Budget for the month {}".format(str(budget_value))
            bot.send_message(chat_id, total_spendings)
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


@bot.message_handler(commands=["edit"])
def edit1(message):
    """
    Handles the command 'edit' and then displays a message explaining the format. The function 'edit_list2' is called next.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)

    try:
        if chat_id in list(user_list.keys()):
            msg = bot.reply_to(
                message,
                "Please enter the date (in mm/dd/yyyy format), category and "
                "value of the transaction you made (Eg: 01/03/2021,Transport,25)",
            )
            bot.register_next_step_handler(msg, edit_list2)

        else:
            bot.send_message(chat_id, "No data found")
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(
            message,
            "Processing Failed - \nError : Incorrect format - (Eg: 01/03/2021,Transport,25)",
        )


def edit_list2(message):
    """
    Parses the input from the user message, and finds the appropriate transaction. Asks the user whether they
    want to update the date, value, or category of the transaction, and then passes control to edit3 function

    :param message: the message sent of the transaction
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        info = message.text
        # date_format = r"^([0123]?\d)[\/](\d?\d)[\/](20\d+)"
        info = info.split(",")

        dateFormat = "%m/%d/%Y"
        info_date = user_list[chat_id].validate_date_format(info[0], dateFormat)
        info_category = info[1].strip()
        info_value = info[2].strip()
        if info_date is None:
            bot.reply_to(message, "The date is incorrect")
            return

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        choices = ["Date", "Category", "Cost"]
        for c in choices:
            markup.add(c)

        for transaction in user_list[chat_id].transactions[info_category]:
            if transaction["Date"].date() == info_date:
                if transaction["Value"] == float(info_value):
                    user_list[chat_id].store_edit_transaction(
                        transaction, info_category
                    )
                    choice = bot.reply_to(
                        message, "What do you want to update?", reply_markup=markup
                    )
                    bot.register_next_step_handler(choice, edit3)
                    break
        else:
            bot.reply_to(message, "Transaction not found")
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - Error: " + str(ex))


def edit3(message):
    """
    Receives the user's input corresponding to what they want to edit, and then transfers the execution to the
    function according to the choice.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    choice1 = message.text
    chat_id = str(message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for category in user_list[chat_id].spend_categories:
        markup.add(category)
    if choice1 == "Date":
        new_date = bot.reply_to(
            message, "Please enter the new date (in mm/dd/yyyy format)"
        )
        bot.register_next_step_handler(new_date, edit_date)

    if choice1 == "Category":
        new_cat = bot.reply_to(
            message, "Please select the new category", reply_markup=markup
        )
        bot.register_next_step_handler(new_cat, edit_cat)

    if choice1 == "Cost":
        new_cost = bot.reply_to(message, "Please type the new cost")
        bot.register_next_step_handler(new_cost, edit_cost)


def edit_date(message):
    """
    This function is called if the user chooses to edit the date of a transaction. This function receives the new
    date and updates the transaction.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    new_date = message.text
    chat_id = str(message.chat.id)
    user_date = datetime.strptime(new_date, "%m/%d/%Y")
    if user_date is None:
        bot.reply_to(message, "The date is incorrect")
        return
    updated_transaction = user_list[chat_id].edit_transaction_date(user_date)
    user_list[chat_id].save_user(chat_id)
    edit_message = (
        "Date is updated. Here is the new transaction. \n Date {}. Value {}. \n".format(
            updated_transaction["Date"].strftime("%m/%d/%Y %H:%M:%S"),
            format(updated_transaction["Value"], ".2f"),
        )
    )
    bot.reply_to(message, edit_message)


def edit_cat(message):
    """
    This function is called if the user chooses to edit the category of a transaction. This function receives the new
    category and updates the transaction.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    new_category = message.text.strip()
    updated_transaction = user_list[chat_id].edit_transaction_category(new_category)
    if updated_transaction:
        user_list[chat_id].save_user(chat_id)
        edit_message = "Category has been edited."
        bot.reply_to(message, edit_message)
    else:
        edit_message = "Category has not been edited successfully"
        bot.reply_to(message, edit_message)


def edit_cost(message):
    """
    This function is called if the user chooses to edit the amount of a transaction. This function receives the new
    amount and updates the transaction.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    new_cost = message.text
    chat_id = str(message.chat.id)
    new_cost = user_list[chat_id].validate_entered_amount(new_cost)
    if new_cost != 0:
        user_list[chat_id].save_user(chat_id)
        updated_transaction = user_list[chat_id].edit_transaction_value(new_cost)
        edit_message = "Value is updated. Here is the new transaction. \n Date {}. Value {}. \n".format(
            updated_transaction["Date"].strftime("%m/%d/%Y %H:%M:%S"),
            format(updated_transaction["Value"], ".2f"),
        )
        bot.reply_to(message, edit_message)

    else:
        bot.reply_to(message, "The cost is invalid")
        return


@bot.message_handler(content_types=["document"])
def handle_budget_document_csv(message):
    """
    This function is called if the user inputs a csv file that contains their budget in a csv format with column names
    date, description, and debit. The function reads the csv file and then for transactions that the bot does not
    know how to categorize, it sends a message to the user asking how they would like for that transaction to be categorized.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        file_info = bot.get_file(message.document.file_id)
        download_file = bot.download_file(file_info.file_path)
        with open("data/{}_spending.csv".format(chat_id), mode="wb") as f:
            f.write(download_file)
        unknown_spending = user_list[chat_id].read_budget_csv(
            "data/{}_spending.csv".format(chat_id), chat_id
        )
        for _, row in unknown_spending.iterrows():
            text = "How do you want to categorize the following transaction \n"
            text += "Date: {}. Description: {}. Debit: {}. \n".format(
                row["date"], row["description"], row["debit"]
            )
            buttons = telebot.types.InlineKeyboardMarkup(row_width=3)
            for category in user_list[chat_id].spend_categories:
                callback = "{},{},{},{}".format(
                    category, row["date"], row["debit"], row["description"]
                )
                buttons.add(
                    telebot.types.InlineKeyboardButton(category, callback_data=callback)
                )
            bot.send_message(chat_id, text, reply_markup=buttons)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - Error: " + str(ex))


def is_csv_callback(query):
    """
    Callback to identify if the button pressed was from the csv function

    :param query: the button pressed
    :return: if the button pressed relates to the csv
    """
    return "," in query.data


@bot.callback_query_handler(func=is_csv_callback)
def csv_callback(call):
    """
    This function is used to handle the callback with the data received from the user pressing a category option
    for the transactions that the bot read from the csv file but did not know how to categorize.The callback object
    contains the category the user choose for that particular transaction.

    :param call: telegram.CallbackQuery representing the callback object
    :type: object
    :return: None
    """
    try:
        data = call.data.split(",")
        category = data[0]
        date = datetime.strptime(data[1], "%m/%d/%y")
        debit = float(data[2])
        description = data[3]
        chat_id = str(call.from_user.id)
        user_list[chat_id].create_rules_and_add_unknown_spending(
            category, description, date, debit, chat_id
        )
        bot.delete_message(
            chat_id=call.from_user.id, message_id=call.message.message_id
        )
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.send_message(call.from_user.id, "Processing Failed - Error: " + str(ex))


@bot.message_handler(commands=["categoryAdd"])
def category_add(message):
    """
    Handles the command 'categoryAdd' and then displays a message prompting the user to enter the category name.
    The function 'receive_new_category' is called next.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """

    try:
        chat_id = str(message.chat.id)
        option.pop(chat_id, None)
        if chat_id not in user_list.keys():
            user_list[chat_id] = User(chat_id)
        category = bot.reply_to(message, "Enter category name")
        bot.register_next_step_handler(category, receive_new_category)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Oh no. " + str(ex))


def receive_new_category(message):
    """
    This function receives the category name that user inputs and then calls user.add_category which appends the category to the existing category list.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        category = message.text.strip()
        chat_id = str(message.chat.id)
        if category == "":  # category cannot be empty
            raise Exception("Category name cannot be empty")
        if category in user_list[chat_id].transactions:
            raise Exception("Category already exists!")
        user_list[chat_id].add_category(category, chat_id)
        bot.send_message(
            chat_id, "{} has been added as a new category".format(category)
        )
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Oh no. " + str(ex))


@bot.message_handler(commands=["categoryList"])
def category_list(message):
    """
    Handles the command 'categoryList'. Lists all categories.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        option.pop(chat_id, None)
        if chat_id not in user_list.keys():
            user_list[chat_id] = User(chat_id)
        chat_id = str(message.chat.id)
        if len(user_list[chat_id].transactions.keys()) == 0:
            raise Exception("Sorry! No categories found!")
        category_list_str = "Here is your category list : \n"
        for index, category in enumerate(user_list[chat_id].transactions.keys()):
            category_list_str += "{}. {}".format(index + 1, category + "\n")
        bot.send_message(chat_id, category_list_str)

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


@bot.message_handler(commands=["categoryDelete"])
def category_delete(message):
    """
    Handles the command 'categoryDelete'. Lists all categories from which the user can choose a category to delete.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        option.pop(chat_id, None)
        if chat_id not in user_list.keys():
            user_list[chat_id] = User(chat_id)
        spend_categories = user_list[chat_id].spend_categories
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for c in spend_categories:
            markup.add(c)
        msg = bot.reply_to(message, "Select Category", reply_markup=markup)
        bot.register_next_step_handler(msg, receive_delete_category)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - \nError : " + str(ex))


def receive_delete_category(message):
    """
    Checks whether the selected category can be deleted and calls user.delete_category if the category can be deleted.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    try:
        chat_id = str(message.chat.id)
        category = message.text.strip()
        if category not in user_list[chat_id].transactions:
            raise Exception("Oops! Category does not exist!")
        if len(user_list[chat_id].transactions[category]) != 0:
            raise Exception(
                "Sorry! This category has transactions. Delete those transactions to proceed."
            )
        user_list[chat_id].delete_category(category, chat_id)
        bot.reply_to(message, "{} has been removed from category list".format(category))
    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


@bot.message_handler(commands=["delete"])
def command_delete(message):
    """
    Handles the 'delete' command. The user is then given 3 options, 'day', 'month' and 'All" from which they can choose.
    An error message is displayed if there is no transaction history. If there is transaction history, the execution is
    passed to the function 'process_delete_argument'.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    dateFormat = "%m/%d/%Y"
    monthFormat = "%m/%Y"
    chat_id = str(message.chat.id)
    try:
        if (
                chat_id in user_list
                and user_list[chat_id].get_number_of_transactions() != 0
        ):
            curr_day = datetime.now()
            prompt = "Enter the day, month, or All\n"
            prompt += f"\n\tExample day: {curr_day.strftime(dateFormat)}\n"
            prompt += f"\n\tExample month: {curr_day.strftime(monthFormat)}"
            reply_message = bot.reply_to(message, prompt)
            bot.register_next_step_handler(reply_message, process_delete_argument)
        else:
            delete_history_text = (
                "No records to be deleted. Start adding your expenses to keep track of your "
                "spendings! "
            )
            bot.send_message(chat_id, delete_history_text)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - \nError : " + str(ex))


def process_delete_argument(message):
    """
    This function receives the choice that user inputs for delete and asks for a confirmation. 'handle_confirmation'
    is called next.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    dateFormat = "%m/%d/%Y"
    monthFormat = "%m/%Y"
    text = message.text
    chat_id = str(message.chat.id)

    date = None
    is_month = False
    if text.lower() == "all":
        date = "all"
    else:
        # try and parse as Date-Month-Year
        if user_list[chat_id].validate_date_format(text, dateFormat) is not None:
            date = user_list[chat_id].validate_date_format(text, dateFormat)
        # try and parse as Month-Year
        elif user_list[chat_id].validate_date_format(text, monthFormat) is not None:
            date = user_list[chat_id].validate_date_format(text, monthFormat)
            is_month = True

    if date is None:
        # if none of the formats worked
        bot.reply_to(message, "Error parsing date")
    else:
        # get the records either by given day, month, or all records
        records_to_delete = user_list[chat_id].get_records_by_date(date, is_month)
        # if none of the records match that day
        if len(records_to_delete) == 0:
            bot.reply_to(message, f"No transactions within {text}")
            return
        response_str = "Confirm records to delete\n"
        response_str += user_list[chat_id].display_transaction(records_to_delete)

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes")
        markup.add("No")
        response_str += "\nReply Yes or No"
        response = bot.reply_to(message, response_str, reply_markup=markup)
        bot.register_next_step_handler(response, handle_confirmation, records_to_delete)


def handle_confirmation(message, records_to_delete):
    """
    Deletes the transactions in the previously chosen time period if the user chooses 'yes'.

    :param message: telebot.types.Message object representing the message object
    :param records_to_delete: the records to remove
    :type: object
    :return: None
    """

    chat_id = str(message.chat.id)
    if message.text.lower() == "yes":
        user_list[chat_id].deleteHistory(records_to_delete)
        user_list[chat_id].save_user(chat_id)
        bot.send_message(message.chat.id, "Successfully deleted records")
    else:
        bot.send_message(message.chat.id, "No records deleted")


def get_calendar_buttons(user):
    """
    Gets the calendar buttons for each numeric day

    :param user: the user to add to
    :return: the rows of calendar buttons
    """
    kb = types.InlineKeyboardMarkup()

    # creating the headers
    header = create_header(user)
    kb.row(*header)
    weekdays = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    rows = [types.InlineKeyboardButton(w, callback_data="none") for w in weekdays]
    kb.row(*rows)

    # create the days
    m = monthrange(user.curr_date.year, user.curr_date.month)
    # for each day in the total days
    # for the first day, figure out how many ' ' to append
    row = []
    if m[0] != 6:
        row = [
            types.InlineKeyboardButton(" ", callback_data="none")
            for _ in range(m[0] + 1)
        ]
    for day in range(1, m[1] + 1):
        # if it is on a sunday, start a new row
        if user.curr_date.replace(day=day).weekday() == 6:
            kb.row(*row)
            row = []
        row.append(
            types.InlineKeyboardButton(
                day,
                callback_data="{},{},{}".format(
                    user.curr_date.year, user.curr_date.month, day
                ),
            )
        )
    # finish out the last row
    if len(row) != 7:
        for _ in range(7 - len(row)):
            row.append(types.InlineKeyboardButton(" ", callback_data="none"))

    kb.row(*row)
    return kb


@bot.message_handler(commands=["chart"])
def get_chart(message):
    """
    Handles the chart command. When the user runs this command the bot will create a piechart
    of all the transactions and their categories and post that to the chat

    :param message:
    :return: None
    """
    # Original Code

    # chat_id = str(message.chat.id)
    # chart_file = user_list[chat_id].create_chart(chat_id)
    # with open(chart_file, "rb") as f:
    #     bot.send_photo(chat_id, f)
    # bot.send_photo(chat_id, chart_file)

    # Modified Code
    chat_id = str(message.chat.id)
    chart_file = user_list[chat_id].create_chart(chat_id)
    for cf in chart_file:
        with open(cf, "rb") as f:
            bot.send_photo(chat_id, f)
            # bot.send_photo(chat_id, cf)


def create_header(user):
    """
    Creates the header for the calender

    :param user: the user
    :return: the header row
    """
    # get the month name
    row = [
        (
            types.InlineKeyboardButton(
                user.curr_date.strftime("%B"), callback_data="none"
            )
        )
    ]
    if user.curr_date > user.min_date:
        # if we should be able to go back a month
        row.append(types.InlineKeyboardButton("<", callback_data="prev"))
    else:
        # append a blank
        row.append(types.InlineKeyboardButton(" ", callback_data="none"))

    if user.curr_date < user.max_date:
        # if we should be able to go forward
        row.append(types.InlineKeyboardButton(">", callback_data="next"))
    else:
        # append a blank
        row.append(types.InlineKeyboardButton(" ", callback_data="none"))
    return row


def handler_callback(callback, user):
    """
    A method for handling callbacks

    :param user: user object
    :param callback: callback from telebot.types.CallbackQuery
    :return: datetime.date object if some date was picked else None
    """

    if callback == "prev" and user.curr_date.replace(day=1) >= user.min_date.replace(
            day=1
    ):
        user.curr_date = user.curr_date.replace(month=user.curr_date.month - 1)
        return None
    if callback == "next" and user.curr_date.replace(day=1) <= user.max_date.replace(
            day=1
    ):
        user.curr_date = user.curr_date.replace(month=user.curr_date.month + 1)
        return None

    if callback != "none":
        entered_date = datetime.strptime(callback, "%Y,%m,%d")
        if user.min_date <= entered_date <= user.max_date:
            return entered_date
        return -1


def get_users():
    """
    Reads data and returns user list as a Dict

    :return: users
    :rtype: dict
    """

    data_dir = "data"
    users = {}
    for file in os.listdir(data_dir):
        if file.endswith(".pickle"):
            u = re.match(r"(.+)\.pickle", file)
            if u:
                u = u.group(1)
                abspath = pathlib.Path("{0}/{1}".format(data_dir, file)).absolute()
                with open(abspath, "rb") as f:
                    users[u] = pickle.load(f)
    return users


@bot.message_handler(commands=["displayDifferentCurrency"])
def command_display_currency(message):
    """
    Handles the command 'display'. If the user has no transaction history, a message is displayed. If there is
    transaction history, user is given choices of time periods to choose from. The function 'display_total' is called
    next.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    chat_id = str(message.chat.id)
    if chat_id not in user_list or user_list[chat_id].get_number_of_transactions() == 0:
        bot.send_message(
            chat_id, "Oops! Looks like you do not have any spending records!"
        )
    else:
        try:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.row_width = 2
            for mode in user_list[chat_id].spend_display_option:
                markup.add(mode)
            msg = bot.reply_to(
                message,
                "Please select a category to see the total expense",
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, display_total_currency)

        except Exception as ex:
            print("Exception occurred : ")
            logger.error(str(ex), exc_info=True)
            bot.reply_to(message, "Oops! - \nError : " + str(ex))


def display_total_currency(message):
    """
    Receives the input time period and displays the transaction summary for the corresponding time period.

    :param message: telebot.types.Message object representing the message object
    :type: object
    :return: None
    """
    dateFormat = "%m/%d/%Y"
    try:
        chat_id = str(message.chat.id)
        day_week_month = message.text

        if day_week_month not in user_list[chat_id].spend_display_option:
            raise Exception(
                'Sorry I can\'t show spendings for "{}"!'.format(day_week_month)
            )

        if len(user_list[chat_id].transactions) == 0:
            raise Exception("Oops! Looks like you do not have any spending records!")

        bot.send_message(chat_id, "Hold on! Calculating...")

        if day_week_month == "Day":
            query = datetime.today()
            query_result = ""
            total_value = 0
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    if transaction["Date"].strftime("%d") == query.strftime("%d"):
                        query_result += "Category {} Date {} Value {:.2f} \n".format(
                            category,
                            transaction["Date"].strftime(dateFormat),
                            transaction["Value"],
                        )
                        total_value += transaction["Value"]
            total_spendings = "Here are your total spendings for the date {} \n".format(
                datetime.today().strftime("%m/%d/%Y")
            )
            total_spendings += query_result
            total_spendings += "Total Value {:.2f}".format(total_value)
            bot.send_message(chat_id, total_spendings)
        elif day_week_month == "Month":
            query = datetime.today()
            query_result = ""
            total_value = 0
            # print(user_list[chat_id].keys())
            budget_value = user_list[chat_id].monthly_budget
            for category in user_list[chat_id].transactions.keys():
                for transaction in user_list[chat_id].transactions[category]:
                    if transaction["Date"].strftime("%m") == query.strftime("%m"):
                        query_result += "Category {} Date {} Value {:.2f} \n".format(
                            category,
                            transaction["Date"].strftime(dateFormat),
                            transaction["Value"],
                        )
                        total_value += transaction["Value"]
            total_spendings = (
                "Here are your total spendings for the Month {} \n".format(
                    datetime.today().strftime("%B")
                )
            )
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.row_width = 2
            choices = ["INR", "EUR", "CHF"]
            for c in choices:
                markup.add(c)

            total_spendings += query_result
            total_spendings += "Total Value {:.2f}\n".format(total_value)
            total_spendings += "Budget for the month {}".format(str(budget_value))
            global completeSpendings  # pylint: disable=global-statement
            completeSpendings = total_value
            choice = bot.reply_to(
                message, "Which currency to you want to covert to?", reply_markup=markup
            )
            bot.register_next_step_handler(choice, display_total_currency2)
            # bot.send_message(chat_id, total_spendings)

    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, str(ex))


def display_total_currency2(message):
    try:
        # chat_id = str(message.chat.id)
        selection = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2

        if selection == "INR":
            completeExpenses = round(completeSpendings * DOLLARS_TO_RUPEES,2)
            completeExpensesMessage = (
                    "The total expenses in INR is Rs. " + str(completeExpenses)
            )
            bot.reply_to(message, completeExpensesMessage)
        if selection == "EUR":
            completeExpenses = round(completeSpendings * DOLLARS_TO_EUROS,2)
            completeExpensesMessage = (
                    "The total expenses in EUR is " + str(completeExpenses) + " EUR"
            )
            bot.reply_to(message, completeExpensesMessage)
        if selection == "CHF":
            completeExpenses = round(completeSpendings * DOLLARS_TO_SWISS_FRANC,2)
            completeExpensesMessage = (
                    "The total expenses in Swiss Franc is " + str(completeExpenses) + " CHF"
            )
            bot.reply_to(message, completeExpensesMessage)


    except Exception as ex:
        print("Exception occurred : ")
        logger.error(str(ex), exc_info=True)
        bot.reply_to(message, "Processing Failed - Error: " + str(ex))


if __name__ == "__main__":
    try:
        user_list = get_users()
        bot.polling(none_stop=True)
    except Exception as e:
        # Connection will be timed out with the set time interval - 3
        time.sleep(3)
        print("Exception occurred while processing : ")
        logger.error(str(e), exc_info=True)
