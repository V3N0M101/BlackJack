import os, sys
from flask import Flask, render_template, request, redirect, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, ssl
from email.message import EmailMessage
import random
import threading

# It's assumed 'secure.py' exists and contains EMAIL_PASS_SECURE
from secure import EMAIL_PASS_SECURE 

# It's assumed 'Black_logic.py' exists within the 'Back' directory
from Back.black_logic import BlackjackMultiGame

# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

def send_verification_email(to_email: str, code: str, username: str = ""):
    """
    Sends a verification email with a given code.
    The username parameter is optional and can be used to personalize the email.
    """
    sender_email = "blackhub420@gmail.com"
    app_password = EMAIL_PASS_SECURE

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = to_email
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
    # MODIFIED: Use app.root_path to get the absolute path to your project directory
    db_path = os.path.join(app.root_path, 'users.db')
    conn = sqlite3.connect(db_path) 
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to save chips to the database
def save_chips_to_db(username, chips):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET chips = ? WHERE username = ?", (chips, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving chips for {username}: {e}")
        return False
    finally:
        conn.close()

    
## API Routes for Blackjack Game

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """
    Initializes a new Blackjack game for the logged-in user.
    Requires the user to be logged in.
    """
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    player_username = session.get("username")
    player_chips = session.get("chips", 10000)  # Default chips if not found in session

    # Always initialize with 3 hands when starting a new game
    game = BlackjackMultiGame(player_username, initial_chips=player_chips, num_hands=3)
    game.reset_round()  

    session["blackjack_game_state"] = game.to_dict()

    return jsonify({"success": True, "game_state": game.get_game_state(reveal_dealer_card=False)})


@app.route('/api/place_bets', methods=['POST'])
def place_bets():
    """
    Allows the player to place bets for each hand.
    Requires an active game session.
    """
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    bets_data = request.json.get("bets")

    if not game.place_bets(bets_data):
        session["blackjack_game_state"] = game.to_dict()
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})
    
    # Store the placed bets in session for rebet functionality
    # We only store the main_bet, side_bet_21_3, and side_bet_perfect_pair
    session['last_bets'] = [
        {
            "main_bet": hand_data["main_bet"],
            "side_21_3": hand_data["side_bet_21_3"],
            "side_pp": hand_data["side_bet_perfect_pair"]
        } for hand_data in game.player_hands
    ]

    if not game.deal_initial_cards():
        session["blackjack_game_state"] = game.to_dict()
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})

    session["blackjack_game_state"] = game.to_dict()

    reveal_dealer = game.game_phase in ["round_over"]
    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=reveal_dealer)})

@app.route('/api/rebet', methods=['POST'])
def rebet():
    """
    Resets the current round and retrieves the last placed bets.
    Requires an active game session.
    """
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])

    # Before resetting, ensure chips are saved if the previous round ended
    if game.game_phase == "round_over":
        player_username = session["username"]
        final_chips = game.player.chips
        if save_chips_to_db(player_username, final_chips):
            session["chips"] = final_chips
            game.game_message = "Chips saved! " + game.game_message
        else:
            game.game_message = "Failed to save chips before rebet. " + game.game_message

    # Get the last saved bets *before* resetting the game state
    last_bets_from_session = session.get('last_bets', [])

    # Reset the round on the *existing* game object
    # This will clear the hands and set game_phase to "betting"
    # and reinitialize with the correct number of hands
    game.reset_round() 
    
    # After resetting, apply the last_bets to the game's player_hands
    # Ensure that last_bets_from_session has data for all hands
    if last_bets_from_session and len(last_bets_from_session) == game.num_hands:
        for i, hand_data in enumerate(game.player_hands):
            if i < len(last_bets_from_session):
                hand_data["main_bet"] = last_bets_from_session[i].get("main_bet", 0)
                hand_data["side_bet_21_3"] = last_bets_from_session[i].get("side_21_3", 0)
                hand_data["side_bet_perfect_pair"] = last_bets_from_session[i].get("side_pp", 0)
        game.game_message += " Previous bets loaded!"
    else:
        game.game_message += " No previous bets to load or inconsistent number of hands."

    session["blackjack_game_state"] = game.to_dict()

    return jsonify({
        "success": True,
        "message": game.game_message,
        "game_state": game.get_game_state(reveal_dealer_card=False),
        "last_bets": last_bets_from_session # Include last_bets in the response
    })


