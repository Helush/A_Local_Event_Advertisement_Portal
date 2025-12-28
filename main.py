from flask import *
import sqlite3
app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    if "username" in session:
        return render_template("index.html", username=session['username'])
    else:
        return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def doLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("posts.db")
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()
        if row != None:
            session["username"] = username
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
        fullname = request.form["fullname"]
        email = request.form["email"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO user VALUES(?,?,?,?)", (username, password, fullname, email))
        conn.commit()
        conn.close()
        msg = "Successfully registered. Please click <a href='/index'>here</a> to go back to the home page."
        return render_template("registration.html", msg= msg)
    except:
        return render_template("registration.html", msg="Please enter all the required fields")

if __name__ == "__main__":
    app.run()