// --- Global Variables and DOM Elements ---
let currentGameState = null; // Stores the current game state from the backend
let activeBetInput = null; // To track which bet input is currently focused for chip clicks
let activeBetButton = null; // To track the currently selected circular bet button

// Get references to all necessary DOM elements
const dealerCardsDiv = document.getElementById('dealer-cards');
const dealerTotalSpan = document.getElementById('dealer-total');
const playerChipsSpan = document.getElementById('player-chips');
const totalBetDisplaySpan = document.getElementById('total-bet-display');
const gameMessageDiv = document.getElementById('game-message');

const playerHandsContainer = document.querySelector('.player'); // The div containing all Player-Area elements

// Action Buttons (keep these global as they are fixed)
const dealBtn = document.getElementById('dealBtn');
const hitBtn = document.getElementById('hitBtn');
const standBtn = document.getElementById('standBtn');
const doubleBtn = document.getElementById('doubleBtn');
const splitBtn = document.getElementById('splitBtn');
const clearBetsBtn = document.getElementById('clearBetsBtn');
const reBetBtn = document.getElementById('reBetBtn');
const collectBtn = document.getElementById('collectBtn');

// Chip Buttons
const chipButtons = document.querySelectorAll('.chips button');

// --- Helper Functions ---

/**
 * Clears all card images from a given container.
 * @param {HTMLElement} container - The div element containing card images.
 */
function clearCards(container) {
    container.innerHTML = '';
}

/**
 * Adds card images to a given container based on card data.
 * @param {HTMLElement} container - The div element to add cards to.
 * @param {Array<Object>} cardsArray - An array of card objects (from game_state.hand).
 */
function addCardImages(container, cardsArray) {
    cardsArray.forEach(card => {
        const img = document.createElement('img');
        img.src = `/static/Images/cards/${card.filename}`;
        img.alt = `${card.rank}${card.suit}`;
        img.classList.add('card');
        container.appendChild(img);
    });
}

/**
 * Disables/enables a list of buttons.
 * @param {Array<HTMLElement>} buttons - An array of button elements.
 * @param {boolean} disable - True to disable, false to enable.
 */
function setButtonsDisabled(buttons, disable) {
    buttons.forEach(button => {
        if (button) { // Check if button actually exists
            button.disabled = disable;
            if (disable) {
                button.classList.add('disabled');
            } else {
                button.classList.remove('disabled');
            }
        }
    });
}

/**
 * Manages the 'selected' class for bet area buttons.
 * Only one bet area button should be selected at a time.
 * @param {HTMLElement} newSelectedButton - The button that was just clicked/selected.
 */
function setSelectedBetButton(newSelectedButton) {
    if (activeBetButton) {
        activeBetButton.classList.remove('selected');
    }
    activeBetButton = newSelectedButton;
    if (activeBetButton) { // Ensure newSelectedButton is not null
        activeBetButton.classList.add('selected');
    }
}

/**
 * Gets or creates a player hand container and its sub-elements.
 * @param {number} index The index of the hand (0, 1, 2, 3...)
 * @returns {Object} An object containing references to the hand's DOM elements.
 */
