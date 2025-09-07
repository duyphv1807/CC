import sqlite3
db_name = r"C:\Users\ASUS\final_database"
def connect_to_database():
    try:
        connection = sqlite3.connect(db_name)
        print("Connection established")
        cursor = connection.cursor()
        return connection
    except sqlite3.OperationalError:
        print("Database does not exist")
        return None