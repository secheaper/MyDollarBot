"""
File contains functions that stores and retrieves data from the .pickle file and also handles validations
"""
import logging
import pathlib
import pickle
import re
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger()


class User:
    def __init__(self, userid):
        self.spend_categories = [
            "Food",
            "Groceries",
            "Utilities",
            "Transport",
            "Shopping",
            "Miscellaneous",
        ]
        self.spend_display_option = ["Day", "Month"]
        self.transactions = {}
        self.edit_transactions = {}
        self.edit_category = {}
        self.monthly_budget = 0
        self.monthly_savings = 0
        self.rules = {}

        # for the calendar widget
        self.max_date = datetime.today() + timedelta(days=1)
        self.curr_date = datetime.today()
        self.min_date = datetime.today()
        self.min_date = self.min_date.replace(year=self.min_date.year - 1)

        for category in self.spend_categories:
            self.transactions[category] = []
            self.rules[category] = []
        self.save_user(userid)

    def save_user(self, userid):
        """
        Saves data to .pickle file

        :param userid: userid string which is also the file name
        :type: string
        :return: None
        """

        try:
            data_dir = "data"
            abspath = pathlib.Path("{0}/{1}.pickle".format(data_dir, userid)).absolute()
            with open(abspath, "wb") as f:
                pickle.dump(self, f)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def validate_entered_amount(self, amount_entered):
        """
        Validates that an entered amount is greater than zero and also rounds it to 2 decimal places.

        :param amount_entered: entered amount
        :type: float
        :return: rounded amount if valid, else 0.
        :rtype: float
        """
        if 0 < len(amount_entered) <= 15:
            if amount_entered.isdigit:
                if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                    amount = round(float(amount_entered), 2)
                    if amount > 0:
                        return amount
        return 0

    def add_transaction(self, date, category, value, userid):
        """
        Stores the transaction to file.

        :param date: date string of the transaction
        :type: string
        :param category: category of the transaction
        :type: string
        :param value: amount of the transaction
        :type: string
        :param userid: userid string which is also the file name
        :type: string
        :return: None
        """
        try:
            self.transactions[category].append({"Date": date, "Value": value})
            self.save_user(userid)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def store_edit_transaction(self, existing_transaction, edit_category):
        """
        Assigns the transaction and category to be edited.

        :param existing_transaction: the transaction which the user chose to edit
        :type: string
        :param edit_category: the existing category of the transaction
        :type: string
        :return: None
        """
        try:
            self.edit_transactions = existing_transaction
            self.edit_category = edit_category

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def edit_transaction_date(self, new_date):
        """
        Returns the edited transaction with the new date.

        :param new_date: the new date of the transaction.
        :type: string
        :return: transactions dict
        :rtype: dict
        """
        transaction = None
        for transaction in self.transactions[self.edit_category]:
            if transaction == self.edit_transactions:
                transaction["Date"] = new_date
                break
        return transaction

    def edit_transaction_category(self, new_category):
        """
        Updates the edited transaction with the new category.

        :param new_category: the new category of the transaction.
        :type: string
        :return: True
        :rtype: bool
        """

        self.transactions[self.edit_category].remove(self.edit_transactions)
        self.transactions[new_category].append(self.edit_transactions)
        return True

    def edit_transaction_value(self, new_value):
        """
        Returns the edited transaction with the new value.

        :param new_value: the new value of the transaction.
        :type: string
        :return: transactions dict
        :rtype: dict
        """
        transaction = None
        for transaction in self.transactions[self.edit_category]:
            if transaction == self.edit_transactions:
                transaction["Value"] = new_value
                break
        return transaction

    def deleteHistory(self, records=None):
        """
        Deletes transactions

        :param records: list of records to delete.
        :type: array
        :return: None
        """

        # if there are specific records to delete
        # and it is not all records from the user
        if records is not None and self.transactions != records:
            # delete only the records specified
            for category in records:
                for record in records[category]:
                    try:
                        self.transactions[category].remove(record)
                    except Exception as e:
                        print("Exception occurred : ")
                        logger.error(str(e), exc_info=True)
        else:
            self.transactions = {}
            for category in self.spend_categories:
                self.transactions[category] = []

    def validate_date_format(self, text, date_format):
        """
        Converts the inputted date to the inputted date format

        :param text has the date which is to be converted
        :type: string
        :param date_format has the format to which the conversion should be done
        :type: string
        :return: date, contains the formatted date
        :rtype: datetime.dateime
        """
        date = None
        # try and parse as Month-Day-Year
        try:
            date = datetime.strptime(text, date_format).date()
        except ValueError:
            pass
        return date

    def get_records_by_date(self, date: datetime.date, is_month: bool):
        """
        Given a date and chat_id returns all records that match the filter
        If is_month is true, only matches year and month, not day

        :param date: date for filtering records
        :type: datetime.date
        :param is_month: this parameter is true if records for a month are taken
        :type: bool
        :return: matched_dates which is the array of records for that day or month
        :rtype: array
        """
        user_history = self.transactions
        if date == "all":
            return user_history
        # else filter by date
        matched_dates = {}
        for category in self.spend_categories:
            matched_dates[category] = []
        for category in user_history:
            for record in user_history[category]:
                record_date = record["Date"]
                # format it to date and time, then only get the day,month,year
                record_date = record_date.date()
                if is_month:
                    # strip the date
                    record_date = record_date.replace(day=1)
                    date = date.replace(day=1)
                # checks if the records are equal/matching
                if record_date == date:
                    matched_dates[category].append(record)
        return matched_dates

    def display_transaction(self, transaction):
        """
        Helper function to turn the dictionary into a user-readable string

        :param transaction: dictionary of category, and each value is a dictionary of transactions of that category
        :return: final_str, which is the transactions stringifies
        :rtype: string
        """
        final_str = ""

        for category in transaction:
            for record in transaction[category]:
                final_str += (
                    f'{category}, {record["Date"].date()}, {record["Value"]:.2f}\n'
                )

        return final_str

    def get_number_of_transactions(self):
        """
        Helper function to get the total number of transactions across
        all categories

        :return: number of transactions
        :rtype: int
        """
        total = 0
        for category in self.transactions:
            total += len(self.transactions[category])
        return total

    def add_monthly_budget(self, amount, userid):
        """
        Given amount and userid, edit the budget of the current user

        :param amount: budget amount
        :param userid:
        :return: None
        """
        try:
            if amount != 0:
                self.monthly_budget = amount
                self.save_user(userid)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def add_monthly_savings(self, amount, userid):
        """
        Given amount and userid, edit the budget of the current user

        :param amount: budget amount
        :param userid:
        :return: None
        """
        try:
            if amount != 0:
                self.monthly_savings = amount
                self.save_user(userid)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def monthly_total(self):
        """
        Calculates total expenditure for the current month

        :return: total_value - rounded amount if valid, else 0.
        :rtype: float
        """
        date = datetime.today()
        total_value = 0
        for category in self.spend_categories:
            for transaction in self.transactions[category]:
                if transaction["Date"].strftime("%m") == date.strftime("%m"):
                    total_value += transaction["Value"]
        return total_value

    def read_budget_csv(self, file, userid):
        """
        This function reads the csv file passed to the bot by the user into a Pandas Dataframe.
        It goes through each transaction, and checks if it knows how to categorize that transaction. If it does,
        it will add the transaction to the user history.

        :param file: csv file sent to the telegram bot
        :param userid: chat id of the conversation
        :return: df pandas dataframe that contains all of the transactions that the bot could not categorize by itself
        :rtype: Dataframe
        """
        df = pd.read_csv(file)
        df.columns = df.columns.str.lower()
        df = df[["date", "description", "debit"]]
        df = df.dropna()
        df = df.loc[df["debit"] != 0]
        for index, row in df.iterrows():
            for category in self.rules.keys():
                if row["description"] in self.rules[category]:
                    date = datetime.strptime(row["date"], "%m/%d/%y")
                    value = float(row["debit"])
                    self.add_transaction(date, category, value, userid)
                    df = df.drop(index)
        return df

    def create_rules_and_add_unknown_spending(
        self, category, description, date, value, userid
    ):
        """
        This function is used to remember how an user categorized a certain transaction, so that the next time
        the bot sees the transaction the bot will be able to categorize it automatically.

        :param category: category of the transaction
        :type: string
        :param description:
        :type: string
        :param date:
        :type: Datetime object
        :param value:
        :type: float
        :param userid:
        :type: string
        :return: None
        """
        self.rules[category].append(description)
        self.add_transaction(date, category, value, userid)
        self.save_user(userid)

    def create_chart(self, userid):
        """
        This is used to create the matplotlib piechart of all the transactions and
        their categories. If a category does not have any transactions, then it is not
        included in the piechart

        :param userid:
        :return: filepath to the image created by matplotlib
        """
        labels = []
        totals = []
        charts = []
        for category in self.spend_categories:
            total = 0
            for transaction in self.transactions[category]:
                total = total + transaction["Value"]
            if total != 0:
                labels.append(category)
                totals.append(total)

        # Pie Chart
        plt.clf()
        plt.pie(totals, labels=labels)
        plt.title("Your Expenditure Report")
        plt.savefig("data/{}_pie_chart.png".format(userid)) # Ensure that the file name is unique
        charts.append("data/{}_pie_chart.png".format(userid)) # Ensure that the file name is unique

        # Bar Graph
        plt.clf()
        plt.switch_backend("Agg")
        plt.title("Your Expenditure Report")
        plt.bar(labels, totals)
        plt.xlabel('Categories')
        plt.ylabel('Expenditure')
        plt.title("Your Expenditure Report")
        plt.savefig("data/{}_bar_chart.png".format(userid)) # Ensure that the file name is unique
        charts.append("data/{}_bar_chart.png".format(userid)) # Ensure that the file name is unique

        # Add more visualizations here. Maintain the above format while adding more visualizations. 

        return charts

    def add_category(self, new_category, userid):
        """
        Stores the category to category list.

        :param new_category: name of the new category
        :type: string
        :param userid: userid string which is also the file name
        :type: string
        :return: None
        """
        try:
            self.spend_categories.append(new_category)
            self.transactions[new_category] = []
            self.rules[new_category] = []
            self.save_user(userid)

        except Exception as e:
            logger.error(str(e), exc_info=True)

    def delete_category(self, category, userid):
        """
        Removes the category from category list.

        :param category: name of the category to be removed
        :type: string
        :param userid: userid string which is also the file name
        :type: string
        :return: None
        """
        try:
            self.spend_categories.remove(category)
            self.transactions.pop(category, None)
            self.rules.pop(category, None)
            self.save_user(userid)

        except Exception as e:
            logger.error(str(e), exc_info=True)
