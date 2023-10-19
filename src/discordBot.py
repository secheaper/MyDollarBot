"""
File: DiscordBot.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: File contains Discord bot message handlers and their associated functions.

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

import asyncio
import discord
from discord.ext import commands
from discordUser import User
from discord.ui import Select, View
import os
import pathlib
import pickle
import re
from datetime import datetime
from tabulate import tabulate

BOT_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

bot = commands.Bot(command_prefix="#", intents=discord.Intents.all())
user_list = {}

@bot.event
async def on_ready():
    """
    An event handler for the "on_ready" event.
    This function is called when the bot has successfully connected to the Discord server and is ready to operate. It sends a welcome message to a specific channel and then calls the "menu" 
    function to display a menu, likely for user interaction.

    Parameters: 
    - None

    Returns: 
    - None
    """
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send("Hello ! Welcome to FinBot - a simple solution to track your expenses! \n\n")
    await menu(channel)

@bot.command()
async def menu(ctx):
    """
    Handles the 'menu' command to display a list of available commands and their descriptions in an embed window.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.

    Returns:
    - None
    """
    em = discord.Embed(title="FinBot", description="Here is a list of available commands, please enter a command of your choice with a prefix '#' so that I can assist you further.\n ",color = discord.Color.teal())
    em.add_field(name="**#menu**", value="Displays all commands and their descriptions", inline=False)
    em.add_field(name="**#add**", value="Record/Add a new spending", inline=False)
    em.add_field(name="**#display**", value="Show sum of expenditure for the current day/month", inline=False)
    em.add_field(name="**#history**", value="Display spending history", inline=False)
    em.add_field(name="**#delete**", value="Clear/Erase all your records", inline=False)
    em.add_field(name="**#edit**", value="Edit/Change spending details", inline=False)
    em.add_field(name="**#budget**", value="Set budget for the month", inline=False)
    em.add_field(name="**#chart**", value="See your expenditure in different charts", inline=False)
    
    await ctx.send(embed=em)

@bot.command()
async def display(ctx):
    """
    Handles the command 'display'. If the user has no transaction history, a message is displayed. If there is
    transaction history, user is given choices of time periods to choose from. The function 'display_total' is called
    next.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.

    Returns:
    - None
    """
    if CHANNEL_ID not in user_list or user_list[CHANNEL_ID].get_number_of_transactions() == 0: await ctx.send("Oops! Looks like you do not have any spending records!")
    else:
        try:
            select_options = [discord.SelectOption(label="Day"),discord.SelectOption(label="Month"),]
            select = Select(placeholder="Select a category", max_values=1,min_values=1, options=select_options)
                
            async def my_callback(interaction):
                await interaction.response.send_message(f'You chose: {select.values[0]}')
                await asyncio.sleep(0.5)
                await display_total(ctx, select.values[0])
            
            select.callback = my_callback
            view = View(timeout=90)
            view.add_item(select)
            
            await ctx.send('Please select a category to see the total expense', view=view)

        except Exception as ex:
            print(str(ex), exc_info=True)
            await ctx.send("Request cannot be processed. Please try again with correct format!")


async def display_total(ctx, sel_category):
    """
    Receives the input time period from display(ctx) and displays the transaction summary for the corresponding time period.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window
    - sel_category (string): The time period selected by the user (day / month)

    Returns:
    - None
    """
    dateFormat = "%m/%d/%Y"
    try:
        day_week_month = sel_category

        if day_week_month not in user_list[CHANNEL_ID].spend_display_option: raise Exception('Sorry I can\'t show spendings for "{}"!'.format(day_week_month))

        if len(user_list[CHANNEL_ID].transactions) == 0: raise Exception("Oops! Looks like you do not have any spending records!")

        await ctx.send("Hold on! Calculating...")

        if day_week_month == "Day":
            query = datetime.today()
            query_result = ""
            total_value = 0
            for category in user_list[CHANNEL_ID].transactions.keys():
                for transaction in user_list[CHANNEL_ID].transactions[category]:
                    if transaction["Date"].strftime("%d") == query.strftime("%d"):
                        query_result += "Category: {} ; Date: {} ; Value: {:.2f} \n".format(category, transaction["Date"].strftime(dateFormat), transaction["Value"])
                        total_value += transaction["Value"]
            total_spendings = "Here are your total spendings for the date {} \n\n".format(datetime.today().strftime("%m/%d/%Y"))
            total_spendings += query_result
            total_spendings += "Total Value {:.2f}".format(total_value)
            await ctx.send(total_spendings)
        elif day_week_month == "Month":
            query = datetime.today()
            query_result = ""
            total_value = 0
            budget_value = user_list[CHANNEL_ID].monthly_budget
            for category in user_list[CHANNEL_ID].transactions.keys():
                for transaction in user_list[CHANNEL_ID].transactions[category]:
                    if transaction["Date"].strftime("%m") == query.strftime("%m"):
                        query_result += "Category: {} ; Date: {} ; Value: {:.2f} \n".format(category,transaction["Date"].strftime(dateFormat),transaction["Value"])
                        total_value += transaction["Value"]
            total_spendings = ("Here are your total spendings for the Month {} \n\n".format(datetime.today().strftime("%B")))
            total_spendings += query_result
            total_spendings += "Total Value {:.2f}\n".format(total_value)
            total_spendings += "Budget for the month {}".format(str(budget_value))
            await ctx.send(total_spendings)
    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")

@bot.command()
async def budget(ctx):
    """
    Handles the commands 'budget'. To set a budget monthly and hence keep a track of the transactions. 

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.

    Returns:
    - None
    """
    if CHANNEL_ID not in user_list.keys(): user_list[CHANNEL_ID] = User(CHANNEL_ID)
    try:
        await ctx.send(f"Your current monthly budget is {user_list[CHANNEL_ID].monthly_budget}")
        await ctx.send("Enter an amount to update your monthly budget. (Enter numeric values only)")
        budget_resp = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send('You ran out of time to answer!')
    else:
        if budget_resp: await post_budget_input(ctx, budget)
        else: await ctx.send('Nope enter a valid date')

async def post_budget_input(ctx, budget_resp):
    """
    Handles the processing of user input (budget). This function validates the entered amount and sets the budget. The error handling 
    functionality is also implemented.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - budget (discord.Message): The user's response message containing the budget input.

    Returns:
    - None
    """
    try:
        amount_entered = budget_resp.content
        amount_value = user_list[CHANNEL_ID].validate_entered_amount(amount_entered)  # validate
        if amount_value == 0:  raise Exception("Budget amount has to be a positive number.") # cannot be $0 spending
        user_list[CHANNEL_ID].add_monthly_budget(amount_value, CHANNEL_ID)
        await ctx.send(f"The budget for this month has been set as $ {amount_value}")
    
    except Exception as ex:
        await ctx.send("Oh no! " + str(ex))
        budget_new = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if budget_new.content.isnumeric(): await post_budget_input(ctx, budget_new)
        elif '#' not in budget_new.content : await ctx.send("Exception received: 'budget' is not a numeric character. Please re-enter #budget command")

async def select_date(ctx):
    '''
    Function to get date selection from user. This function is invoked from the add to
    enter the date of expense to be added.

    :param ctx - Discord context window
    :param Bot - Discord Bot object
    :param date - date message object received from the user
    :type: object
    :return: None

    '''
    dateFormat = "%m-%d-%Y"
    curr_day = datetime.now()
    await ctx.send("Enter day")
    await ctx.send(f"\n\tExample day in format mm-dd-YYYY: {curr_day.strftime(dateFormat)}\n")
    def check(msg): return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        date_message = await bot.wait_for('message', check=check, timeout=60)
        date_str = date_message.content.strip()
        month, date, year = map(int, date_str.split('-'))

        # Call the next function with the date, month, and year
        await process_date(ctx, date, month, year)
    except asyncio.TimeoutError: await ctx.send("You took too long to respond. Please try again.")

async def process_date(ctx, date, month, year):
    '''
    Process the date, month, and year here
    You can perform any necessary calculations or operations
    For example, you can convert them to a datetime object
    :param ctx - Discord context window
    :param date - date string
    :param month - month string
    :param year - year string
    :type: object
    :return: None
    '''
    
    try:
        date_obj = datetime(int(year), int(month), int(date))
        await ctx.send(f"Selected Date: {date_obj.strftime('%m-%d-%Y')}")
        await select_category(ctx, date_obj)
    except ValueError: await ctx.send("Invalid date, month, or year. Please enter valid values.")

@bot.command()
async def add(ctx):
    """
    Handles the commands 'add'. To add a transaction to the user records. 

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.

    Returns: None
    """
     
    if CHANNEL_ID not in user_list.keys(): user_list[CHANNEL_ID] = User(CHANNEL_ID)
    try: await select_date(ctx)

    except Exception as ex:
        print("exception occurred:"+str(ex))
        await ctx.send("Request cannot be processed. Please try again with correct format!")

async def select_category(ctx, date):
    """
    Function to enable category selection via a custom-defined category dropdown. This function is invoked from the 'select_date' function 
    to select the category of expense to be added. It utilizes the Select and View classes from discord.ui and a callback to handle the 
    interaction response.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - date (discord.Message): The date message object received from the user.

    Returns:
    - None
    """

    spend_categories = user_list[CHANNEL_ID].spend_categories
    select_options = [discord.SelectOption(label=category) for category in spend_categories]
    select = Select(placeholder="Select a category", max_values=1,min_values=1, options=select_options)
    
    async def my_callback(interaction):
        await interaction.response.send_message(f'You chose: {select.values[0]}')
        await asyncio.sleep(0.5)
        if select.values[0] not in spend_categories:
            await ctx.send("Invalid category")   
            raise Exception('Sorry I don\'t recognise this category "{}"!'.format(select.values[0]))

        await post_category_selection(ctx, date, select.values[0])

    select.callback = my_callback
    
    view = View(timeout=90)
    view.add_item(select)
  
    await ctx.send('Please select a category', view=view)

async def post_category_selection(ctx, date_to_add,category):
    """
    Receives the category selected by the user and then asks for the amount spent. If an invalid category is given,
    an error message is displayed, followed by a command list. If the category given is valid, 'post_amount_input' is
    called next to collect the amount spent.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - date_to_add (object): The date of the purchase.
    - category (str): The selected category for the expense.

    Returns:
    - None
    """
    try:
        selected_category = category
        
        await ctx.send(f'\nHow much did you spend on {selected_category}')
        amount = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await post_amount_input(ctx, amount.content,selected_category,date_to_add)
    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")
        

async def post_amount_input(ctx, amount_entered,selected_category,date_to_add):
    """
    Receives the amount entered by the user and adds it to the transaction history. An error is displayed if the entered
    amount is zero. Else, a message is shown that the transaction has been added.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - amount_entered (str): The amount entered by the user for the transaction.
    - selected_category (str): The category of the expense selected by the user.
    - date_to_add (str): The date of the transaction in a string format.

    Returns:
    - None
    """
   
    try:
        amount_value = user_list[CHANNEL_ID].validate_entered_amount(amount_entered)  # validate
        if amount_value == 0:  raise Exception("Spent amount has to be a non-zero number.") # cannot be $0 spending

        category_str, amount_str = (selected_category,format(amount_value, ".2f"))
        user_list[CHANNEL_ID].add_transaction(date_to_add, selected_category, amount_value, CHANNEL_ID)
        total_value = user_list[CHANNEL_ID].monthly_total()
        add_message = f"The following expenditure has been recorded: You have spent ${amount_str} for {category_str} on {date_to_add}"

        if user_list[CHANNEL_ID].monthly_budget > 0:
            if total_value > user_list[CHANNEL_ID].monthly_budget: await ctx.send("*You have gone over the monthly budget*")
            elif total_value == user_list[CHANNEL_ID].monthly_budget: await ctx.send("*You have exhausted your monthly budget. You can check/download history*")
            elif total_value >= 0.8 * user_list[CHANNEL_ID].monthly_budget: await ctx.send("*You have used 80% of the monthly budget*")

        await ctx.send(add_message)
    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")

@bot.command()
async def delete(ctx):
    """
    Handles the 'delete' command and prompts the user to choose a deletion option.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    
    Returns:
    - None
    """

    dateFormat = "%m-%d-%Y"
    monthFormat = "%m-%Y"
    try:
        if (CHANNEL_ID in user_list
            and user_list[CHANNEL_ID].get_number_of_transactions() != 0):
            
            curr_day = datetime.now()
            prompt = "Enter the day, month, or All\n"
            prompt += f"\n\tExample day in format mm-dd-YYYY: {curr_day.strftime(dateFormat)}\n"
            prompt += f"\n\tExample month in format mm-YYYY: {curr_day.strftime(monthFormat)}"
            await ctx.send(prompt)
            delete_type = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await process_delete_argument(ctx, delete_type.content)
        else:
            delete_history_text = ("No records to be deleted. Start adding your expenses to keep track of your spendings! ")
            await ctx.send(delete_history_text)

    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")


async def process_delete_argument(ctx, delete_type):
    """
    Receives the user's choice for deletion and asks for confirmation.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - delete_type (str): The user's input for deletion.

    Returns:
    - None
    """

    dateFormat = "%m-%d-%Y"
    monthFormat = "%m-%Y"
    text = delete_type #delete_type
    date = None
    is_month = False
    if text.lower() == "all": date = "all"
    else:
        # try and parse as Date-Month-Year
        if user_list[CHANNEL_ID].validate_date_format(text, dateFormat) is not None: date = user_list[CHANNEL_ID].validate_date_format(text, dateFormat)
        # try and parse as Month-Year
        elif user_list[CHANNEL_ID].validate_date_format(text, monthFormat) is not None:
            date = user_list[CHANNEL_ID].validate_date_format(text, monthFormat)
            is_month = True

    if date is None: await ctx.send("error parsing text")
    else:
        # get the records either by given day, month, or all records
        records_to_delete = user_list[CHANNEL_ID].get_records_by_date(date, is_month)
        # if none of the records match that day
        if len(records_to_delete) == 0: await ctx.send(f"No transactions within {text}")
        response_str = "Confirm records to delete\n"
        response_str += user_list[CHANNEL_ID].display_transaction(records_to_delete)
        await ctx.send(response_str)
        response_str = "\nEnter Yes or No"
        await ctx.send(response_str)
        response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await handle_confirmation(ctx, response.content, records_to_delete)


async def handle_confirmation(ctx, message, records_to_delete):
    """
    Deletes transactions if the user confirms.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - message (str): The user's confirmation ("Yes" or "No").
    - records_to_delete (list): The records to be deleted.

    Returns:
    - None
    """

    if message.lower() == "yes":
        user_list[CHANNEL_ID].deleteHistory(records_to_delete)
        user_list[CHANNEL_ID].save_user(CHANNEL_ID)
        await ctx.send("Successfully deleted records")
    else: await ctx.send("No records deleted")


@bot.command()
async def history(ctx):
    """
    Handles the command 'history'. Lists the transaction history.

    :param ctx - Discord context window
    :param Bot - Discord Bot object
    :type: object
    :return: None
    """
    try:
        count = 0
        table = [["Category", "Date", "Amount in $"]]

        if CHANNEL_ID not in user_list.keys(): user_list[CHANNEL_ID] = User(CHANNEL_ID)

        if not user_list[CHANNEL_ID].transactions: raise Exception("Sorry! No spending records found!")

        for category, transactions in user_list[CHANNEL_ID].transactions.items():
            for transaction in transactions:
                count += 1
                date = transaction["Date"].strftime("%m-%d-%y")
                value = format(transaction["Value"], ".2f")
                table.append([category, date, "$ " + value])

        if count == 0: raise Exception("Sorry! No spending records found!")

        spend_total_str = "```" + tabulate(table, headers='firstrow') + "```"
        await ctx.send(spend_total_str)

    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")

@bot.command()
async def edit(ctx):
    """
    Handles the command 'edit' and then displays a message explaining the format. The function 'edit_list2' is called next.

    :param ctx - Discord context window
    :param Bot - Discord Bot object
    :type: object
    :return: None
    """

    try:
        if CHANNEL_ID in list(user_list.keys()):
            await ctx.send("Please enter the date of transaction to edit(in mm-dd-yyyy format)")
            date = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)

            await ctx.send("Please enter the value of transaction to edit")
            value = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)

            select_options = [discord.SelectOption(label="Food"), discord.SelectOption(label="Groceries"), discord.SelectOption(label="Utilities"), discord.SelectOption(label="Transport"), discord.SelectOption(label="Shopping")]
            select = Select(max_values=1,min_values=1, options=select_options)
            async def my_callback(interaction):
                await interaction.response.send_message(f'You chose: {select.values[0]}')
                await asyncio.sleep(0.5)
                await edit_list2(ctx, date.content, select.values[0], value.content)

            select.callback = my_callback
            view = View(timeout=90)
            view.add_item(select)

            await ctx.send('Please select the Category of transaction', view=view)
        
        else: await ctx.send("No data found")
    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")


async def edit_list2(ctx,date,category,value):
    """
    Parses the input from the user message, finds the appropriate transaction, and asks the user whether they
    want to update the date, value, or category of the transaction, then passes control to the edit3 function.

    Parameters:
    - ctx (discord.ext.commands.Context): The Discord context window.
    - date (str): The date of the transaction in the format "%m-%d-%Y".
    - category (str): The category of the expense to be edited.
    - value (str or float): The value of the transaction to be edited.

    Returns:
    - None
    """
    try:
        dateFormat = "%m-%d-%Y"
        info_date = user_list[CHANNEL_ID].validate_date_format(date, dateFormat)
        info_category = category
        info_value = value

        if info_date is None:
            await ctx.send("The date is incorrect")
            return
        select_options = [discord.SelectOption(label="Date"), discord.SelectOption(label="Category"), discord.SelectOption(label="Cost")]
        select = Select(placeholder="What do you want to update", max_values=1,min_values=1, options=select_options)
        async def my_callback(interaction):
            await interaction.response.send_message(f'You chose: {select.values[0]}')
            await asyncio.sleep(0.5)
            await edit3(ctx, select.values[0])

        for transaction in user_list[CHANNEL_ID].transactions[info_category]:
            if transaction["Date"].date() == info_date:
                if transaction["Value"] == float(info_value):
                    user_list[CHANNEL_ID].store_edit_transaction(transaction, info_category)
                    select.callback = my_callback
                    view = View(timeout=90)
                    view.add_item(select)

                    await ctx.send('Please select an option to update', view=view)
                    break
        else: await ctx.send("Transaction not found")
    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")


async def edit3(ctx,choice):
    """
    Receives the user's input corresponding to what they want to edit and transfers the execution to the function
    according to the choice.

    :param ctx: The Discord context window.
    :param choice: The user's choice for editing ("Date," "Category," or "Cost").
    :return: None
    """
    choice1 = choice
    if choice1 == "Date":
        await ctx.send ("Please enter the new date (in mm-dd-yyyy format)")
        new_date = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await edit_date(ctx,new_date)

    if choice1 == "Category":
        select_options = [discord.SelectOption(label="Food"),discord.SelectOption(label="Groceries"),discord.SelectOption(label="Utilities"),discord.SelectOption(label="Transport"),discord.SelectOption(label="Shopping")]
        select = Select(max_values=1,min_values=1, options=select_options)
        async def my_callback(interaction):
            await interaction.response.send_message(f'You chose: {select.values[0]}')
            await asyncio.sleep(0.5)
            await edit_cat(ctx, select.values[0])

        select.callback = my_callback
        view = View(timeout=90)
        view.add_item(select)

        await ctx.send('Please select the new Category', view=view)

    if choice1 == "Cost":
        await ctx.send ( "Please type the new cost")
        new_cost = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await edit_cost(ctx,new_cost)


async def edit_date(ctx, message):
    """
    Updates the date of a transaction when the user chooses to edit it.

    :param ctx: The Discord context window.
    :param message: The user's message containing the new date.
    :return: None
    """
    new_date = message.content
    user_date = datetime.strptime(new_date, "%m-%d-%Y")
    if user_date is None:
        await ctx.send ("The date is incorrect")
        return
    updated_transaction = user_list[CHANNEL_ID].edit_transaction_date(user_date)
    user_list[CHANNEL_ID].save_user(CHANNEL_ID)
    await ctx.send(("Date is updated. Here is the new transaction. \n Date {}. Value {}. \n".format(updated_transaction["Date"].strftime("%m-%d-%Y %H:%M:%S"),format(updated_transaction["Value"], ".2f"))))


async def edit_cat(ctx,new_category):
    """
    Updates the category of a transaction when the user chooses to edit it.

    :param ctx: The Discord context window.
    :param new_category: The new category chosen by the user.
    :return: None
    """
    updated_transaction = user_list[CHANNEL_ID].edit_transaction_category(new_category)
    if updated_transaction:
        user_list[CHANNEL_ID].save_user(CHANNEL_ID)
        await ctx.send("Category has been edited.")
    else: await ctx.send("Category has not been edited successfully")


async def edit_cost(ctx,message):
    """
    Updates the amount of a transaction when the user chooses to edit it.

    :param ctx: The Discord context window.
    :param message: The user's message containing the new cost.
    :return: None
    """
    new_cost = message.content

    new_cost = user_list[CHANNEL_ID].validate_entered_amount(new_cost)
    if new_cost != 0:
        user_list[CHANNEL_ID].save_user(CHANNEL_ID)
        updated_transaction = user_list[CHANNEL_ID].edit_transaction_value(new_cost)
        await ctx.send("Value is updated. Here is the new transaction. \n Date {}. Value {}. \n".format(updated_transaction["Date"].strftime("%m-%d-%Y %H:%M:%S"),format(updated_transaction["Value"], ".2f")))

    else:
        await ctx.send("The cost is invalid")
        return




@bot.command()
async def chart(ctx):
    """
    Handles the chart command. When the user runs this command the bot will create a piechart
    of all the transactions and their categories and post that to the chat

    :param ctx - Discord context window
    :param Bot - Discord Bot object
    :param date - date message object received from the user
    :type: object
    :return: None
    """
    try:
        dateFormat = "%m-%d-%Y"
        curr_day = datetime.now()
        await ctx.send("Enter start day")
        await ctx.send(f"\n\tExample day in format mm-dd-YYYY: {curr_day.strftime(dateFormat)}\n")

        def check(message):return message.author == ctx.author and message.channel == ctx.channel

        start_date_message = await bot.wait_for('message', check=check, timeout=30)
        start_date_str = start_date_message.content

        await ctx.send("Enter end day")
        await ctx.send(f"\n\tExample day in format mm-dd-YYYY: {curr_day.strftime(dateFormat)}\n")

        end_date_message = await bot.wait_for('message', check=check, timeout=30)
        end_date_str = end_date_message.content

        start_date_dt = datetime.strptime(start_date_str, "%m-%d-%Y")
        end_date_dt = datetime.strptime(end_date_str, "%m-%d-%Y")

        chart_file = user_list[CHANNEL_ID].create_chart(CHANNEL_ID, start_date_dt, end_date_dt)
        for cf in chart_file:
            with open(cf, "rb") as f:
                file = discord.File(f)
                await ctx.send(file=file)

    except Exception as ex:
        print(str(ex), exc_info=True)
        await ctx.send("Request cannot be processed. Please try again with correct format!")

def get_users():
    """
    Reads user data from files in a specified directory and returns it as a dictionary.
    The function searches for files with a ".pickle" extension in the specified directory, reads each file's content, and stores it in a 
    dictionary where the keys are the filenames (without the ".pickle" extension) and the values are the deserialized data from the files.

    Returns:
    - users (dict): A dictionary containing user data.
    """

    data_dir = "discordData"
    users = {}
    for file in os.listdir(data_dir):
        if file.endswith(".pickle"):
            u = re.match(r"(.+)\.pickle", file)
            if u:
                u = u.group(1)
                abspath = pathlib.Path("{0}/{1}".format(data_dir, file)).absolute()
                with open(abspath, "rb") as f: users[u] = pickle.load(f)

    return users

if __name__ == "__main__":
    try:
        user_list = get_users()
        bot.run(BOT_TOKEN)
    except Exception as e: print(f"{e}")

