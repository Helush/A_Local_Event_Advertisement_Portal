from tokenize import group

from flask import *
import sqlite3
from dbscript import *
import re
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "123"

"""
Displays the main homepage of the application. Fetches all available societies from the database
and displays them in a list.  The page adapts based on
whether a user is logged in, it serves as the landing page and main navigation hub for the entire application.
"""
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

"""
Simple redirect route that forwards any requests to /home back to the index page.
Provides an alternative URL endpoint for accessing the homepage.
"""
@app.route("/home", methods=["GET", "POST"])
def home():
    return redirect(url_for("index"))

"""
Handles user authentication by accepting username and password credentials from a login form.
Validates that both fields are provided, then queries the database to verify the credentials match
an existing user account. If authentication succeeds, creates a session storing the username and
admin status, then redirects to the homepage. If credentials are invalid or missing, displays
appropriate error messages to the user. GET requests simply redirect to the index page.
"""
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


"""
Terminates the user's session by removing the username from the session storage,
effectively logging them out. Redirects to the homepage where they'll see the logged-out view.
"""
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


"""
Displays the user registration form where new users can create an account.
Simply renders the registration template without any data processing.
"""
@app.route("/register")
def openregistrationform():
    return render_template("registration.html")


"""
Validates email addresses using a regular expression pattern. Checks that the email follows
the standard format of local-part@domain.extension. Returns True if the email is valid,
False otherwise. Used to ensure users provide properly formatted email addresses during
registration and profile updates.
"""
email_pattern= r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
def is_valid_email(email):
    return re.match(email_pattern, email)


"""
Enforces password strength requirements to ensure user account security. Validates that passwords
are at least 10 characters long and contain a mix of character types: at least one uppercase letter,
one lowercase letter, and one numeric digit. Returns True if all requirements are met, False if any
requirement fails. This helps protect user accounts from common password attacks.
"""
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

"""
Processes new user registration by collecting username, password, full name, and email from the
registration form. Automatically determines admin status - users with emails starting with "org-"
are granted admin privileges. Validates the email format and password strength using helper functions.
Checks for duplicate usernames to prevent account conflicts. If all validations pass, creates a new
user record in the database. Displays appropriate error messages for validation failures or if the
username already exists. Successfully registered users are redirected to the homepage.
"""
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


"""
Displays the event management dashboard for logged-in users. Shows all events that the current user
has created, along with a list of all available societies for creating new events. For each event,
retrieves associated society information and formats it as a comma-separated list. The page allows
users to view their events with full details including ID, name, date/time, entry price, description,
and associated societies. Only accessible to authenticated users - others are redirected to the homepage.
"""
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


"""
Provides society management functionality for logged-in users. Handles both viewing all existing
societies and creating new ones. When displaying societies, shows each society name along with a
count of how many events are associated with it using a LEFT JOIN to include societies with zero events.
For POST requests, processes new society creation by validating that the society name doesn't already
exist (case-insensitive check). If a duplicate is found, displays an error message. Successfully created
societies are added to the database and the page refreshes to show the updated list. Only accessible
to authenticated users.
"""
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



"""
Processes the creation of new events by authenticated users. Collects event details from the form
including name, date/time, associated societies, description, and entry fee (either free or a specific
amount). Validates that the event name doesn't already exist in the database to prevent duplicates.
Creates the event record, links it to the creating user through the USER_EVENT table, and establishes
associations with selected societies through the society_events table. The societies list can include
multiple societies that will host or sponsor the event. After successful creation, redirects to the
event management page. Displays error messages if the event name is already taken or if any database
operation fails.
"""
@app.route("/createEvent", methods=["POST"])
def createEvent():
    if "username" not in session:
        return redirect(url_for("index"))
    conn = None

    try:
        name = request.form["name"]
        time_date = request.form["time_date"]
        societies_list = request.form.getlist("societies[]")
        description = request.form["description"]
        fee = request.form.get("fee")
        fee_amount = request.form.get("fee_amount", "")

        entry_price = "Free" if fee == "Free" else fee_amount
        if not fee:
            session["error_msg"] = "Please select an entry fee type."
            return redirect(url_for("manageEvents"))

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
    except sqlite3.IntegrityError:
        conn.close()
        session["error_msg"] = "Event already exists"
        return redirect(url_for("manageEvents"))


"""
Performs event searches based on user-provided keywords and optional society filters. Searches through
event names and descriptions for matches to the keyword using SQL LIKE queries. Can either search across
all societies or filter results to a specific society. Results are ordered by society name and event name
for organized presentation. The search results and selected society filter are stored in the session so
they can be displayed on the index page after redirecting. This allows users to discover events that
match their interests or find specific information about activities offered by different societies.
"""
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


"""
Displays detailed information for a specific event identified by its event ID. Retrieves the event's
name, scheduled date/time, description, and entry price from the database. Also fetches all societies
associated with the event to show which organizations are hosting or sponsoring it. This page provides
users with comprehensive information about an event before they decide to attend. Accessible to all
users regardless of authentication status, allowing anyone to browse event details.
"""
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


"""
Allows authenticated users to delete events they have created. First verifies that the current user
is the owner of the event by checking the USER_EVENT table - this prevents users from deleting events
created by others. If ownership is confirmed, performs a cascading delete that removes the event record
along with all associated data: the society-event associations from SOCIETY_EVENTS table and the user-event
link from USER_EVENT table. This ensures complete cleanup and maintains database integrity. After successful
deletion, redirects back to the event management page. Non-owners attempting to delete an event are silently
redirected without making any changes.
"""
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

"""
Displays the user profile page for authenticated users. Retrieves the current user's account information
from the database including username, password, full name, and email address. This information is displayed
in the profile template where users can review their account details and make updates if needed. Only
accessible to logged-in users - unauthenticated visitors are redirected to the homepage. If the user record
cannot be found in the database, also redirects to the homepage.
"""
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


"""
Processes user profile updates for authenticated users. Accepts modified name, email, and password from
the profile form. Re-validates the email format and password strength using the same validation functions
used during registration to maintain consistent security standards. Automatically updates the admin status
based on whether the email starts with "org-" - allowing users to gain or lose admin privileges if they
change their email prefix. If validation fails, redisplays the profile form with error messages and the
submitted values so users can correct issues without re-entering all information. Upon successful update,
saves changes to the database and displays a success message. Only accessible to authenticated users.
"""
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
    if name == "":
        msg = "Please insert full name"
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
    createDatabase()
    app.run()