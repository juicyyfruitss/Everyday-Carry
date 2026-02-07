import sqlite3
import logging
import log
from datetime import datetime, timedelta    
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('Log.db')
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        tableExist = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';")
        if not tableExist.fetchone():
            self.cur.execute("CREATE TABLE events (level TEXT, event TEXT, timestamp TEXT)")
            self.conn.commit()

    def LogEvent(self, level, event, timestamp):
        self.cur.execute(f"INSERT INTO events (level, event, timestamp) VALUES ('{level}', '{event}', '{timestamp}')")
        self.conn.commit()

#gets all events from the database that are not older then 14 days old
    def GetEvents(self):
        self.cur.execute(f"SELECT * FROM events WHERE timestamp >= '{(datetime.now() + timedelta(days=-14)).strftime('%Y-%m-%d %H:%M:%S')}'")
        return self.cur.fetchall()
    
    # class DBHandler(logging.Handler):
    #     def __init__(self):
    #         super().__init__()

    #     def emit(self, record):
    #         when = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
    #         label = log.LevelLabels.get(record.levelname, record.levelname.title())
    #         message = record.getMessage()
    #         self.LogEvent(label, message, when)