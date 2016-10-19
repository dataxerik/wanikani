import sqlite3
import logging

LOG_FILE = 'logging_daily.txt'

_db_connection = None
_db_cur = None

class DailyRecords():
    def __init__(self):
        self._db_connection = sqlite3.connect('wanikani.db')
        self._db_cur = self._db_connection.cursor()
        self._table_name = 'daily_wanikani_rec'
        logging.basicConfig(filename=LOG_FILE,
                            level=logging.INFO)

    def create_table(self):
        self._db_cur.execute('''CREATE TABLE daily_wanikani_rec
                             (id INTEGER PRIMARY KEY, user TEXT, date datetime default current_timestamp,
                             apprentice_difference INTEGER, guru_difference INTEGER,
                             master_difference INTEGER, enlighten_difference INTEGER,
                             burned_difference INTEGER)''')
        self._db_connection.commit()

    def check_if_table_exist(self, table_name):
        self._db_cur.execute("SELECT name from sqlite_master where type = 'table' and name = ?", [table_name])
        for row in self._db_cur.execute("PRAGMA table_info('daily_wanikani_rec')").fetchall():
            print(row)
        if self._db_cur.fetchone() is None:
            return False
        return True

    def select_records(self, limit=5):
        self._db_cur.execute('''SELECT user, datetime(date, 'localtime'), apprentice_difference, guru_difference, master_difference,
                              enlighten_difference, burned_difference from daily_wanikani_rec ORDER BY date DESC LIMIT ?''', [limit])


        return self._db_cur.fetchall()

    def insert_record(self, count_info):
        self._db_cur.execute('''INSERT INTO daily_wanikani_rec (user, apprentice_difference, guru_difference, master_difference,
                              enlighten_difference, burned_difference) values (?, ?, ?, ?, ?, ?)''', count_info)

        self._db_connection.commit()

if __name__ == '__main__':
    db = DailyRecords()
    #if not db.check_if_table_exist('daily_wanikani_rec'):
    #print(db.create_table())
    #print(db.check_if_table_exist('daily_wanikani_rec'))
    for record in db.select_records(5):
        print(record)