function getOrCreatePlayerHandElement(index) {
    let handEl = document.getElementById(`hand-${index}`);
    let isNewHand = false;

    if (!handEl) {
        isNewHand = true;
        // Create the new hand container if it doesn't exist
        handEl = document.createElement('div');
        handEl.classList.add('Player-Area');
        handEl.id = `hand-${index}`;
        playerHandsContainer.appendChild(handEl); // Append to the main player container

        // Populate the new hand container with its inner structure
        handEl.innerHTML = `
            <div class="cards" id="cards-hand-${index}"></div>
            <div class="hand-info">
                <span class="hand-total" id="total-hand-${index}">Total:</span> <span class="hand-message" id="message-hand-${index}"></span>
            </div>
            <div class="Zone">
                <button class="PP bet-area-button" id="pp-bet-${index}" data-input-target="pp-bet-input-${index}">PP</button>
                <button class="MAIN bet-area bet-area-button" data-hand-index="${index}" data-input-target="main-bet-input-${index}"></button>
                <button class="TWENTYONE bet-area-button" id="213-bet-${index}" data-input-target="213-bet-input-${index}">21+3</button>
            </div>
            <div class="bet-input-container">
                <input type="number" class="main-bet-input" id="main-bet-input-${index}" placeholder="Main Bet" value="0" min="500" step="500">
                <input type="number" class="side-bet-input" id="213-bet-input-${index}" placeholder="21+3" value="0" min="0" step="100">
                <input type="number" class="side-bet-input" id="pp-bet-input-${index}" placeholder="PP" value="0" min="0" step="100">
            </div>
        `;
    }

    // Return an object with references to the elements for easier access
    const handElements = {
        area: handEl,
        cardsDiv: document.getElementById(`cards-hand-${index}`),
        totalSpan: document.getElementById(`total-hand-${index}`),
        messageSpan: document.getElementById(`message-hand-${index}`),
        mainBetInput: document.getElementById(`main-bet-input-${index}`),
        side213BetInput: document.getElementById(`213-bet-input-${index}`),
        sidePPBetInput: document.getElementById(`pp-bet-input-${index}`),
        mainBetDisplay: handEl.querySelector(`.MAIN.bet-area`), // This is the MAIN button
        ppBetButton: handEl.querySelector(`.PP.bet-area-button`),
        twentyOneBetButton: handEl.querySelector(`.TWENTYONE.bet-area-button`)
    };

    // Attach event listeners for bet inputs and circular buttons if new hand or not already attached
    if (isNewHand || !handEl.dataset.listenersAttached) { // Use a data attribute to prevent re-attaching
        if (handElements.mainBetInput) handElements.mainBetInput.addEventListener('focus', () => {
            activeBetInput = handElements.mainBetInput;
            setSelectedBetButton(handElements.mainBetDisplay); // MAIN button is the display
        });
        if (handElements.side213BetInput) handElements.side213BetInput.addEventListener('focus', () => {
            activeBetInput = handElements.side213BetInput;
            setSelectedBetButton(handElements.twentyOneBetButton);
        });
        if (handElements.sidePPBetInput) handElements.sidePPBetInput.addEventListener('focus', () => {
            activeBetInput = handElements.sidePPBetInput;
            setSelectedBetButton(handElements.ppBetButton);
        });

        // --- NEW: Attach click listeners to the circular bet zone buttons (PP, MAIN, 21+3) ---
        // This is where the core fix is
        handElements.ppBetButton.addEventListener('click', function() {
            activeBetInput = handElements.sidePPBetInput;
            setSelectedBetButton(this); // 'this' refers to the clicked button
            activeBetInput.focus(); // Optional: visually focus the input field
        });
        handElements.mainBetDisplay.addEventListener('click', function() { // mainBetDisplay is the MAIN button
            activeBetInput = handElements.mainBetInput;
            setSelectedBetButton(this);
            activeBetInput.focus();
        });
        handElements.twentyOneBetButton.addEventListener('click', function() {
            activeBetInput = handElements.side213BetInput;
            setSelectedBetButton(this);
            activeBetInput.focus();
        });

        handEl.dataset.listenersAttached = 'true'; // Mark listeners as attached
    }

    return handElements;
}

/**
 * Sets the visibility of bet input fields, bet display spans, and bet zone buttons for a specific hand.
 * @param {Object} handEl - The object containing references to the hand's DOM elements.
 * @param {boolean} isBettingPhase - True if it's the betting phase, false otherwise.
 */
