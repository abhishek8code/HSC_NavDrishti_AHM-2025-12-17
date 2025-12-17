import sqlite3
import os

# Check database files
db_files = ['./navdrishti.db', './dev_navdrishti.db', './Traffic_Backend/dev_navdrishti.db']

for db_file in db_files:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            print(f"{db_file}: {table_names}")
            conn.close()
        except Exception as e:
            print(f"{db_file}: Error - {str(e)}")
    else:
        print(f"{db_file}: File not found")
