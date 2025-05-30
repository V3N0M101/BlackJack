// --- Global Variables and DOM Elements ---
let currentGameState = null; // Stores the current game state from the backend
let activeBetInput = null; // To track which bet input is currently focused for chip clicks

// Get references to all necessary DOM elements
const dealerCardsDiv = document.getElementById('dealer-cards');
const dealerTotalSpan = document.getElementById('dealer-total');
const playerChipsSpan = document.getElementById('player-chips');
const totalBetDisplaySpan = document.getElementById('total-bet-display');
const gameMessageDiv = document.getElementById('game-message');

const playerHandElements = []; // Array to store references to each player hand's elements
for (let i = 0; i < 3; i++) {
    playerHandElements.push({
        area: document.getElementById(`hand-${i}`),
        cardsDiv: document.getElementById(`cards-hand-${i}`),
        totalSpan: document.getElementById(`total-hand-${i}`),
        messageSpan: document.getElementById(`message-hand-${i}`),
        mainBetInput: document.getElementById(`main-bet-input-${i}`),
        side213BetInput: document.getElementById(`213-bet-input-${i}`),
        sidePPBetInput: document.getElementById(`pp-bet-input-${i}`),
        mainBetDisplay: document.getElementById(`main-bet-${i}`), // Span to display current main bet
        betAreaBtn: document.querySelector(`.bet-area[data-hand-index="${i}"]`) // The MAIN button/area
    });
}

// Action Buttons
const dealBtn = document.getElementById('dealBtn');
const hitBtn = document.getElementById('hitBtn');
const standBtn = document.getElementById('standBtn');
const doubleBtn = document.getElementById('doubleBtn');
const splitBtn = document.getElementById('splitBtn'); // Still disabled, but good to have a ref
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
            // Optionally add/remove a class for visual disabled state
            if (disable) {
                button.classList.add('disabled');
            } else {
                button.classList.remove('disabled');
            }
        }
    });
}

/**
 * Sets the visibility of bet input fields and bet display spans.
 * @param {boolean} showInputs - True to show inputs, false to show display spans.
 */
function toggleBetInputVisibility(showInputs) {
    playerHandElements.forEach(hand => {
        if (hand.mainBetInput) hand.mainBetInput.style.display = showInputs ? 'inline-block' : 'none';
        if (hand.side213BetInput) hand.side213BetInput.style.display = showInputs ? 'inline-block' : 'none';
        if (hand.sidePPBetInput) hand.sidePPBetInput.style.display = showInputs ? 'inline-block' : 'none';
        
        // Hide/show the display spans which show the committed bet
        if (hand.mainBetDisplay) hand.mainBetDisplay.style.display = showInputs ? 'none' : 'inline-block';
        if (hand.betAreaBtn) hand.betAreaBtn.style.display = showInputs ? 'none' : 'inline-block'; // The MAIN button that acts as bet display
        if (hand.betAreaBtn.previousElementSibling) hand.betAreaBtn.previousElementSibling.style.display = showInputs ? 'none' : 'inline-block'; // PP button
        if (hand.betAreaBtn.nextElementSibling) hand.betAreaBtn.nextElementSibling.style.display = showInputs ? 'none' : 'inline-block'; // 21+3 button
    });
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

    // 3. Update Player Hands (Loop through each hand)
    let totalCurrentBet = 0;
    playerHandElements.forEach((handEl, index) => {
        const handData = gameState.player_hands[index];

        clearCards(handEl.cardsDiv);
        addCardImages(handEl.cardsDiv, handData.hand);
        handEl.totalSpan.textContent = `Total: ${handData.total}`;
        handEl.messageSpan.textContent = handData.result_message;

        // Update displayed bets
        handEl.mainBetDisplay.textContent = handData.main_bet;
        // You might want to display side bets too if there's space
        // e.g., handEl.side213BetDisplay.textContent = handData.side_bet_21_3;

        // Highlight active hand
        if (index === gameState.current_active_hand_index && gameState.game_phase === "player_turns") {
            handEl.area.classList.add('active-hand');
        } else {
            handEl.area.classList.remove('active-hand');
        }

        totalCurrentBet += handData.main_bet + handData.side_bet_21_3 + handData.side_bet_perfect_pair;
    });
    totalBetDisplaySpan.textContent = `Total Bet: $${totalCurrentBet}`;


    // 4. Manage Button States and Input Visibility based on game_phase
    const isBettingPhase = gameState.game_phase === "betting";
    const isPlayerTurn = gameState.game_phase === "player_turns";
    const isRoundOver = gameState.game_phase === "round_over";

    // Toggle bet input fields vs. displayed bet values
    toggleBetInputVisibility(isBettingPhase);

    // Main action buttons
    setButtonsDisabled([dealBtn], !isBettingPhase);
    setButtonsDisabled([hitBtn, standBtn, doubleBtn], !isPlayerTurn);
    setButtonsDisabled([splitBtn], true); // Split is not implemented yet
    setButtonsDisabled([clearBetsBtn, reBetBtn], !isBettingPhase && !isRoundOver); // Can clear/re-bet in betting or after round.
    setButtonsDisabled([collectBtn], !isRoundOver); // Only collect chips when the round is over

    // Disable action buttons for non-active hands
    if (isPlayerTurn) {
        playerHandElements.forEach((handEl, index) => {
            if (index !== gameState.current_active_hand_index) {
                // Dim or disable buttons for inactive hands, or just let the main disable handle it
                // For simplicity, we enable/disable the global action buttons, and rely on the backend
                // to reject actions on inactive hands.
            }
        });
        // Specific checks for the active hand's buttons
        const activeHandData = gameState.player_hands[gameState.current_active_hand_index];
        if (activeHandData) { // Ensure there is an active hand
            setButtonsDisabled([doubleBtn], !activeHandData.can_double);
        } else {
            setButtonsDisabled([hitBtn, standBtn, doubleBtn], true); // If no active hand (e.g. all hands finished)
        }
    }
}

