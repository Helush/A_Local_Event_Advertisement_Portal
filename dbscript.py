import sqlite3

def createDatabase():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # table for user
    c.execute("""
        CREATE TABLE IF NOT EXISTS USER (
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

    # table for society
    c.execute("""
        CREATE TABLE IF NOT EXISTS SOCIETY (
            societyID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    conn.commit() # save changes
    conn.close()

def insertUser(username, name, password, email, is_admin):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
    INSERT INTO USER (username, name, password, email, is_admin)
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
    """), (eventID, name, time_date, entry_price, description)
    conn.commit()
    conn.close()

def insertSociety(societyID, name, description):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
    INSERT INTO SOCIETY (societyID, name, description)
    VALUES (?, ?, ?)
    """), (societyID, name, description)
    conn.commit()
    conn.close()



