import sqlite3
import logging

LOG_FILE = 'logging.txt'

class WanikaniDB():
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
        return True

    def create_wanikani_table(self):
        try:
            self._db_cur.execute('''CREATE TABLE wanikani_rec
                                (id INTEGER PRIMARY KEY, date datetime default current_timestamp,
                                user_id INTEGER, apprentice_total INTEGER,
                                 guru_total INTEGER, master_total INTEGER, enlightened_total INTEGER,
                                 burned INTEGER)''')
        except sqlite3.OperationalError as e:
            logging.exception("Error creating the db: {}".format(e))
            raise(e)

    def select_records(self, limit=5):
        try:
            self._db_cur.execute("SELECT user_id, datetime(date, 'localtime'), apprentice_total, guru_total, "
                                 "master_total, enlightened_total, burned FROM wanikani_rec ORDER BY date DESC LIMIT ?", (limit,))
            return self._db_cur.fetchall()
        except sqlite3.ProgrammingError as e:
            logging.exception("DB connection closed: {}".format(e))
            raise(e)

    def select_all_records(self):
        try:
            self._db_cur.execute("SELECT user_id, datetime(date, 'localtime'), "
                                 "apprentice_total, guru_total, master_total, enlightened_total, burned FROM wanikani_rec")
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
                             'VALUES ( ?, ?, ?, ?, ?, ?)',  info_list)
            self._db_connection.commit()
        except sqlite3.OperationalError as e:
            logging.exception(e)
            raise (e)
        except sqlite3.ProgrammingError as e:
            logging.exception(e)
            raise(e)

    def close_connection(self):
        self._db_connection.close()

if __name__ == '__main__':

    db_test = WanikaniDB()
    print(db_test.check_if_table_exist('wanikani_rec'))
    #db_test.create_wanikani_table()
    #db_test.insert_record([2, 30, 4, 5, 6, 7])
    #db_test.delete_all_records
    for record in db_test.select_all_records():
        print(record)
    for record in db_test.select_records(2):
        print(record)
    print(db_test.check_if_table_exist('wanikani_rec'))
    db_test.close_connection()