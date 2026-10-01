from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("fitness.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db()
    # Table 1: Users for Register & Login
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Table 2: Progress tracking for workout logs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration INTEGER NOT NULL,
            calories INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Email already registered."

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            return render_template("dashboard.html", user_name=user['name'])
        
        return "Invalid email or password."

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", user_name="User")
@app.route("/workouts")
def workouts():
    return render_template("workout_plans.html")
@app.route("/progress", methods=["GET", "POST"])
def progress():
    conn = get_db()
    if request.method == "POST":
        user_name = request.form["user_name"]
        workout_type = request.form["workout_type"]
        duration = request.form["duration"]
        calories = request.form["calories"]

        conn.execute(
            "INSERT INTO progress (user_name, workout_type, duration, calories) VALUES (?, ?, ?, ?)",
            (user_name, workout_type, duration, calories)
        )
        conn.commit()
        conn.close()
        return redirect("/progress")

    logs = conn.execute("SELECT * FROM progress ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("progress.html", logs=logs)
if __name__ == "__main__":
    init_db()  
    app.run(debug=True)