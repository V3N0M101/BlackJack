import os, sys
from flask import Flask, render_template, request, redirect, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, ssl
from email.message import EmailMessage
import random
from secure import EMAIL_PASS_SECURE


# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

def send_verification_email(to_email: str, code: str):
    sender_email = "blackhub420@gmail.com"
    app_password = EMAIL_PASS_SECURE

    # (optional) look up username by email so you can say “Hi Ned,” instead of “Hi,”
    conn = get_db_connection()
    row = conn.execute(
        "SELECT username FROM users WHERE email = ?",
        (to_email,)
    ).fetchone()
    conn.close()
    username = row["username"] if row else ""

    message = EmailMessage()
    message["From"]    = sender_email
    message["To"]      = to_email
    message["Subject"] = "Your Password Reset Code"
    message.set_content(
        f"Hi {username},\n\n"
        f"Your verification code is: {code}\n\n"
        "If you didn’t request this, just ignore this email."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, app_password)
        server.send_message(message)

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
    # pop the one-off flag so it only fires once
    login_in_alert = session.pop("login_alert", False)
    return render_template(
        "main.html",
        logged_in       = "username" in session,
        login_in_alert = login_in_alert)
    


@app.route("/game")
def game():
    fullscreen = request.args.get("fullscreen", "").lower() == "true"
    return render_template("game.html", fullscreen=fullscreen)



@app.route("/email")
def email():
    return render_template("email.html")

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route('/send-reset-code', methods=['POST'])
def send_reset_code():
    email = request.form['email']
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    session['email'] = email
    session['code'] = code
    # Send email in background to avoid lag:
    import threading
    threading.Thread(target=send_verification_email, args=(email, code)).start()
    # Redirect back with query param to show verification section
    return redirect('/forgot?verify=true')

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    input_code = data.get('code')
    if input_code == session.get('code'):
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect("/reset-password")

        user_email = session.get("email")
        if not user_email:
            flash("Session expired. Please restart the password reset process.")
            return redirect("/forgot")

        hashed_password = generate_password_hash(new_password)

        conn = get_db_connection()
        conn.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, user_email))
        conn.commit()
        conn.close()

        flash("Password reset successful! Please log in.")
        return redirect("/login")

    # GET request: just show the reset form
    return render_template("reset.html")

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

        conn    = get_db_connection()
        user    = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"]    = user["username"]
            session["chips"]       = user["chips"]
            session["login_alert"] = True   # set the flag
            return redirect("/")           # literal path

        flash("Invalid username or password.")
        return redirect("/login")         # literal path

    # just render the form on GET
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
