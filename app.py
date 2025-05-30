import os, sys
from flask import Flask, render_template, request, redirect, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, ssl
from email.message import EmailMessage
import random
from secure import EMAIL_PASS_SECURE
from Back.black_logic import BlackjackMultiGame


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
    message["From"]      = sender_email
    message["To"]        = to_email
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
@app.route('/api/start_game', methods=['POST'])
def start_game():
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    player_username = session.get("username")
    # Retrieve chips from the session for the game's initial state
    # This value comes from the database when the user logs in
    player_chips = session.get("chips", 10000)

    # Initialize a new multi-hand game with the player's current chips and 3 hands
    game = BlackjackMultiGame(player_username, initial_chips=player_chips, num_hands=3)
    game.reset_round() # Ensure a clean slate for the new game

    # Store the entire game state dictionary in the session
    session["blackjack_game_state"] = game.to_dict()

    # Send initial game state to frontend (dealer card hidden initially)
    return jsonify({"success": True, "game_state": game.get_game_state(reveal_dealer_card=False)})


@app.route('/api/place_bets', methods=['POST'])
def place_bets():
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    # Reconstruct the game object from the session state
    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    bets_data = request.json.get("bets") # Expects a list of bet objects, one for each hand

    # Attempt to place bets
    if not game.place_bets(bets_data):
        # Update session even on failure so the frontend gets the error message
        session["blackjack_game_state"] = game.to_dict()
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})

    # If bets placed successfully, deal initial cards
    if not game.deal_initial_cards():
        # Update session if dealing fails (e.g., unexpected internal error)
        session["blackjack_game_state"] = game.to_dict()
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})

    # Save the updated game state back to the session
    session["blackjack_game_state"] = game.to_dict()

    # Determine if dealer's second card should be revealed
    # This happens if the game immediately transitions to round_over (e.g., dealer blackjack)
    reveal_dealer = game.game_phase in ["round_over"] # Dealer's hand should be revealed only if round is over

    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=reveal_dealer)})


@app.route('/api/player_action', methods=['POST'])
def player_action():
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    action_type = request.json.get("action")
    hand_index = request.json.get("hand_index") # Crucial for multi-hand: which hand is acted upon

    success = False
    if action_type == 'hit':
        success = game.hit(hand_index)
    elif action_type == 'stand':
        success = game.stand(hand_index)
    elif action_type == 'double': # Handle 'double down' action
        success = game.double_down(hand_index)
    # elif action_type == 'split': # Placeholder for future split functionality
    #     success = game.split(hand_index)
    else:
        game.game_message = "Invalid action."
        success = False

    if not success:
        session["blackjack_game_state"] = game.to_dict() # Save state with updated message
        return jsonify({"success": False, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})

    # After a player action, check if it's now the dealer's turn
    if game.game_phase == "dealer_turn":
        game.dealer_play() # Dealer performs their actions
        game.settle_all_bets() # Settle all hands once the dealer is done

    # Save the updated game state back to the session
    session["blackjack_game_state"] = game.to_dict()

    # Determine if dealer's hand should be revealed
    # It should be revealed once the dealer's turn starts or the round is over
    reveal_dealer = game.game_phase in ["dealer_turn", "settlement", "round_over"]

    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=reveal_dealer)})


@app.route('/api/reset_round', methods=['POST'])
def reset_round():
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "Game not started"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    game.reset_round() # Reset the game for a new round
    session["blackjack_game_state"] = game.to_dict() # Save the reset state

    return jsonify({"success": True, "message": game.game_message, "game_state": game.get_game_state(reveal_dealer_card=False)})


@app.route('/api/collect_chips', methods=['POST'])
def collect_chips():
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    if "blackjack_game_state" not in session:
        return jsonify({"success": False, "message": "No active game"}), 400

    game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    player_username = session["username"]
    final_chips = game.player.chips # Get the current chips from the game instance

    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET chips = ? WHERE username = ?", (final_chips, player_username))
        conn.commit()
        session["chips"] = final_chips # Update chips in Flask session as well
        return jsonify({"success": True, "message": "Chips collected and saved!", "new_chips": final_chips})
    except Exception as e:
        flash(f"Error saving chips: {e}")
        return jsonify({"success": False, "message": "Failed to save chips."}), 500
    finally:
        conn.close()


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
    game_state_for_display = None

    # Check if a game state exists in the session
    if "blackjack_game_state" in session:
        try:
            # Reconstruct the game object
            game_obj = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
            # Get the state dictionary to pass to the template
            game_state_for_display = game_obj.get_game_state(reveal_dealer_card=False) # Keep dealer card hidden on initial load
        except Exception as e:
            print(f"Error loading game from session in /game route: {e}")
            session.pop('blackjack_game_state', None) # Clear corrupted session data
            # Optionally, you might want to initialize a new game here or redirect to home/start_game
            # For now, if loading fails, game_state_for_display remains None, which default(0) in template handles.
    
    # If no game state in session, or if loading failed, create a placeholder
    # This ensures game_state is always defined when rendering the template.
    if game_state_for_display is None:
        # Create a default game state to avoid Jinja2 errors
        # This is a minimal representation to satisfy the template's initial needs
        # Player chips will be 0, num_hands will be 0 or a default you prefer
        game_state_for_display = {
            "player_chips": session.get("chips", 0), # Use stored chips from login if available
            "game_phase": "betting",
            "game_message": "Place your bets!",
            "dealer_hand": [],
            "dealer_total": 0,
            "player_hands": [], # Empty list for hands if no game active
            "num_hands": 3 # Default number of hands for the template loop
        }


    return render_template("game.html", fullscreen=fullscreen, game_state=game_state_for_display)


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
            session["username"]     = user["username"]
            session["chips"]        = user["chips"]
            session["login_alert"]  = True   # set the flag
            return redirect("/")             # literal path

        flash("Invalid username or password.")
        return redirect("/login")            # literal path

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
    (email, username, hashed_password, 1000000)   # Starting chips
        )
        conn.commit()
        conn.close()

        flash('''Registration successful! 
              You can now log in.''')
        return redirect('/login')

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)