function toggleBetElementsVisibilityForHand(handEl, isBettingPhase) {
    // Buttons (PP, MAIN, 21+3) are always visible, but their clickability changes
    if (handEl.mainBetDisplay) handEl.mainBetDisplay.style.display = 'inline-block'; // MAIN
    if (handEl.ppBetButton) handEl.ppBetButton.style.display = 'flex'; // PP (use flex as per your CSS)
    if (handEl.twentyOneBetButton) handEl.twentyOneBetButton.style.display = 'flex'; // 21+3 (use flex as per your CSS)

    // Control their clickability based on the phase
    const betButtons = [handEl.mainBetDisplay, handEl.ppBetButton, handEl.twentyOneBetButton];
    setButtonsDisabled(betButtons, !isBettingPhase);


    if (isBettingPhase) {
        // During betting phase: Show input fields, clear display text on main bet button
        if (handEl.mainBetInput) handEl.mainBetInput.style.display = 'inline-block';
        if (handEl.side213BetInput) handEl.side213BetInput.style.display = 'inline-block';
        if (handEl.sidePPBetInput) handEl.sidePPBetInput.style.display = 'inline-block';

        // Clear the displayed bet values on the buttons if in betting phase
        if (handEl.mainBetDisplay) handEl.mainBetDisplay.textContent = '';
        if (handEl.ppBetButton) handEl.ppBetButton.textContent = 'PP';
        if (handEl.twentyOneBetButton) handEl.twentyOneBetButton.textContent = '21+3';


    } else {
        // After betting phase (game in progress): Hide input fields, show bet values on buttons
        if (handEl.mainBetInput) handEl.mainBetInput.style.display = 'none';
        if (handEl.side213BetInput) handEl.side213BetInput.style.display = 'none';
        if (handEl.sidePPBetInput) handEl.sidePPBetInput.style.display = 'none';

        // Update the displayed bet values on the buttons
        // These will be updated by updateUI later with actual bet amounts
    }
}

/**
 * Updates the UI based on the current game state.
 * @param {Object} gameState - The game state object received from the backend.
 */
