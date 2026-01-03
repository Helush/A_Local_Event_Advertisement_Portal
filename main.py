from tokenize import group

from flask import *
import sqlite3
from dbscript import *
import re
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "123"

@app.route("/")
@app.route("/index")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT NAME FROM SOCIETY")
    societies = []
    records = c.fetchall()
    for row in records:
        societies.append(row[0])
    conn.close()
    events = session.pop("events", None)
    search_society = session.get("search_society", None)

    grouped_events = None
    if events:
        grouped_events = defaultdict(list)
        for e in events:
            society_name = e[3]
            grouped_events[society_name].append(e)

    if "username" in session:
        return render_template("index.html", username=session['username'], is_admin=session['is_admin'],  societies=societies, grouped_events=grouped_events, search_society=search_society)
    else:
        return render_template("index.html", societies=societies, grouped_events=grouped_events, search_society=search_society)

@app.route("/home", methods=["GET", "POST"])
def home():
    return redirect(url_for("index"))

@app.route("/login", methods=["POST", "GET"])
def doLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            msg = "Please enter both username and password"
            return render_template("index.html", msg=msg)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM USERS WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()
        if row != None:
            session["username"] = username
            session["is_admin"] = row[4]
            return redirect(url_for("index"))
        else:
            msg = "Invalid username or password"
            return render_template("index.html", msg=msg)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/register")
def openregistrationform():
    return render_template("registration.html")


email_pattern= r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

def is_valid_email(email):
    return re.match(email_pattern, email)


def is_valid_password(pwd):
    # Check if length is at least 10
    if len(pwd) < 10:
        return False

    # Check for at least one uppercase letter
    if not any(c.isupper() for c in pwd):
        return False

    # Check for at least one lowercase letter
    if not any(c.islower() for c in pwd):
        return False

    # Check for at least one digit
    if not any(c.isdigit() for c in pwd):
        return False

    return True
@app.post("/applyregister")
def register():
    try:
        username= request.form["username"]
        password = request.form["password"]
        name = request.form["fullname"]
        email = request.form["email"]
        is_admin=1 if email.startswith("org-") else 0

        if not is_valid_email(email):
            msg = "Please enter a valid email address; name@example.com"
            return render_template("registration.html", msg=msg, msg_type = "error")

        if not is_valid_password(password):
            msg = "The password should include at least one upper case letter, one lower case letter, and one digit and its length should be at least ten."

            return render_template("registration.html", msg=msg, msg_type = "error")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Check if username already exists
        c.execute("SELECT username FROM USERS WHERE username=?", (username,))
        existing_user = c.fetchone()

        if existing_user:
            conn.close()
            msg = "Username already exists. Please choose a different username."
            return render_template("registration.html", msg=msg,msg_type = "error")

        c.execute("""INSERT INTO users (username, name, password, email, is_admin)
        VALUES (?, ?, ?, ?, ?)
        """, (username, name, password, email, is_admin))
        conn.commit()
        conn.close()

        msg = "Successfully registered"
        return redirect(url_for("index"))
    except Exception as e:
        msg = f"An error occurred during registration. Please try again."
        return render_template("registration.html", msg=msg, msg_type = "error")

@app.route("/manageEvents")
def manageEvents():
    if "username" in session:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT name FROM SOCIETY")
        societies = [row[0] for row in c.fetchall()]

        c.execute("""
                SELECT e.eventID, e.name, e.time_date, e.entry_price, e.description
                FROM EVENT e
                JOIN USER_EVENT u ON u.eventID=e.eventID
                WHERE u.username=?
            """, (session['username'],))
        events_raw  = c.fetchall()

        events = []
        for event in events_raw:
            event_id = event[0]

            # Get societies for this event
            c.execute("""
                   SELECT s.name
                   FROM SOCIETY s
                   JOIN society_events i ON s.societyID = i.societyID
                   WHERE i.eventID = ?
               """, (event_id,))
            society_names = [row[0] for row in c.fetchall()]
            societies_str = ", ".join(society_names)

            events.append({
                'id': event_id,
                'name': event[1],
                'time_date': event[2],
                'entry_price': event[3],
                'description': event[4],
                'societies': societies_str
            })
        conn.close()

        return render_template("manage_events.html", societies=societies, events=events)
    return redirect(url_for("index"))

@app.route("/manageSociety", methods=["POST", "GET"])
def manageSociety():
    if "username" not in session:
        return redirect(url_for("index"))
    msg = None

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == "POST":
        try:
            name = request.form["society_name"]
            c.execute("""
                 SELECT COUNT(*) FROM SOCIETY
                 WHERE LOWER(name) = LOWER(?)""", (name,))
            exists = c.fetchone()[0]
            if exists > 0:
                 conn.close()
                 raise Exception(f"Society {name} Already Exists")
            c.execute("INSERT INTO SOCIETY (name) VALUES (?)", (name,))
            conn.commit()
        except Exception as e:
            msg = str(e)
    c.execute("""
        SELECT s.name, COUNT(se.eventID) AS count_event 
        FROM SOCIETY s
        LEFT JOIN society_events se ON s.societyID = se.societyID
        GROUP BY s.societyID
    """)
    societies = c.fetchall()
    conn.close()
    return render_template("manage_society.html", societies=societies, msg = msg)



