import requests
import json
import sqlite3
import logging
import datetime
from collections import namedtuple
from daily_wanikani import DailyRecords


LOG_FILE = 'logging.txt'
CONFIG_FILE = 'config.ini'


class WanikaniDB:
    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = sqlite3.connect('wanikani.db')
        self._db_cur = self._db_connection.cursor()
        self._table_name = 'wanikani_rec'
        logging.basicConfig(filename=LOG_FILE,
                            level=logging.INFO)

    def check_if_table_exist(self, table_name):
        self._db_cur.execute("SELECT ? FROM sqlite_master WHERE type='table' AND name=?", ['name', table_name])
        if self._db_cur.fetchone() is None:
            return False
        else:
            return True

    def create_wanikani_table(self):
        try:
            self._db_cur.execute('''CREATE TABLE wanikani_rec
                                (id INTEGER PRIMARY KEY, date datatime default current_timestamp,
                                user_id INTEGER, apprentice_total INTEGER,
                                 guru_total INTEGER, master_total INTEGER, enlightened_total INTEGER,
                                 burned INTEGER)''')
        except sqlite3.OperationalError as sql_op:
            logging.exception("Error creating the db: {}".format(sql_op))
            raise sql_op

    def select_records(self, limit=5):
        try:
            self._db_cur.execute('SELECT user_id, date, apprentice_total, guru_total, master_total, enlightened_total, burned FROM wanikani_rec ORDER BY date DESC LIMIT ?', (limit,))
            return self._db_cur.fetchall()
        except sqlite3.ProgrammingError as sql_pe:
            logging.exception("DB connection closed: {}".format(sql_pe))
            raise sql_pe

    def select_all_records(self):
        try:
            self._db_cur.execute('SELECT user_id, apprentice_total, guru_total, master_total, enlightened_total, burned FROM wanikani_rec')
            return self._db_cur.fetchall()
        except sqlite3.OperationalError as e:
            logging.exception(e)
            print(e)

    def delete_all_records(self):
        self._db_cur.execute('DELETE FROM wanikani_rec')
        self._db_connection.commit()

    def insert_record(self, info_list):
        try:
            self._db_cur.execute('INSERT INTO wanikani_rec '
                                 '(user_id, apprentice_total, guru_total, master_total, enlightened_total, burned) '
                                 'VALUES ( ?, ?, ?, ?, ?, ?)', info_list)
            self._db_connection.commit()
        except sqlite3.OperationalError as e:
            logging.exception(e)
            raise e
        except sqlite3.ProgrammingError as e:
            logging.exception(e)
            raise e

    def close_connection(self):
        self._db_connection.close()


def get_wanikani_distribution():
    def get_api_key():
        with open(CONFIG_FILE) as fout:
            api_key = fout.readline()
        return api_key

    def store_wani_information():
        pass

    request_url = "https://www.wanikani.com/api/user/{}/srs-distribution".format(get_api_key())
    return requests.get(request_url).text


def test_info():
    with open('api_reply.txt') as fout:
        response_ = json.load(fout)

    print(type(response_))

    for level, breakdown in response_['requested_information'].items():
        print("{} has {} characters".format(level, breakdown['total']))

    return response_

def compute_daily_change(records_):
    rec = []
    rec.append(records_[0].user)
    rec.append(records_[0].apprentice_number - records_[1].apprentice_number)
    rec.append(records_[0].guru_number - records_[1].guru_number)
    rec.append(records_[0].master_number - records_[1].master_number)
    rec.append(records_[0].enlighten_number - records_[1].enlighten_number)
    rec.append(records_[0].burned_number - records_[1].burned_number)

    return rec

wani_db = WanikaniDB()
daily_recs = DailyRecords()
daily_records = None
wani_record = namedtuple('wani_record', ['user', 'date', 'apprentice_number', 'guru_number',
                                         'master_number', 'enlighten_number', 'burned_number'])

def is_daily_rec_recorded(record):
    date = [int(num) for num in wani_record(*record[0]).date.split(" ")[0].split("-")]
    return datetime.date(date[0], date[1], date[2]) < datetime.date.today()
try:
    
    response = json.loads(get_wanikani_distribution())
    user = response['user_information']['username']
    apprentice_number = response['requested_information']['apprentice']['total']
    guru_number = response['requested_information']['guru']['total']
    master_number = response['requested_information']['master']['total']
    enlighten_number = response['requested_information']['enlighten']['total']
    burned_number = response['requested_information']['burned']['total']

    if is_daily_rec_recorded(wani_db.select_records(1)):
        print("A record is not already inserted")
        wani_db.insert_record([user, apprentice_number, guru_number, master_number, enlighten_number, burned_number])
    else:
        print("")

    #wani_db.insert_record([user, apprentice_number, guru_number, master_number, enlighten_number, burned_number])


    daily_records = [wani_record(*record) for record in wani_db.select_records(2)]
    print(daily_recs.select_records(1))
    if daily_records is not None and len(daily_records) > 1 and is_daily_rec_recorded(daily_recs.select_records(1)):
        print(compute_daily_change(daily_records))
        daily_recs.insert_record(compute_daily_change(daily_records))
    else:
        print("Record already inserted for today")
    print("going to print")
    for record in daily_recs.select_records(5):

        print(record)
except FileNotFoundError as e:
    logging.exception(e)
except KeyError as e:
    logging.exception("Key error: {}".format(e))
    raise e
except sqlite3.OperationalError as e:
    logging.exception(e)
except sqlite3.ProgrammingError as e:
    logging.exception(e)
finally:
    wani_db.close_connection()




    # Object: Get the daily numerical change between levels

    # I need to get two response: one in the morning and one at night

    # write something to do this automatically

    # store the information in a db or file

    # log to a db