function updateUI(gameState) {
    currentGameState = gameState; // Store the latest state

    // 1. Update Dealer's Hand
    clearCards(dealerCardsDiv);
    addCardImages(dealerCardsDiv, gameState.dealer_hand);
    dealerTotalSpan.textContent = `Dealer: ${gameState.dealer_total}`;

    // 2. Update Player's Chips and Global Message
    playerChipsSpan.textContent = `Balance: $${gameState.player_chips}`;
    gameMessageDiv.textContent = gameState.game_message;

    // --- Dynamic Player Hand Management ---
    // Remove extra hands if any (e.g., if a previous game had more hands than current)
    const currentNumHandsInDOM = playerHandsContainer.children.length;
    for (let i = gameState.player_hands.length; i < currentNumHandsInDOM; i++) {
        const extraHandEl = document.getElementById(`hand-${i}`);
        if (extraHandEl) {
            playerHandsContainer.removeChild(extraHandEl);
        }
    }

    // 3. Update Player Hands (Loop through each hand from the game state)
    let totalCurrentBet = 0;
    for (let i = 0; i < gameState.player_hands.length; i++) {
        const handData = gameState.player_hands[i];
        const handEl = getOrCreatePlayerHandElement(i); // Get or create the DOM elements for this hand

        clearCards(handEl.cardsDiv);
        addCardImages(handEl.cardsDiv, handData.hand);

        // *** THIS IS THE CRUCIAL CHANGE ***
        // Only display the total if it's not 0 or if it's not the betting phase
        if (handData.total === 0 && gameState.game_phase === "betting") {
            handEl.totalSpan.textContent = 'Total:'; // Keep "Total:" but no number
        } else {
            handEl.totalSpan.textContent = `Total: ${handData.total}`;
        }
        // **********************************

        handEl.messageSpan.textContent = handData.result_message;

        // Update displayed bets (the text content of the MAIN, PP, and 21+3 buttons)
        if (handEl.mainBetDisplay) handEl.mainBetDisplay.textContent = `$${handData.main_bet}`;
        if (handEl.ppBetButton) handEl.ppBetButton.textContent = handData.side_bet_perfect_pair > 0 ? `$${handData.side_bet_perfect_pair}` : 'PP';
        if (handEl.twentyOneBetButton) handEl.twentyOneBetButton.textContent = handData.side_bet_21_3 > 0 ? `$${handData.side_bet_21_3}` : '21+3';


        // Highlight active hand
        if (i === gameState.current_active_hand_index && gameState.game_phase === "player_turns") {
            handEl.area.classList.add('active-hand');
        } else {
            handEl.area.classList.remove('active-hand');
        }

        // Toggle visibility of bet inputs vs. bet displays/zones
        const isBettingPhase = gameState.game_phase === "betting";
        toggleBetElementsVisibilityForHand(handEl, isBettingPhase);

        // Update bet inputs' values if in betting phase
        if (isBettingPhase) {
            handEl.mainBetInput.value = handData.main_bet || 500;
            handEl.side213BetInput.value = handData.side_bet_21_3 || 0;
            handEl.sidePPBetInput.value = handData.side_bet_perfect_pair || 0;
        }

        totalCurrentBet += handData.main_bet + handData.side_bet_21_3 + handData.side_bet_perfect_pair;
    }
    totalBetDisplaySpan.textContent = `Total Bet: $${totalCurrentBet}`;


    // 4. Manage Global Button States based on game_phase
    const isBettingPhase = gameState.game_phase === "betting";
    const isPlayerTurn = gameState.game_phase === "player_turns";
    const isRoundOver = gameState.game_phase === "round_over";

    setButtonsDisabled([dealBtn], !isBettingPhase);
    setButtonsDisabled([hitBtn, standBtn, doubleBtn], !isPlayerTurn);

    let activeHandData = null;
    if (gameState.current_active_hand_index !== -1 && gameState.player_hands[gameState.current_active_hand_index]) {
        activeHandData = gameState.player_hands[gameState.current_active_hand_index];
    }
    setButtonsDisabled([splitBtn], !(isPlayerTurn && activeHandData && activeHandData.can_split));

    setButtonsDisabled([clearBetsBtn, reBetBtn], !(isBettingPhase || isRoundOver));
    setButtonsDisabled([collectBtn], !isBettingPhase);

    if (!isPlayerTurn) {
        setButtonsDisabled([hitBtn, standBtn, doubleBtn, splitBtn], true);
    } else {
        if (activeHandData) {
            setButtonsDisabled([doubleBtn], !activeHandData.can_double);
        } else {
            setButtonsDisabled([hitBtn, standBtn, doubleBtn, splitBtn], true);
        }
    }

    // Reset active button state if not in betting phase
    if (!isBettingPhase) {
        if (activeBetButton) {
            activeBetButton.classList.remove('selected');
        }
        activeBetButton = null;
        activeBetInput = null;
    } else {
        // If transitioning to betting phase, ensure a button is selected by default
        // (e.g., the main bet of the first hand)
        if (!activeBetButton && currentGameState.player_hands.length > 0) {
            const firstHandEl = getOrCreatePlayerHandElement(0);
            if (firstHandEl.mainBetDisplay) {
                setSelectedBetButton(firstHandEl.mainBetDisplay);
                activeBetInput = firstHandEl.mainBetInput;
            }
        }
    }
}

// --- API Calls (remains the same) ---
async function fetchGameState(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        const data = await response.json();

        if (data.success) {
            updateUI(data.game_state);
        } else {
            gameMessageDiv.textContent = `Error: ${data.message}`;
            if (data.game_state) {
                updateUI(data.game_state);
            }
            console.error("API Error:", data.message);
        }
    } catch (error) {
        gameMessageDiv.textContent = `Network error: ${error.message}`;
        console.error("Fetch Error:", error);
    }
}

// --- Event Listeners ---

// Initial game start when page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState('/api/start_game', { method: 'POST' });

    // Set initial active bet input to the first main bet input and button
    const initialHandEl = getOrCreatePlayerHandElement(0);
    if (initialHandEl && initialHandEl.mainBetInput && initialHandEl.mainBetDisplay) {
        activeBetInput = initialHandEl.mainBetInput;
        setSelectedBetButton(initialHandEl.mainBetDisplay);
        activeBetInput.focus();
    }
});


