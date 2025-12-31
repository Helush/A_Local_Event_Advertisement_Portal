from flask import *
import sqlite3
from dbscript import *
app = Flask(__name__)
app.secret_key = "123"

@app.route("/")
@app.route("/index")
def index():
    if "username" in session:
        return render_template("index.html", username=session['username'])
    else:
        return render_template("index.html")


@app.route("/ping")
def ping():
    return "THIS IS THE CORRECT APP"

@app.route("/login", methods=["POST", "GET"])
def doLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()
        is_admin = row[4]
        if row != None:
            session["username"] = username
        return redirect(url_for("index", is_admin=is_admin))
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/register")
def openregistrationform():
    return render_template("registration.html")


@app.post("/applyregister")
def register():
    try:
        username= request.form["username"]
        password = request.form["password"]
        name = request.form["fullname"]
        email = request.form["email"]
        is_admin=1 if email.startswith("org-") else 0

        # conn = sqlite3.connect("database.db")
        # c = conn.cursor()
        # c.execute("INSERT INTO user VALUES(?,?,?,?,?)", (username, password, name, email, is_admin))
        # conn.commit()
        # conn.close()
        insertUser(username, name, password, email, is_admin)

        msg = "Successfully registered. Please click <a href='/index'>here</a> to go back to the home page."
        return render_template("registration.html", msg= msg)
    except Exception as e:
        return render_template("registration.html", msg=str(e))

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
                c.execute("""Insert into society_events(eventID, societyID) values (?,?)""",(event_id,society_id))


        conn.commit()
        conn.close()

        return redirect(url_for("manageEvents"))
    except Exception as e:
        print(e)
        return redirect(url_for("manageEvents"))
if __name__ == "__main__":
    app.run()