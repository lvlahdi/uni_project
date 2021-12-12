#!/usr/bin/env python3
from __future__ import print_function
import os
import csv
import mysql.connector
from time import sleep
from mysql.connector import errorcode
from time import sleep
from textwrap import fill


# get the.py directory for some important reasons
HERE = os.path.dirname(__file__)


# connecting to test db
cnx = mysql.connector.connect(user='root', password='Mahdi',
                              host='127.0.0.1',
                              database='test')


# create cursor
cursor = cnx.cursor()


# define tables we want to create
# DB_NAME = 'test'
TABLES = {}
TABLES['NEWS'] = (
    "CREATE TABLE news (title varchar(500), news_text text, ID int primary key auto_increment)")
NEWS_DICTIONARY = {}    # NOTE this will be used in insert to db function


# check/create tables
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


# clear screen function
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # if machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


# import CSV content to db
def before_import_to_db():
    with open('%s/news.csv' % HERE) as fin:
        reader = csv.reader(fin)
        for key, value in reader:
            NEWS_DICTIONARY[key.strip()] = value.strip()


# def import news by CSV file
def import_manual():
    title = input('Please enter NEWS title :\n')
    text = input('Please enter NEWS text :\n')
    NEWS_DICTIONARY[title] = text


def import_by_csv():
    clearConsole()
    print('''
    To import files by a CSV file, you should create/copy/move a CSV in this format :
    "title,text" into the application.py path directory(next to main application)
    Every row, must contain just one title and one text part.
    The title has 500 characters limit and text part can contain up to 64k characters.
    Note that you have to bring the CSV file in current path and rename it to news.csv. In case
    to do these tasks wrong, the app will be having erred.
    ''')
    print('Press enter/return key if you ready to import...')
    input()
    # we got python program directory on top of the code.
    # here, we will use that to access csv file without
    # requesting the user to run program from specific directory.
    if os.path.isfile('%s/news.csv' % HERE) == True:  # check news.csv file exist or not
        print('Alright. CSV file exist.')
        sleep(1)
        print('Time to check data formats...')
        sleep(2)
        import pandas as pd  # [x] : complete this
        # reads in all the rows, but skips the first one as it is a header.
        # so that, we will set header=None to prevent logical errors on data format check.
        df = pd.read_csv("%s/news.csv" % HERE, header=None)
        total_rows = len(df.axes[0])    # axes of 0 is for a row
        total_cols = len(df.axes[1])    # axes of 1 is for a column
        if total_cols == 2:
            print('Alright... requested content are followed. Everything is OK for importing data to database \U0001F642.')
            sleep(3)
            print('Importing...\nThanks for your patience.')
            sleep(3)
            before_import_to_db()
            return
        elif total_cols < 2:
            print('The requested csv content format is not followed. it has less than two columns.\nYou will redirect to main menu.')
            sleep(3)
            return
        elif total_cols > 2:
            print('The requested csv content format is not followed. it has more than two columns.\nYou will redirect to main menu.')
            sleep(3)
            return
        input()
    elif os.path.isfile('%s/news.csv' % HERE) == False:
        print('"news.csv" file is not exist...\nYou will redirect to main menu.')
        return


# ask to read or write
def user_prompt():
    print(
        'Main Menu :\n\nPlease enter :\n\t[i] to import a NEWS\n\t[r] to read NEWS list\n\t[d] to delete recorded data')
    print('''
        
        You can enter Ctrl+C everytime do you want to exit from app.\n
    ''')
    prompt = input()
    while True:
        if prompt == 'i' or prompt == 'I':  # NOTE: in case user entered 'i' to import data
            clearConsole()
            import_by_what = input(
                '\n\nPlease enter: \n\n\t[c] to import news from CSV file\n\t[i] to insert them manually one by one\n')
            if import_by_what == 'c' or import_by_what == 'C':  # COMMENT: if user want to import NEWS from CSV
                NEWS_DICTIONARY.clear()
                import_by_csv()
                return 'Was written'
            elif import_by_what == 'i' or import_by_what == 'I':  # COMMENT: if user want to import NEWS one by one
                NEWS_DICTIONARY.clear()
                import_manual()
                return 'Was written'
            else:  # in case user pressed wrong key...
                print('wrong key pressed! try again.')
            break
        # NOTE: in case user entered 'r' to read NEWS:
        elif prompt == 'r' or prompt == 'R':
            clearConsole()
            # COMMENT: because we use this dictionary not only for writing! we use it for reading too :)...
            NEWS_DICTIONARY.clear()
            # COMMENT: it will let us to use a clear dictionary for reading data from database.
            return 'Go read!'
        # NOTE: in case user entered 'r' to delete database records:
        elif prompt == 'd' or prompt == 'D':
            clearConsole()
            print(
                '\n\nPlease enter :\n\t[ ] the number of records you want to delete\n\t[a] to delete all recorded data')
            print('''
            \n\tCAUTION!\n\tIn case delete records, it will no longer be possible to recover it
            ''')
            how_many = input()
            if how_many == 'a' or how_many == 'A':  # COMMENT: if user want to delete all records
                return 'Clear all'
            else:
                return how_many
        else:
            # in case user pressed wrong key...
            print('wrong key pressed! try again.')


# import news to database
while True:
    clearConsole()
    program_phase_changer = user_prompt()
    '''We have 3 switches here!
    first one is "Was written". it changes program phase to writing
    second one is "Go Read!" that will do some tasks to display news in database to user
    and the last one is "Clear all" to clear all the database records.'''
    if program_phase_changer == 'Was written':
        for external_title, external_text in NEWS_DICTIONARY.items():   # we used external to make reading easier
            cursor.execute("insert into news (title, news_text) values (%s, %s)",
                           (external_title, external_text))
        cnx.commit()
        sleep(0.5)
        print('Done :)')
        sleep(1.5)
        print('You will redirect to main menu.')
        sleep(2)
    elif program_phase_changer == 'Go read!':
        cursor.execute('select title, news_text from news')
        for external_title, external_text in cursor:
            print('%s\n' % external_title)
            print('%s' % fill(external_text, width=80))
            print('\n\n\n\n\n\n\n')
        input('Press enter/return key to redirect to main menu.')
# [x]:  ask how many records to remove!?
    elif program_phase_changer == 'Clear all':
        cursor.execute('delete from news')
        cnx.commit()
        sleep(1)
        print('Done :)')
        sleep(1.5)
        print('You will redirect to main menu.')
        sleep(1.5)
    else:
        # FIXME
        # [x]: FIXED!!!
        #NOTE: it's really fun :| we have to do it by defining a variable and put our number and our command into. this is why I am a noob :))
        remover_command = "delete from news order by ID desc limit %s" % (
            program_phase_changer)
        cursor.execute(remover_command)
        '''
        in addition :
        it could have been written better if we define a regex that only contains numbers and
        if user enter a wrong key or characters, show a message that ur input is wrong.
        it could also prevent some errors!
        '''
        cnx.commit()
        sleep(1)
        print('Done :)')
        sleep(1.5)
        print('You will redirect to main menu.')
        sleep(1.5)


# [ ]: find a suitable way to exit from app by user.
# [x]: data shows ugly and unclear in database after import. do it beautifuller.    # it could still be better than this but it's okay for now
# [x]: better record remover!
# [ ]: create a GUI
# [ ]: add to github
# [ ]: write full documentation, user's manual and readme for project.