@app.route('/api/player_action', methods=['POST'])
def player_action():
    """
    Processes player actions (hit, stand, double).
    Requires an active game session.
    """
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    action_type = request.json.get("action")
    hand_index = request.json.get("hand_index")

    success = False
    if action_type == 'hit':
        success = game.hit(hand_index)
    elif action_type == 'stand':
        success = game.stand(hand_index)
    elif action_type == 'double':
        success = game.double_down(hand_index)
    elif action_type == 'split': # NEW: Handle split action
        success = game.split(hand_index)
    else:
        game.game_message = "Invalid action."
        success = False

    if not success:
        session["blackjack_game_state"] = game.to_dict()
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})

    if game.game_phase == "dealer_turn":
        game.dealer_play()
        game.settle_all_bets()
        player_username = session["username"]
        final_chips = game.player.chips
        if save_chips_to_db(player_username, final_chips):
            session["chips"] = final_chips # Update session chips after saving
            game.game_message += " Chips saved!"
        else:
            game.game_message += " Failed to save chips."

    session["blackjack_game_state"] = game.to_dict()

    reveal_dealer = game.game_phase in ["dealer_turn", "settlement", "round_over"]
    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=reveal_dealer)})


@app.route('/api/reset_round', methods=['POST'])
def reset_round():
    """
    Resets the current round of the Blackjack game, allowing new bets.
    Requires an active game session.
    """
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    # Before resetting, ensure chips are saved if the previous round ended
    if game.game_phase == "round_over":
        player_username = session["username"]
        final_chips = game.player.chips
        if save_chips_to_db(player_username, final_chips):
            session["chips"] = final_chips # Update session chips after saving
            game.game_message = "Chips saved! " + game.game_message # Prepend message
        else:
            game.game_message = "Failed to save chips before reset. " + game.game_message
    
    # Reinitialize the game with 3 hands when resetting the round
    player_username = session.get("username")
    player_chips = game.player.chips # Use current chips
    game = BlackjackMultiGame(player_username, initial_chips=player_chips, num_hands=3)
    game.reset_round()
    
    session["blackjack_game_state"] = game.to_dict()

    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})


@app.route('/api/collect_chips', methods=['POST'])
def collect_chips():
    """
    Saves the player's current chip count from the game to the database.
    Requires the user to be logged in and an active game session.
    """
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "No active game"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    player_username = session["username"]
    final_chips = game.player.chips

    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET chips = ? WHERE username = ?", (final_chips, player_username))
        conn.commit()
        session["chips"] = final_chips
        return jsonify({"success": True, "message": "Chips collected and saved!", "new_chips": final_chips})
    except Exception as e:
        flash(f"Error saving chips: {e}")
        return jsonify({"success": False, "message": "Failed to save chips."}), 500
    finally:
        conn.close()

## HTML Page Routes

@app.route("/")
def home():
    """
    Renders the main home page.
    Displays a login alert if a user just logged in.
    """
    login_in_alert = session.pop("login_alert", False)
    return render_template(
        "main.html",
        logged_in="username" in session,
        login_in_alert=login_in_alert,
    )
    

@app.route("/game")
def game():
    """
    Renders the Blackjack game page.
    Loads existing game state from the session or provides a default.
    """
    fullscreen = request.args.get("fullscreen", "").lower() == "true"
    game_state_for_display = None

    if "blackjack_game_state" in session:
        try:
            game_obj = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
            # Ensure the number of hands for display is pulled from the game object,
            # or defaulted to 3 if starting fresh.
            game_state_for_display = game_obj.get_game_state(reveal_dealer_card=False)
            game_state_for_display["num_hands"] = game_obj.num_hands # Ensure num_hands is set
        except Exception as e:
            print(f"Error loading game from session in /game route: {e}")
            session.pop('blackjack_game_state', None)

    if game_state_for_display is None:
        game_state_for_display = {
            "player_chips": session.get("chips", 0),
            "game_phase": "betting",
            "game_message": "Place your bets!",
            "dealer_hand": [],
            "dealer_total": 0,
            "player_hands": [],
            "num_hands": 3 # Default to 3 hands for new games
        }

    return render_template("game.html", fullscreen=fullscreen, game_state=game_state_for_display)


