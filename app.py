import os, sys, json
from flask import Flask, render_template, request, redirect, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, ssl
from email.message import EmailMessage
import random
import threading
from datetime import datetime, timedelta, timezone

# It's assumed 'secure.py' exists and contains EMAIL_PASS_SECURE
from secure import EMAIL_PASS_SECURE 

# It's assumed 'Black_logic.py' exists within the 'Back' directory
from Back.black_logic import BlackjackMultiGame
BONUS_COOLDOWN_SECONDS = 120
BONUS_AMOUNT = 10000

# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

def send_verification_email(to_email: str, code: str, username: str = "", email_type: str = "verification"):
    """
    Sends a verification email with a given code.
    The username parameter is optional and can be used to personalize the email.
    The email_type parameter determines the subject and content.
    """
    sender_email = "blackhub420@gmail.com"
    app_password = EMAIL_PASS_SECURE

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = to_email
    
    if email_type == "reset":
        message["Subject"] = "Your Password Reset Code"
        email_body = (
            f"Hi {username if username else to_email},\n\n"
            f"Your password reset code is: {code}\n\n"
            "If you didn't request this, just ignore this email."
        )
    else: # Default to "verification"
        message["Subject"] = "Verify Your BlackJack Account"
        email_body = (
            f"Hi {username if username else to_email},\n\n"
            f"Your account verification code is: {code}\n\n"
            "Please use this code to complete your registration."
        )

    message.set_content(email_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, app_password)
        server.send_message(message)

app = Flask(__name__)
app.secret_key = 'secretkey123'  # required for sessions, flash, etc.

@app.context_processor
def inject_custom_message():
    """Injects custom message variables into template context if they exist in session."""
    context = {}
    if 'show_custom_message_on_redirect' in session:
        context['show_custom_message'] = session.pop('show_custom_message_on_redirect')
        context['custom_message_content'] = session.pop('custom_message_content_on_redirect', 'Message not found.')
    # Note: Direct render_template calls will pass these explicitly, not via session for this processor part.
    return context

