import sqlite3


def createDatabase():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # table for user
    c.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL
        )
    """)

    # table for event
    c.execute("""
        CREATE TABLE IF NOT EXISTS EVENT (
            eventID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            time_date TEXT NOT NULL,
            entry_price FLOAT NOT NULL,
            description TEXT
        )
    """)

    #table for user_event
    c.execute("""
        CREATE TABLE IF NOT EXISTS USER_EVENT(
                username TEXT NOT NULL,
                eventID INTEGER NOT NULL,
                FOREIGN KEY (username) REFERENCES USERS(username) ON DELETE CASCADE,
                FOREIGN KEY (eventID) REFERENCES EVENT(eventID) ON DELETE CASCADE,
                PRIMARY KEY (username, eventID))""")

    # table for society
    c.execute("""
        CREATE TABLE IF NOT EXISTS SOCIETY (
            societyID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    #table for society_events
    c.execute("""
        CREATE TABLE IF NOT EXISTS SOCIETY_EVENTS(
            eventID INTEGER NOT NULL,
            societyID INTEGER NOT NULL,

            FOREIGN KEY (eventID) REFERENCES EVENT(eventID) ON DELETE CASCADE,
            FOREIGN KEY (societyID) REFERENCES SOCIETY(societyID) ON DELETE CASCADE,
            PRIMARY KEY (eventID, societyID))""")

    conn.commit() # save changes
    conn.close()

if __name__ == "__main__":
    createDatabase()

