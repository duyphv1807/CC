import sqlite3
db_name = r"C:\Users\LENOVO\Documents\test3"
def connect_to_database():
    try:
        connection = sqlite3.connect(db_name)
        print("Connection established")
        cursor = connection.cursor()
        return connection
    except sqlite3.OperationalError:
        print("Database does not exist")
        return None
