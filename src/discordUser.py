"""
File: DiscordUser.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: File contains functions that stores and retrieves data from the .pickle file and also handles validations.

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
import pathlib
import pickle
import re
from datetime import datetime
import matplotlib.pyplot as plt


class User:
    """
    A class that represents a user's financial data and transactions. It functions that stores and retrieves data from the .pickle file and 
    handles validations

    Attributes:
        spend_categories (list): List of spend categories.
        spend_display_option (list): List of display options for spend categories.
        transactions (dict): Dictionary to store user's financial transactions.
        edit_transactions (dict): Dictionary to store transactions being edited.
        edit_category (str): The category of the transaction being edited.
        monthly_budget (float): User's monthly budget.
        rules (dict): Dictionary to store user-defined rules for categories.

    Methods:
        - save_user(userid): Saves user data to a .pickle file.
        - validate_entered_amount(amount_entered): Validates and rounds entered amounts.
        - add_transaction(date, category, value, userid): Stores a transaction to file.
        - store_edit_transaction(existing_transaction, edit_category): Assigns a transaction and category to be edited.
        - edit_transaction_date(new_date): Returns the edited transaction with the new date.
        - edit_transaction_category(new_category): Updates the edited transaction with the new category.
        - edit_transaction_value(new_value): Returns the edited transaction with the new value.
        - deleteHistory(records=None): Deletes transactions.
        - validate_date_format(text, date_format): Converts an inputted date to the specified date format.
        - get_records_by_date(date, is_month): Returns records that match the filter by date.
        - display_transaction(transaction): Converts a dictionary of transactions into a user-readable string.
        - get_number_of_transactions(): Returns the total number of transactions across all categories.
        - add_monthly_budget(amount, userid): Edits the user's monthly budget.
        - monthly_total(): Calculates the total expenditure for the current month.
        - create_chart(userid, start_date=None, end_date=None): Creates matplotlib charts of expenditure transactions.
    """    
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

        for category in self.spend_categories:
            self.transactions[category] = []
        self.save_user(userid)

    def save_user(self, userid):
        """
        Save user data to a pickle file.

        This function takes a user ID and attempts to save the user data to a pickle
        file. It constructs the file path based on the provided user ID and the
        'discordData' directory. The user data is serialized using the pickle module
        and saved to the specified file.

        Parameters:
        -  userid (string): The unique identifier for the user whose data is being saved.

        Raises:
        - Exception: If an error occurs during the data saving process, an exception
                   is raised and an error message is printed.

        Return: 
        - None
        """
        try:
            data_dir = "discordData"
            abspath = pathlib.Path("{0}/{1}.pickle".format(data_dir, userid)).absolute()
            with open(abspath, "wb") as f:
                pickle.dump(self, f)

        except Exception as e: print("exception occurred:"+str(e))
            

    def validate_entered_amount(self, amount_entered):
        """
        Validates and rounds an entered amount.

        This function validates an entered amount to ensure it is greater than zero and
        rounds it to 2 decimal places.

        Parameters:
        - amount_entered (float): The entered amount to be validated and rounded.

        Return (float): 
        - The rounded amount if valid, else 0.
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
        Stores a transaction in a user's data file.

        This function records a transaction with the provided date, category, and value
        in the user's data file, identified by the 'userid'.

        Parameters:
        - date (string): The date of the transaction 
        - category (string): The category of the transaction.
        - value (string): The amount of the transaction.
        - userid (string): The unique identifier for the user and the filename.
        
        Returns:
        - None
        """
        try:
            self.transactions[category].append({"Date": date, "Value": value})
            self.save_user(userid)

        except Exception as e: print("exception occurred:"+str(e))

    def store_edit_transaction(self, existing_transaction, edit_category):
        """
        Assigns a transaction and its category for editing.

        This function sets the transaction and category that the user has chosen to edit.

        Parameters:
        - existing_transaction (string): The transaction to be edited.
        - edit_category (string): The existing category of the transaction.

        Returns: 
        - None
        """
        try:
            self.edit_transactions = existing_transaction
            self.edit_category = edit_category

        except Exception as e: print("exception occurred:"+str(e))

    def edit_transaction_date(self, new_date):
        """
        Returns the transaction with the new date.

        This function returns the edited transaction with the specified new date.

        Paramters: 
        - new_date (string): the new date of the transaction.
        
        Returns:
        - transactions dict (dict): A dictionary representing the edited transaction.
        """
        transaction = None
        for transaction in self.transactions[self.edit_category]:
            if transaction == self.edit_transactions:
                transaction["Date"] = new_date
                break
        return transaction

    def edit_transaction_category(self, new_category):
        """
        Updates the category of the edited transaction.

        This function modifies the category of the previously edited transaction to the
        specified new category.

        Parameters:
        - new_category (string): the new category of the transaction.

        Returns (bool): 
        - True if the category update is successful.
        """
        self.transactions[self.edit_category].remove(self.edit_transactions)
        self.transactions[new_category].append(self.edit_transactions)
        return True

    def edit_transaction_value(self, new_value):
        """
        Updates the value of the edited transaction and returns the modified transaction.

        This function modifies the value of the previously edited transaction to the
        specified new value and returns the modified transaction.

        Parameters:
        - new_value(string): the new value of the transaction.

        Returns:
        - transactions (dict): A dictionary representing the edited transaction.
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
                    except Exception as e: print("exception occurred:"+str(e))
        else:
            self.transactions = {}
            for category in self.spend_categories:
                self.transactions[category] = []

    def validate_date_format(self, text, date_format):
        """
        Deletes specified transaction records.

        This function deletes transaction records from the user's history based on the provided list of records.

        Parameters:
        - text(string): has the date which is to be converted
        - date_format(string): has the format to which the conversion should be done

        Return:
        - date (datetime.dateime): contains the formatted date
        """
        date = None

        # try and parse as Month-Day-Year
        try:
            date = datetime.strptime(text, date_format).date()
            
        except Exception as e: print(e)
        return date

    def get_records_by_date(self, date: datetime.date, is_month: bool):
        """
        Retrieve transaction records that match a given date or month.

        This function filters the user's transaction records based on the provided date.
        If `is_month` is True, it matches the year and month, but not the day.

        Parameters:
        - date (datetime.date): The date for filtering records
        - is_month(bool): If True, filter records for the entire month.

        Returns (dictionary): 
        A dict of matched records categorized by spend category.
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
        Convert a dictionary of transactions into a user-readable string.

        This function takes a dictionary where each key is a spend category, and the
        corresponding value is a list of transaction records for that category. It
        then converts this data into a user-readable string format.

        Parameters:
        - transaction (dict): A dictionary of transaction records organized by category
        
        Returns (string):
        - final_str, which is the transactions stringifies
        """
        final_str = ""

        for category in transaction:
            for record in transaction[category]:
                final_str += (
                    f'{category}, {record["Date"].date()}, {record["Value"]:}\n'
                )

        return final_str

    def get_number_of_transactions(self):
        """
        Helper function to get the total number of transactions across
        all categories

        Parameters:
        - None

        Return (int):
        - number of transactions
        """
        total = 0
        for category in self.transactions:
            total += len(self.transactions[category])
        return total

    def add_monthly_budget(self, amount, userid):
        """
        Set or update the monthly budget for the current user.

        This function allows setting or updating the monthly budget for a user with the
        specified 'userid'.

        Parameters:
        - amount (float): The budget amount to be set or updated.
        - userid (str): The unique identifier for the user.

        Returns:
        - None
        """
        try:
            if amount != 0:
                self.monthly_budget = amount
                self.save_user(userid)

        except Exception as e: print("exception occurred:"+str(e))

    def monthly_total(self):
        """
        Calculate the total expenditure for the current month.

        This function calculates the total expenditure for the current month based on
        the user's transaction records.

        Parameters:
        - None

        Return:
        - total_value (float) - The total expenditure for the current month, rounded to 2 decimal places.
        """
        date = datetime.today()
        total_value = 0
        for category in self.spend_categories:
            for transaction in self.transactions[category]:
                if transaction["Date"].strftime("%m") == date.strftime("%m"):
                    total_value += transaction["Value"]
        return total_value

    def create_chart(self, userid, start_date=None, end_date=None):
        """
        Generate visualizations of transaction data, including a pie chart and a bar graph.

        This function creates visualizations using Matplotlib to represent transaction data. It generates
        a pie chart and a bar graph, where each segment or bar represents a spending category and its total
        expenditure.

        Parameter:
        - userid (str): The unique identifier for the user
        - start_date (datetime.date or None): Optional start date to filter transactions (inclusion criterion).
        - end_date (datetime.date or None): Optional end date to filter transactions (inclusion criterion).

        Returns (str):
        - A list of file paths to the generated images.
        """
        labels = []
        totals = []
        charts = []
        for category in self.spend_categories:
            total = 0
            for transaction in self.transactions[category]:
                transaction_date = transaction["Date"]
                if start_date and transaction_date < start_date: continue
                if end_date and transaction_date > end_date: continue
                total += int(transaction["Value"])
            if total != 0:
                labels.append(category)
                totals.append(total)

        # Pie Chart
        plt.clf()
        plt.pie(totals, labels=labels)
        plt.title("Your Expenditure Report")
        plt.savefig("discordData/{}_pie_chart.png".format(userid)) # Ensure that the file name is unique
        charts.append("discordData/{}_pie_chart.png".format(userid)) # Ensure that the file name is unique

        # Bar Graph
        plt.clf()
        plt.switch_backend("Agg")
        plt.title("Your Expenditure Report")
        plt.bar(labels, totals)
        plt.xlabel('Categories')
        plt.ylabel('Expenditure')
        plt.title("Your Expenditure Report")
        plt.savefig("discordData/{}_bar_chart.png".format(userid)) # Ensure that the file name is unique
        charts.append("discordData/{}_bar_chart.png".format(userid)) # Ensure that the file name is unique

        # Add more visualizations here. Maintain the above format while adding more visualizations. 

        return charts