// Chip buttons click handler
chipButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (currentGameState.game_phase !== 'betting') {
            gameMessageDiv.textContent = "You can only place bets during the betting phase.";
            return;
        }

        if (activeBetInput && !activeBetInput.disabled) {
            const chipValue = parseInt(button.dataset.chipValue);
            let currentValue = parseInt(activeBetInput.value) || 0;
            let newValue = currentValue + chipValue;

            // Simple check to prevent negative balance locally
            // A more robust check might need to aggregate all bets
            if (currentGameState.player_chips < newValue) { // This is a simplified check
                gameMessageDiv.textContent = "Not enough chips!";
                return;
            }

            activeBetInput.value = newValue;

            // Update the displayed bet on the main button if it's the main bet input
            // Or update the specific side bet button's text
            const handIndex = parseInt(activeBetInput.closest('.Player-Area').id.replace('hand-', ''));
            const handEl = getOrCreatePlayerHandElement(handIndex);

            if (activeBetInput === handEl.mainBetInput) {
                handEl.mainBetDisplay.textContent = `$${newValue}`;
            } else if (activeBetInput === handEl.sidePPBetInput) {
                handEl.ppBetButton.textContent = `$${newValue}`;
            } else if (activeBetInput === handEl.side213BetInput) {
                handEl.twentyOneBetButton.textContent = `$${newValue}`;
            }

            // Update total bet display immediately
            updateTotalBetDisplay();

        } else {
            gameMessageDiv.textContent = "Please select a bet area (PP, Main, or 21+3) first.";
        }
    });
});

/**
 * Calculates and updates the total bet displayed at the bottom.
 */
function updateTotalBetDisplay() {
    let currentTotalBet = 0;
    // Iterate through all currently active hands in the DOM
    const handElements = playerHandsContainer.querySelectorAll('.Player-Area');
    handElements.forEach((handElDiv, index) => {
        const handEl = getOrCreatePlayerHandElement(index); // Re-get elements for safety
        currentTotalBet += (parseInt(handEl.mainBetInput.value) || 0);
        currentTotalBet += (parseInt(handEl.side213BetInput.value) || 0);
        currentTotalBet += (parseInt(handEl.sidePPBetInput.value) || 0);
    });
    totalBetDisplaySpan.textContent = `Total Bet: $${currentTotalBet}`;
}


// Deal button handler
dealBtn.addEventListener('click', () => {
    const bets = [];
    let hasValidBet = false;

    const numHandsToCollectBetsFrom = currentGameState && currentGameState.player_hands ? currentGameState.player_hands.length : 3;

    for (let i = 0; i < numHandsToCollectBetsFrom; i++) {
        const handEl = getOrCreatePlayerHandElement(i);
        const mainBet = parseInt(handEl.mainBetInput.value) || 0;
        const side213 = parseInt(handEl.side213BetInput.value) || 0;
        const sidePP = parseInt(handEl.sidePPBetInput.value) || 0;

        bets.push({
            main_bet: mainBet,
            side_21_3: side213,
            side_pp: sidePP
        });

        if (mainBet > 0) {
            hasValidBet = true;
        }
    }

    if (!hasValidBet) {
        gameMessageDiv.textContent = "You must place a main bet on at least one hand.";
        return;
    }

    // Clear active bet button highlight when dealing
    setSelectedBetButton(null);
    activeBetInput = null;

    fetchGameState('/api/place_bets', {
        method: 'POST',
        body: JSON.stringify({ bets: bets })
    });
});


// Player Action Buttons (Hit, Stand, Double, Split)
hitBtn.addEventListener('click', () => {
    if (currentGameState && currentGameState.current_active_hand_index !== -1) {
        fetchGameState('/api/player_action', {
            method: 'POST',
            body: JSON.stringify({ action: 'hit', hand_index: currentGameState.current_active_hand_index })
        });
    } else {
        gameMessageDiv.textContent = "No active hand to hit.";
    }
});

standBtn.addEventListener('click', () => {
    if (currentGameState && currentGameState.current_active_hand_index !== -1) {
        fetchGameState('/api/player_action', {
            method: 'POST',
            body: JSON.stringify({ action: 'stand', hand_index: currentGameState.current_active_hand_index })
        });
    } else {
        gameMessageDiv.textContent = "No active hand to stand.";
    }
});

