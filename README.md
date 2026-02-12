# BlackHub: Integrated Blackjack & Side-Bet Engine

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-orange?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styling-blue?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite&logoColor=white)

## Overview

BlackHub is a full-stack, web-based Blackjack simulation that delivers an authentic casino experience right in your browser. The platform goes beyond standard Blackjack by incorporating sophisticated side-bet mechanics, including Perfect Pairs and 21+3 variants, while maintaining the classic feel of traditional casino card games.

The application combines a robust Flask backend for game state management with a dynamic frontend interface. The design philosophy centers around a unique three-zone layout that allows players to monitor multiple aspects of gameplay simultaneously, creating an immersive and engaging user experience.

## Technical Setup

### Prerequisites

Before getting started, ensure you have Python 3.x installed on your system. The project dependencies are managed through pip and include Flask for the web framework along with database management libraries.

Install the required packages by running:

```bash
pip install -r requirements.txt
```

### Database Initialization

The application uses a local SQL database to store user profiles, manage bankrolls, and maintain leaderboard statistics. To set up the database schema, execute the initialization script:

```bash
python init_db.py
```

This will create the necessary tables and prepare the database for user registration and gameplay tracking.

### Running the Application

Launch the development server with the following command:

```bash
python3 app.py
```

Once the server is running, open your web browser and navigate to:

```
http://127.0.0.1:5000
```

You should see the BlackHub interface ready for gameplay.

## Architecture & Logic

The project follows object-oriented design principles to ensure reliable card dealing, accurate bet resolution, and seamless session management. The codebase is structured to separate concerns between game logic, user management, and interface rendering.

### System Design

The architecture consists of several key components:

- **Game Engine**: Handles card deck initialization, shuffling, dealing, and hand evaluation
- **Bet Resolution System**: Calculates payouts for main bets and side bets based on game outcomes
- **User Authentication**: Manages secure login and registration with password hashing
- **Session Management**: Maintains game state across requests using Flask sessions
- **Database Layer**: Stores persistent user data and leaderboard information

### Logic Flow

The typical game flow follows this pattern:

1. User authenticates and their bankroll is loaded from the database
2. Player places main bet and optional side bets (Perfect Pairs, 21+3)
3. Cards are dealt from a shuffled deck
4. Side bets are immediately evaluated and resolved
5. Player makes decisions (hit, stand, double down, split if applicable)
6. Dealer plays according to standard casino rules
7. Main bet is resolved and bankroll is updated
8. Game state is persisted to the database
9. Leaderboard rankings are recalculated if applicable

## Key Features

### Advanced Side-Bet Engine

The platform includes a complete implementation of two popular casino side bets:

- **Perfect Pairs**: Evaluates the player's initial two cards for matching pairs, with different payout tiers for mixed pairs, colored pairs, and perfect pairs
- **21+3**: Combines the player's two cards with the dealer's up card to form poker hands, including flushes, straights, three-of-a-kind, straight flushes, and suited three-of-a-kind

All payouts are calculated in real-time with transparent odds display.

### Multi-Zone Interface

The user interface is optimized for clarity and engagement. The three-zone layout separates the dealer area, player area, and controls/statistics, reducing cognitive load while maintaining visual interest. This design approach aims to keep players focused and engaged throughout extended gameplay sessions.

### Persistent User Profiles

The authentication system provides secure account creation and login functionality. Each user has a persistent profile that tracks:

- Current bankroll balance
- Career high bankroll
- Total hands played
- Win/loss statistics
- Leaderboard ranking

### State Management

Flask session handling ensures that game state is preserved even if the browser is refreshed or temporarily disconnected. Players can resume their session without losing their current bankroll or game progress.

### Global Leaderboard

A competitive leaderboard tracks the highest career bankrolls across all users, adding a social element to the single-player experience. Rankings update dynamically as players achieve new personal bests.

## Project Structure

```
BlackHub/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/             # Stylesheets
│   ├── js/              # Client-side JavaScript
│   └── images/          # Card graphics and UI assets
├── templates/           # HTML templates
└── database/            # SQLite database files
```

## Disclaimer

This project was developed for academic and entertainment purposes only. It serves as a demonstration of full-stack web development principles and game logic implementation. The application is a simulation and does not involve real-world currency, actual gambling, or any form of monetary transaction.

---

**Note**: This is a learning project intended to showcase web development skills and game programming concepts. Please gamble responsibly if you choose to participate in real-world casino activities.
