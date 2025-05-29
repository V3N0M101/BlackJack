import os, sys
from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

app = Flask(__name__)
app.secret_key = 'secretkey123'  # 🔐 required for sessions, flash, etc.

# users.db 
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

### Define methods and stuff


# Define routes for your HTML pages
@app.route("/")
def home():
    return render_template("main.html", logged_in=False)

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/email")
def email():
    return render_template("email.html")

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["chips"] = user["chips"]
            flash("Logged in successfully.")
            return redirect("/")  # or dashboard/home/game
        else:
            flash("Invalid username or password.")
            return redirect("/login")

    return render_template("login.html", logged_in="username" in session)

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")

@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("")
    return redirect("/login")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validations
        if not email or not username or not password or not confirm_password:
            flash('Please fill out all fields.')
            return redirect('/register')

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect('/register')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username or email already exists.')
            conn.close()
            return redirect('/register')

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (email, username, password, chips) VALUES (?, ?, ?, ?)",
    (email, username, hashed_password, 0)  # Starting chips
        )
        conn.commit()
        conn.close()

        flash('''Registration successful! 
              You can now log in.''')
        return redirect('/login')

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