# users.db 
def get_db_connection():
    # MODIFIED: Use app.root_path to get the absolute path to your project directory
    db_path = os.path.join(app.root_path, 'users.db')
    conn = sqlite3.connect(db_path) 
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to save chips to the database
def save_chips_to_db(username, chips, update_bonus_time=False):
    conn = get_db_connection()
    try:
        if update_bonus_time:
            # Format current UTC time for SQLite TEXT storage
            now_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute("UPDATE users SET chips = ?, last_bonus_collection = ? WHERE username = ?", (chips, now_utc, username))
        else:
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
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    player_username = session["username"]
    conn = get_db_connection() # Crucial for getting user data from DB
    try:
        user_data = conn.execute("SELECT chips, last_bonus_collection FROM users WHERE username = ?", (player_username,)).fetchone()
        if not user_data:
            return jsonify({"success": False, "message": "User not found."}), 404

        player_chips = user_data["chips"] # Get actual chips from DB
        last_bonus_collection_str = user_data["last_bonus_collection"]

        # --- LOAD EXISTING GAME OR CREATE NEW ONE ---
        if "blackjack_game_state" in session:
            # Load existing ongoing game to preserve state across page reloads/fullscreen toggles
            game = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
            game.player.chips = player_chips  # Keep chips in sync with latest DB value
            game.game_message = "Game resumed." if game.game_phase not in ["betting", "round_over"] else game.game_message
        else:
            # No existing game – start a fresh one in betting phase
            game = BlackjackMultiGame(player_username, initial_chips=player_chips, num_hands=3)
            game.game_message = "New game started. Place your bets!"
        session["blackjack_game_state"] = game.to_dict()

        # --- THIS BLOCK CALCULATES BONUS STATUS ---
        last_collection_time = datetime.strptime(last_bonus_collection_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        next_collection_time = last_collection_time + timedelta(seconds=BONUS_COOLDOWN_SECONDS)
        now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

        can_collect = now_utc >= next_collection_time
        bonus_cooldown_message = ""
        next_bonus_time_iso = None

        if can_collect:
            bonus_cooldown_message = "Bonus available!"
            next_bonus_time_iso = None # If bonus is available, there's no "next" time in the future
        else:
            time_remaining = next_collection_time - now_utc
            total_seconds = int(time_remaining.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            bonus_cooldown_message = f"Next bonus in {hours}h {minutes}m {seconds}s."
            next_bonus_time_iso = next_collection_time.isoformat() # <--- Crucial for frontend countdown

        current_game_state = game.get_game_state(reveal_dealer_card=False)
        current_game_state["can_collect_bonus"] = can_collect
        current_game_state["next_bonus_time"] = next_bonus_time_iso
        current_game_state["bonus_cooldown_message"] = bonus_cooldown_message
        current_game_state["player_chips"] = player_chips # Ensure this is always accurate

        initial_message = game.game_message or "Game started/loaded."

        return jsonify({
            "success": True,
            "message": initial_message,
            "game_state": current_game_state
        })
    except Exception as e:
        print(f"Error starting game for {player_username}: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500
    finally:
        conn.close()

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
    # Always store 3 hands (pad with zeros if needed)

    player_username = session["username"]
    if not save_chips_to_db(player_username, game.player.chips):
        return jsonify({"success": False, "message": "Failed to save chips after betting.", "game_state": game.get_game_state(reveal_dealer_card=False)}), 500
    session["chips"] = game.player.chips  # Also update session chips

    bets_for_last_bets = [
        {
            "main_bet": hand_data["main_bet"],
            "side_21_3": hand_data["side_bet_21_3"],
            "side_pp": hand_data["side_bet_perfect_pair"]
        } for hand_data in game.player_hands
    ]
    while len(bets_for_last_bets) < 3:
        bets_for_last_bets.append({"main_bet": 0, "side_21_3": 0, "side_pp": 0})
    session['last_bets'] = bets_for_last_bets

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

    # Always use 3 hands for betting phase
    game.num_hands = 3

    # Get the last saved bets *before* resetting the game state
    last_bets_from_session = session.get('last_bets', [])

    # Pad last_bets_from_session to always have 3 entries
    while len(last_bets_from_session) < 3:
        last_bets_from_session.append({"main_bet": 0, "side_21_3": 0, "side_pp": 0})

    # Reset the round on the *existing* game object
    game.reset_round()

    # After resetting, apply the last_bets to the game's player_hands
    for i, hand_data in enumerate(game.player_hands):
        if i < len(last_bets_from_session):
            hand_data["main_bet"] = last_bets_from_session[i].get("main_bet", 0)
            hand_data["side_bet_21_3"] = last_bets_from_session[i].get("side_21_3", 0)
            hand_data["side_bet_perfect_pair"] = last_bets_from_session[i].get("side_pp", 0)
    game.game_message += " Previous bets loaded!"
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


# app.py

# ... (rest of your imports and setup) ...

@app.route('/api/collect_chips', methods=['POST'])
def collect_chips():
    """
    Allows the player to collect a daily bonus.
    Checks the 24-hour cooldown and updates chips and last_bonus_collection timestamp.
    """
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    player_username = session["username"]

    conn = get_db_connection()
    try:
        user_data = conn.execute("SELECT chips, last_bonus_collection FROM users WHERE username = ?", (player_username,)).fetchone()

        if not user_data:
            return jsonify({"success": False, "message": "User not found."}), 404

        current_chips = user_data["chips"]
        last_collection_str = user_data["last_bonus_collection"]

        last_collection_time = datetime.strptime(last_collection_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        next_collection_time = last_collection_time + timedelta(seconds=BONUS_COOLDOWN_SECONDS)
        now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

        GRACE_PERIOD_SECONDS = 2 # Use consistent naming, e.g., GRACE_PERIOD_SECONDS

        # --- Initialize bonus related variables for the response ---
        can_collect_bonus_response = False
        next_bonus_time_iso_response = None
        bonus_cooldown_message_response = ""

        # Load game state if available, so we can send a complete game_state object
        # even if only chips changed.
        game = BlackjackMultiGame.from_dict(session.get("blackjack_game_state", {}))
        game.player.chips = current_chips # Ensure current chips are accurate in the game object

        # --- APPLY THE GRACE PERIOD LOGIC HERE ---
        # Eligibility check: now_utc must be greater than or equal to next_collection_time,
        # OR within the grace period (meaning, next_collection_time is still in the very near future
        # or has just passed by a small amount).
        
        # Calculate the "earliest" time a user can collect with grace period
        eligible_time_with_grace = next_collection_time - timedelta(seconds=GRACE_PERIOD_SECONDS)

        if now_utc >= eligible_time_with_grace:
            # Player is eligible to collect bonus (either on time or within grace period)

            # Important: Confirm it's not too far in the future due to extreme client clock drift
            # or if the bonus is *actually* past its collection time and we're just handling latency.
            # If now_utc is significantly BEFORE next_collection_time (i.e., not just grace period),
            # then it's still not eligible. This ensures the grace period doesn't allow early collection.
            if now_utc < next_collection_time - timedelta(seconds=GRACE_PERIOD_SECONDS): # If it's *still* more than grace period away
                 # This should ideally not be hit if the frontend countdown is mostly accurate
                 # But it's a safety net for large client clock discrepancies
                 time_remaining = next_collection_time - now_utc
                 hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                 minutes, seconds = divmod(remainder, 60)
                 message = f"You can collect your bonus in {int(hours)}h {int(minutes)}m {int(seconds)}s. (Please wait for countdown)"
                 
                 can_collect_bonus_response = False
                 next_bonus_time_iso_response = next_collection_time.isoformat()
                 bonus_cooldown_message_response = f"Next bonus in {int(hours)}h {int(minutes)}m {int(seconds)}s."
                 
                 return jsonify({
                    "success": False,
                    "message": message,
                    "game_state": {
                        **game.get_game_state(reveal_dealer_card=False),
                        "player_chips": current_chips,
                        "can_collect_bonus": can_collect_bonus_response,
                        "next_bonus_time": next_bonus_time_iso_response,
                        "bonus_cooldown_message": bonus_cooldown_message_response
                    }
                 }), 400

            # If we reached here, the player is truly eligible with grace
            new_chips = current_chips + BONUS_AMOUNT
            
            # Update chips and the last_bonus_collection timestamp in the database
            if save_chips_to_db(player_username, new_chips, update_bonus_time=True):
                session["chips"] = new_chips # Update chips in Flask session
                
                # Update game object with new chips
                game.player.chips = new_chips
                session["blackjack_game_state"] = game.to_dict() # Save updated game state

                message = f"Bonus of ${BONUS_AMOUNT} collected! Your new balance is ${new_chips}."

                # --- Set bonus status for the response after collection ---
                can_collect_bonus_response = False # Just collected, so now on cooldown
                new_next_collection_time_after_bonus = now_utc + timedelta(seconds=BONUS_COOLDOWN_SECONDS)
                next_bonus_time_iso_response = new_next_collection_time_after_bonus.isoformat()
                
                # Recalculate message based on the new cooldown
                time_remaining = new_next_collection_time_after_bonus - now_utc
                hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                # Ensure seconds are not negative in message
                seconds = max(0, int(seconds)) 
                bonus_cooldown_message_response = f"Next bonus in {int(hours)}h {int(minutes)}m {int(seconds)}s."
                
                return jsonify({
                    "success": True,
                    "message": message,
                    "game_state": {
                        **game.get_game_state(reveal_dealer_card=False),
                        "player_chips": new_chips,
                        "can_collect_bonus": can_collect_bonus_response,
                        "next_bonus_time": next_bonus_time_iso_response,
                        "bonus_cooldown_message": bonus_cooldown_message_response
                    }
                })
            else:
                message = "Failed to update chips in the database."
                return jsonify({"success": False, "message": message}), 500
        else:
            # Player is not yet eligible (outside of grace period)
            time_remaining = next_collection_time - now_utc
            hours, remainder = divmod(time_remaining.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # --- Set bonus status for the response when not eligible ---
            can_collect_bonus_response = False
            next_bonus_time_iso_response = next_collection_time.isoformat() # This is the key!
            # Ensure seconds are not negative in message
            seconds = max(0, int(seconds)) 
            bonus_cooldown_message_response = f"Next bonus in {int(hours)}h {int(minutes)}m {int(seconds)}s."

            message = f"You can collect your bonus in {int(hours)}h {int(minutes)}m {int(seconds)}s."
            return jsonify({
                "success": False,
                "message": message,
                "game_state": {
                    **game.get_game_state(reveal_dealer_card=False), # Include other game state
                    "player_chips": current_chips,
                    "can_collect_bonus": can_collect_bonus_response,
                    "next_bonus_time": next_bonus_time_iso_response,
                    "bonus_cooldown_message": bonus_cooldown_message_response
                }
            }), 400 # Indicate bad request/not eligible
    except Exception as e:
        print(f"Error collecting bonus chips for {player_username}: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500
    finally:
        conn.close()

## HTML Page Routes

@app.route("/")
def home():
    """
    Renders the main home page.
    Displays a login alert if a user just logged in.
    """
    logged_in_status = "username" in session
    login_in_alert = session.pop("login_alert", False)
    first_login = session.pop("first_login", False)  # Get and clear first login flag
    
    return render_template(
        "main.html",
        logged_in=logged_in_status,
        login_in_alert=login_in_alert,
        first_login=first_login
    )
    
@app.route("/game")
def game():
    """
    Renders the Blackjack game page, preserving any existing game state (e.g., when toggling fullscreen). A new game is created only if none exists.
    """
    fullscreen = request.args.get("fullscreen", "").lower() == "true"

    # Retrieve existing game state if present; otherwise start a new one
    if "blackjack_game_state" in session:
        game_obj = BlackjackMultiGame.from_dict(session["blackjack_game_state"])
    else:
        initial_chips = session.get("chips", 1000)
        player_username = session.get("username", "Player")
        game_obj = BlackjackMultiGame(player_username, initial_chips=initial_chips, num_hands=3)
        game_obj.reset_round()

    # Persist (or update) the game state in the session
    session["blackjack_game_state"] = game_obj.to_dict()
    # Prepare game state for template
    game_state_for_display = game_obj.get_game_state(reveal_dealer_card=False)
    game_state_for_display["num_hands"] = game_obj.num_hands

    # --- Bonus logic (optional, keep as in your original code) ---
    if "username" in session:
        conn = get_db_connection()
        user_data = conn.execute("SELECT last_bonus_collection FROM users WHERE username = ?", (session["username"],)).fetchone()
        conn.close()

        if user_data:
            last_bonus_collection_str = user_data["last_bonus_collection"]
            if last_bonus_collection_str:
                last_collection_time = datetime.strptime(last_bonus_collection_str, '%Y-%m-%d %H:%M:%S')
                last_collection_time = last_collection_time.replace(tzinfo=timezone.utc)
                next_collection_time = last_collection_time + timedelta(seconds=BONUS_COOLDOWN_SECONDS)
                now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

                game_state_for_display["can_collect_bonus"] = now_utc >= next_collection_time
                game_state_for_display["next_bonus_time"] = next_collection_time.isoformat()

                if not game_state_for_display["can_collect_bonus"]:
                    time_remaining = next_collection_time - now_utc
                    total_seconds_remaining = int(time_remaining.total_seconds())
                    hours = total_seconds_remaining // 3600
                    remainder = total_seconds_remaining % 3600
                    minutes = remainder // 60
                    seconds = remainder % 60
                    game_state_for_display["bonus_cooldown_message"] = f"Next bonus in {hours:02}h {minutes:02}m {seconds:02}s."
                else:
                    game_state_for_display["bonus_cooldown_message"] = "Bonus available!"
            else:
                game_state_for_display["can_collect_bonus"] = True
                game_state_for_display["bonus_cooldown_message"] = "Bonus available!"
                game_state_for_display["next_bonus_time"] = None
        else:
            game_state_for_display["can_collect_bonus"] = True
            game_state_for_display["bonus_cooldown_message"] = "Bonus available!"
            game_state_for_display["next_bonus_time"] = None

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
    
    conn = get_db_connection()
    user = conn.execute("SELECT username FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user:
        return jsonify({
            'success': False,
            'message': 'No account found with this email address.'
        })

    username = user['username']
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    session['reset_email'] = email
    session['reset_code'] = code
    
    # Send email in background to avoid lag
    threading.Thread(target=send_verification_email, args=(email, code, username, "reset")).start()
    
    return jsonify({
        'success': True,
        'message': 'Password reset link sent'
    })

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """
    Verifies the provided reset code against the one stored in the session.
    """
    data = request.get_json()
    input_code = data.get('code')
    
    # Use distinct session keys for reset flow
    if input_code == session.get('reset_code'):
        # Code matches, user is now allowed to reset password.
        # Don't pop 'reset_code' yet, as the user might need it to proceed to reset-password page
        # where the email is retrieved from session for the update query.
        return jsonify({'success': True})
    
    # Flash message for incorrect code for the password reset flow
    flash('Incorrect verification code. Please try again.')
    return jsonify({'success': False, 'message': 'Incorrect verification code.'}), 400

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """
    Handles password reset functionality.
    Allows a user to set a new password after successful code verification.
    """
    if request.method == "GET":
        # Ensure they have gone through the verification step for reset
        if 'reset_email' not in session:
            return jsonify({
                "success": False,
                "message": "Please initiate the password reset process first."
            }), 400
        return render_template("reset.html")

    # POST request handling
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    user_email = session.get("reset_email")
    if not user_email:
        return jsonify({
            "success": False,
            "message": "Session expired. Please restart the password reset process."
        }), 400

    try:
        hashed_password = generate_password_hash(new_password)
        conn = get_db_connection()
        conn.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, user_email))
        conn.commit()
        conn.close()

        # Clear reset session data
        session.pop('reset_email', None)
        session.pop('reset_code', None)

        return jsonify({
            "success": True,
            "message": "Your password has been reset"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred while resetting your password."
        }), 500

@app.route("/logged_out_page") # New route
def logged_out_page():
    """Renders the page that displays the 'not logged in' image."""
    return render_template("logged_out_display.html")

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
    login_in_alert = session.pop("login_alert", False)
    return render_template(
        "learn.html",
        logged_in="username" in session,
        login_in_alert=login_in_alert,
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    Authenticates users against the database and sets session variables upon successful login.
    """
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
            session["first_login"] = True  # Set first login flag
            
            # Restore game state if it exists
            try:
                if "game_state" in user.keys() and user["game_state"]:
                    game_state = json.loads(user["game_state"])
                    session["blackjack_game_state"] = game_state
            except Exception as e:
                print(f"Error restoring game state for {username}: {e}")
                
            return jsonify({"success": True, "message": "Login successful"})
        
        return jsonify({"success": False, "message": "Invalid username or password"})

    logout_alert = session.pop("logout_alert", False)
    register_alert = session.pop("register_alert", False)
    return render_template("login.html", logout_alert=logout_alert, register_alert=register_alert)


@app.route("/navbar")
def navbar():
    """Renders the navigation bar component."""
    return render_template("navbar.html")

@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.
    Saves the game state to the database before logging out.
    Redirects to the home page with a custom logout message.
    """
    # Save game state to database if it exists
    if "username" in session and "blackjack_game_state" in session:
        username = session["username"]
        game_state = json.dumps(session["blackjack_game_state"])
        conn = get_db_connection()
        try:
            # Check if game_state column exists, if not add it
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if "game_state" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN game_state TEXT")
                conn.commit()
            
            # Save game state
            conn.execute("UPDATE users SET game_state = ? WHERE username = ?", (game_state, username))
            conn.commit()
        except Exception as e:
            print(f"Error saving game state for {username}: {e}")
        finally:
            conn.close()
    
    session.clear()
    # Set custom message for display on the target page (main.html via home route)
    session['show_custom_message_on_redirect'] = True
    session['custom_message_content_on_redirect'] = "Logged out successfully"
    return redirect("/") # Redirect to home page to display message on main.html

@app.route("/news")
def news():
    """Renders the news page."""
    login_in_alert = session.pop("login_alert", False)
    return render_template(
        "news.html",
        logged_in="username" in session,
        login_in_alert=login_in_alert,
    )

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
            return jsonify({
                'success': False,
                'message': 'Please fill out all fields.'
            })

        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match.'
            })

        if len(username) > 16:
            return jsonify({
                'success': False,
                'message': 'Please pick a username with 16 or fewer characters.'
            })

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check username and email separately to give specific error messages
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        existing_username = cursor.fetchone()
        
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_email = cursor.fetchone()
        
        conn.close()

        if existing_username:
            return jsonify({
                'success': False,
                'message': 'Username/Email already exists'
            })
            
        if existing_email:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            })

        session['pending_user'] = {
            'email': email,
            'username': username,
            'password': password
        }

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        session['verify_code'] = code
        
        # Pass username to send_verification_email for personalization and specify type
        threading.Thread(target=send_verification_email, args=(email, code, username, "verification")).start()

        return jsonify({
            'success': True,
            'message': 'Registration initiated. Please check your email for verification.',
            'redirect_url': '/verify'
        })

    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """
    Handles email verification during registration.
    If successful, the user's account is created in the database.
    """
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request data."
            }), 400

        code_input = data.get('code', '')
        actual_code = session.get('verify_code')
        user_data = session.get('pending_user')

        if not actual_code or not user_data:
            return jsonify({
                "success": False,
                "message": "Verification session expired. Please register again."
            }), 400

        if code_input == actual_code:
            user = session.pop('pending_user', None)
            session.pop('verify_code', None)

            hashed_password = generate_password_hash(user['password'])
            conn = get_db_connection()
            try:
                initial_bonus_time = '1970-01-01 00:00:00'
                conn.execute(
                    "INSERT INTO users (email, username, password, chips, last_bonus_collection) VALUES (?, ?, ?, ?, ?)",
                    (user['email'], user['username'], hashed_password, 1000000000, initial_bonus_time)
                )
                conn.commit()
                conn.close()

                return jsonify({
                    "success": True,
                    "message": "Account verified successfully! You can now log in.",
                    "redirect_url": "/login"
                })
            except sqlite3.IntegrityError as e:
                conn.close()
                if "UNIQUE constraint failed" in str(e):
                    return jsonify({
                        "success": False,
                        "message": "Registration failed: Username or email already exists."
                    }), 400
                return jsonify({
                    "success": False,
                    "message": "An unexpected database error occurred."
                }), 500
            except Exception as e:
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "An unexpected error occurred."
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Wrong verification code entered"
            }), 400

    # For GET request to /verify
    if 'pending_user' not in session:
        return redirect('/register')

    return render_template('verify.html')


if __name__ == '__main__':
    app.run(debug=True)
