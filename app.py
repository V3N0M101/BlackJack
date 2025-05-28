from flask import Flask, render_template, request, jsonify
from Back.Game.black_logic import BlackjackGame

app = Flask(__name__, template_folder='Front/Pages', static_folder='Front')

# Create one game instance
game = BlackjackGame()

@app.route('/')
def home():
    return render_template('main.html')
@app.route('/blackjack')
def blackjack():
    return render_template('game.html')

@app.route('/deal', methods=['POST'])
def deal():
    result = game.deal()
    return jsonify(result)

@app.route('/hit', methods=['POST'])
def hit():
    result = game.hit()
    return jsonify(result)

@app.route('/stand', methods=['POST'])
def stand():
    result = game.stand()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
