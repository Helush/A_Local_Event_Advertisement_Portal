import sqlite3
from logging import raiseExceptions


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
            name TEXT NOT NULL,
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
                FOREIGN KEY (username) REFERENCES USERS(username),
                FOREIGN KEY (eventID) REFERENCES EVENT(eventID),
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

            FOREIGN KEY (eventID) REFERENCES EVENT(eventID),
            FOREIGN KEY (societyID) REFERENCES SOCIETY(societyID),
            PRIMARY KEY (eventID, societyID))""")

    conn.commit() # save changes
    conn.close()

def insertUser(username, name, password, email, is_admin):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
    INSERT INTO users (username, name, password, email, is_admin)
    VALUES (?, ?, ?, ?, ?)
    """, (username, name, password, email, is_admin))

    conn.commit()
    conn.close()

def insertEvent(eventID, name, time_date, entry_price, description):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
    INSERT INTO EVENT (eventID, name, time_date, entry_price, description)
    VALUES (?, ?, ?, ?, ?)
    """, (eventID, name, time_date, entry_price, description))
    conn.commit()
    conn.close()

def insertSociety(name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM SOCIETY 
        WHERE LOWER(name) = LOWER(?)""", (name,))
    exists = c.fetchone()[0]
    if exists > 0:
        conn.close()
        raise Exception(f"Society {name} Already Exists")
    c.execute("""
        INSERT INTO SOCIETY (name)
        VALUES (?)
    """, (name,))
    conn.commit()
    conn.close()

def insertUserEvents(username, event_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
    INSERT INTO USER_EVENT (username, eventID)
    VALUES (?, ?)
    """, (username, event_id))
    conn.commit()
    conn.close()

def insertSocietyEvents(event_id, society_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
    INSERT INTO SOCIETY_EVENTS (eventID, societyID)
    VALUES (?, ?)
    """, (event_id, society_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    createDatabase()