// --- API Calls ---

/**
 * Generic function to make API calls and update the UI.
 * @param {string} url - The API endpoint URL.
 * @param {Object} options - Fetch options (method, headers, body, etc.).
 */
async function fetchGameState(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...options // Spread existing options
        });
        const data = await response.json();

        if (data.success) {
            updateUI(data.game_state);
        } else {
            // Display error message from backend
            gameMessageDiv.textContent = `Error: ${data.message}`;
            // Optionally update UI with partial game_state if provided even on error
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

    // Set initial active bet input to the first main bet input
    if (playerHandElements.length > 0 && playerHandElements[0].mainBetInput) {
        activeBetInput = playerHandElements[0].mainBetInput;
        activeBetInput.focus();
    }
});

// Event listeners for betting inputs (to track activeBetInput)
playerHandElements.forEach(handEl => {
    handEl.mainBetInput.addEventListener('focus', () => activeBetInput = handEl.mainBetInput);
    handEl.side213BetInput.addEventListener('focus', () => activeBetInput = handEl.side213BetInput);
    handEl.sidePPBetInput.addEventListener('focus', () => activeBetInput = handEl.sidePPBetInput);
});

// Chip buttons click handler
chipButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (activeBetInput && !activeBetInput.disabled) { // Ensure an input is focused and not disabled
            const chipValue = parseInt(button.dataset.chipValue);
            let currentValue = parseInt(activeBetInput.value) || 0;
            activeBetInput.value = currentValue + chipValue;
        } else {
            gameMessageDiv.textContent = "Please select a bet input first.";
        }
    });
});

// Deal button handler
dealBtn.addEventListener('click', () => {
    const bets = [];
    let hasValidBet = false;
    playerHandElements.forEach(handEl => {
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
    });

    if (!hasValidBet) {
        gameMessageDiv.textContent = "You must place a main bet on at least one hand.";
        return;
    }

    fetchGameState('/api/place_bets', {
        method: 'POST',
        body: JSON.stringify({ bets: bets })
    });
});

// Player Action Buttons (Hit, Stand, Double)
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


// Clear Bets button handler
clearBetsBtn.addEventListener('click', () => {
    playerHandElements.forEach(handEl => {
        handEl.mainBetInput.value = 0;
        handEl.side213BetInput.value = 0;
        handEl.sidePPBetInput.value = 0;
    });
    // Update displayed bets to reflect 0
    updateUI(currentGameState); // Re-render with current game state but inputs reset
    gameMessageDiv.textContent = "Bets cleared.";
});

// Re-Bet button handler (simplified: just resets the round for a new betting phase)
reBetBtn.addEventListener('click', () => {
    fetchGameState('/api/reset_round', { method: 'POST' });
    // You might want to store previous bets and re-apply them here if "re-bet" means actual re-betting
    // For now, it just resets the round, user inputs bets again.
    // Future enhancement: save last round's bets to re-populate inputs.
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