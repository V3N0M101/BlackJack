import os, sys
from flask import Flask, render_template

# so you can `import deck, player, Black_logic` directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Back'))

app = Flask(
    __name__,
    static_folder='Front',                # serve all sub-dirs (images/, scripts/, stylesheets/) as “static”
    static_url_path='',
    template_folder=os.path.join('Front','pages')
)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

if __name__ == '__main__':
    app.run(debug=True)