@app.route("/email")
def email():
    """Renders the email page (likely for contact or info)."""
    return render_template("email.html")

@app.route("/forgot")
def forgot():
    """Renders the 'forgot password' page."""
    return render_template("forgot.html")

@app.route('/send-reset-code', methods=['POST'])
def send_reset_code():
    """
    Sends a password reset verification code to the provided email.
    The code is stored in the session.
    """
    email = request.form['email']
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    session['email'] = email
    session['code'] = code
    
    # Send email in background to avoid lag
    threading.Thread(target=send_verification_email, args=(email, code)).start()
    
    return redirect('/forgot?verify=true')

@app.route('/verify-code', methods=['POST'])
def verify_code():
    """
    Verifies the provided reset code against the one stored in the session.
    """
    data = request.get_json()
    input_code = data.get('code')
    if input_code == session.get('code'):
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """
    Handles password reset functionality.
    Allows a user to set a new password after successful code verification.
    """
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

    return render_template("reset.html")

@app.route("/leaderboard")
def leaderboard():
    """
    Renders the leaderboard page, displaying users ranked by their chips.
    """
    conn = get_db_connection()
    # Fetch users ordered by chips in descending order, limit to top 10 for example
    # You can adjust the LIMIT as needed.
    users = conn.execute("SELECT username, chips FROM users ORDER BY chips DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("leaderboard.html", users=users)

@app.route("/learn")
def learn():
    """Renders the 'learn' page (presumably for game rules or tutorials)."""
    return render_template("learn.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    Authenticates users against the database and sets session variables upon successful login.
    """
    logout_alert = session.pop("logout_alert", False)
    register_alert = session.pop("register_alert", False)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["chips"] = user["chips"]
            session["login_alert"] = True
            return redirect("/")
        
        return render_template(
            "login.html",
            alert_message="Invalid username or password.",
            logout_alert=logout_alert,
            register_alert=register_alert
        )

    return render_template("login.html", logout_alert=logout_alert, register_alert=register_alert)


@app.route("/navbar")
def navbar():
    """Renders the navigation bar component."""
    return render_template("navbar.html")

@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.
    Redirects to the login page with a logout alert.
    """
    session.clear()
    session["logout_alert"] = True
    return redirect("/login")

@app.route("/news")
def news():
    """Renders the news page."""
    return render_template("news.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    Validates input, checks for existing users, and initiates email verification.
    """
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validations
        if not email or not username or not password or not confirm_password:
            return render_template('register.html', alert_message='Please fill out all fields.')

        if password != confirm_password:
            return render_template('register.html', alert_message='Passwords do not match.')

        if len(username) > 16:
            return render_template('register.html', alert_message='Please pick a username with 16 or fewer characters.')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            return render_template('register.html', alert_message='Username or email already exists.')

        session['pending_user'] = {
            'email': email,
            'username': username,
            'password': password
        }

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        session['verify_code'] = code
        
        # Pass username to send_verification_email for personalization
        threading.Thread(target=send_verification_email, args=(email, code, username)).start()

        return redirect('/verify')

    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """
    Handles email verification during registration.
    If successful, the user's account is created in the database.
    """
    if request.method == 'POST':
        code_input = ''.join([request.form.get(f'd{i}', '') for i in range(1, 7)])
        actual_code = session.get('verify_code')

        if code_input == actual_code:
            user = session.pop('pending_user', None)
            session.pop('verify_code', None)

            if not user:
                return redirect('/register')

            hashed_password = generate_password_hash(user['password'])
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (email, username, password, chips) VALUES (?, ?, ?, ?)",
                (user['email'], user['username'], hashed_password, 10000) # Starting chips for new users
            )
            conn.commit()
            conn.close()

            session["register_alert"] = True
            return redirect('/login')
        else:
            return render_template('verify.html', alert_message="Incorrect verification code.")

    return render_template('verify.html')


if __name__ == '__main__':
    app.run(debug=True)