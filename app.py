import os, sys
from flask import Flask, render_template

# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

app = Flask(__name__)

# Define routes for your HTML pages
@app.route("/")
def home():
    return render_template("main.html")

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/navbar")
def navbar():
    return render_template("navbar.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)