@app.route("/createEvent", methods=["POST"])
def createEvent():
    if "username" not in session:
        return redirect(url_for("index"))

    try:
        name = request.form["name"]
        time_date = request.form["time_date"]
        societies_list = request.form.getlist("societies[]")
        description = request.form["description"]
        fee = request.form["fee"]
        fee_amount = request.form.get("fee_amount", "")

        entry_price = "Free" if fee == "Free" else fee_amount

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""INSERT INTO EVENT (name, time_date, entry_price,description) VALUES (?, ?, ?,?)""",
                  (name, time_date, entry_price, description))

        event_id = c.lastrowid

        c.execute("""INSERT INTO USER_EVENT(username, eventID) VALUES (?,?)""",(session['username'],event_id))

        for society_name in societies_list:
            c.execute("""select societyID from society where name=?""",(society_name,))
            society_id = c.fetchone()
            if society_id:
                c.execute("""Insert into society_events(eventID, societyID) values (?,?)""", (event_id, society_id[0]))

        conn.commit()
        conn.close()

        return redirect(url_for("manageEvents"))
    except Exception as e:
        print(e)
        return redirect(url_for("manageEvents"))

@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "")
    society = request.form.get("society", "all")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if society == "all":
        c.execute("""
            SELECT e.eventID, e.name, e.description, s.name
            FROM EVENT e
            JOIN society_events se ON e.eventID = se.eventID
            JOIN SOCIETY s ON se.societyID = s.societyID
            WHERE e.name LIKE '%' || ? || '%'
               OR e.description LIKE '%' || ? || '%'
            ORDER BY s.name, e.name
        """, (keyword, keyword))
    else:
        c.execute("""
            SELECT e.eventID, e.name, e.description, s.name
            FROM EVENT e
            JOIN society_events se ON e.eventID = se.eventID
            JOIN SOCIETY s ON se.societyID = s.societyID
            WHERE s.name = ?
              AND (
                   e.name LIKE '%' || ? || '%'
                OR e.description LIKE '%' || ? || '%'
              )
        """, (society, keyword, keyword))

    events = c.fetchall()
    conn.close()
    session["events"] = events
    session["search_society"] = society
    return redirect(url_for("index"))

@app.route("/event/<event_id>")
def event_details(event_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        SELECT e.name, e.time_date, e.description, e.entry_price
        FROM EVENT e
        WHERE e.eventID = ?
    """, (event_id,))
    event = c.fetchone()

    c.execute("""
        SELECT s.name
        FROM SOCIETY s
        JOIN society_events se ON s.societyID = se.societyID
        WHERE se.eventID = ?
    """, (event_id,))
    societies = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template("event_details.html", event=event, societies=societies)


@app.route("/deleteEvent", methods=["POST"])
def deleteEvent():
    if "username" not in session:
        return redirect(url_for("index"))

    eventid = request.form["event_id"]
    print(eventid)
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if user owns this event
    c.execute("SELECT * FROM USER_EVENT WHERE eventID=? AND username=?",
              (eventid, session['username']))
    if c.fetchone() is None:
        conn.close()
        return redirect(url_for("manageEvents"))


    c.execute("DELETE FROM SOCIETY_EVENTS WHERE eventID=?", (eventid,))
    c.execute("DELETE FROM USER_EVENT WHERE eventID=?", (eventid,))
    c.execute("DELETE FROM EVENT WHERE eventID=?", (eventid,))

    conn.commit()
    conn.close()
    return redirect(url_for("manageEvents"))


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("index"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT username, password, name, email FROM USERS WHERE username=?", (session['username'],))

    user = c.fetchone()
    conn.close()

    if user:
        return render_template("profile.html",username=user[0],password=user[1],name=user[2],email=user[3])

    return redirect(url_for("index"))


@app.route("/updateProfile", methods=["POST"])
def updateProfile():
    if "username" not in session:
        return redirect(url_for("index"))


    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    is_admin = 1 if email.startswith("org-") else 0

    if not is_valid_email(email):
        msg = "Please enter a valid email address; name@example.com"
        return render_template("profile.html", username=session['username'],
                               password=password, name=name, email=email,
                               msg=msg, msg_type="error")
    if not is_valid_password(password):
        msg = "The password should include at least one upper case letter, one lower case letter, and one digit and its length should be at least ten."
        return render_template("profile.html", username=session['username'],
                               password=password, name=name, email=email,
                               msg=msg, msg_type="error")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("UPDATE USERS SET name=?, email=?, password=?, is_admin=? WHERE username=?",
                  (name, email, password, is_admin, session['username']))

    conn.commit()
    conn.close()

    return render_template("profile.html", username=session['username'],
                           password=password, name=name, email=email,
                           msg="Successfully updated your profile!", msg_type="success")
if __name__ == "__main__":
    app.run()