doubleBtn.addEventListener('click', () => {
    if (currentGameState && currentGameState.current_active_hand_index !== -1) {
        fetchGameState('/api/player_action', {
            method: 'POST',
            body: JSON.stringify({ action: 'double', hand_index: currentGameState.current_active_hand_index })
        });
    } else {
        gameMessageDiv.textContent = "No active hand to double down.";
    }
});

splitBtn.addEventListener('click', () => {
    if (currentGameState && currentGameState.current_active_hand_index !== -1) {
        fetchGameState('/api/player_action', {
            method: 'POST',
            body: JSON.stringify({ action: 'split', hand_index: currentGameState.current_active_hand_index })
        });
    } else {
        gameMessageDiv.textContent = "No active hand to split.";
    }
});


// Clear Bets button handler
clearBetsBtn.addEventListener('click', () => {
    // Iterate based on the number of hands currently shown, not just 3
    const numHandsInDOM = playerHandsContainer.children.length;
    for (let i = 0; i < numHandsInDOM; i++) {
        const handEl = getOrCreatePlayerHandElement(i); // Ensure elements exist
        if (handEl.mainBetInput) handEl.mainBetInput.value = 0;
        if (handEl.side213BetInput) handEl.side213BetInput.value = 0;
        if (handEl.sidePPBetInput) handEl.sidePPBetInput.value = 0;

        // Also update the display on the MAIN, PP, 21+3 buttons
        if (handEl.mainBetDisplay) handEl.mainBetDisplay.textContent = ''; // Clear for user input
        if (handEl.ppBetButton) handEl.ppBetButton.textContent = 'PP';
        if (handEl.twentyOneBetButton) handEl.twentyOneBetButton.textContent = '21+3';
    }
    gameMessageDiv.textContent = "Bets cleared.";
    updateTotalBetDisplay(); // Update total bet display
});

// --- Re-Bet button handler (THE FIX IS HERE) ---
reBetBtn.addEventListener('click', () => {
    handleRebet(); // Call the async function directly
});


// Collect Chips button handler
collectBtn.addEventListener('click', () => {
    fetchGameState('/api/collect_chips', { method: 'POST' });
});

// Fullscreen functionality (from your original game.js)
function openFullscreen() {
    const elem = document.documentElement; // or document.body;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msFullscreenElement();
    }
}

// Function to handle the "Rebet" button click
async function handleRebet() {
    try {
        const response = await fetch('/api/rebet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();

        if (data.success) {
            updateUI(data.game_state);
            // After rebet, re-select the first main bet by default if in betting phase
            if (data.game_state.game_phase === 'betting' && data.game_state.player_hands.length > 0) {
                const firstHandEl = getOrCreatePlayerHandElement(0);
                if (firstHandEl.mainBetInput && firstHandEl.mainBetDisplay) {
                    activeBetInput = firstHandEl.mainBetInput;
                    setSelectedBetButton(firstHandEl.mainBetDisplay);
                    activeBetInput.focus();
                }
            }
            gameMessageDiv.textContent = data.message; // Display any message from the backend
            updateTotalBetDisplay(); // Ensure total bet is updated after rebet
        } else {
            gameMessageDiv.textContent = "Error rebetting: " + data.message;
            console.error("Error rebetting:", data.message);
        }
    } catch (error) {
        gameMessageDiv.textContent = "An error occurred during rebet.";
        console.error("Error during rebet fetch:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const volumeButton = document.getElementById('volumeButton');
    const volumeIcon = document.getElementById('volumeIcon');
    let isMuted = false; // Initial state: not muted

    if (volumeButton && volumeIcon) {
        volumeButton.addEventListener('click', () => {
            if (isMuted) {
                // If currently muted, change to volume icon
                volumeIcon.src = '/static/Images/icons/vol.png';
                volumeIcon.alt = 'Volume';
                // You would also unmute your actual game audio here
            } else {
                // If currently unmuted, change to mute icon
                volumeIcon.src = '/static/Images/icons/mute.png';
                volumeIcon.alt = 'Mute';
                // You would also mute your actual game audio here
            }
            isMuted = !isMuted; // Toggle the state
        });
    } else {
        console.error('Volume button or icon not found. Check IDs.');
    }
});