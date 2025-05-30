// --- Global Variables and DOM Elements ---
let currentGameState = null; // Stores the current game state from the backend
let activeBetInput = null; // To track which bet input is currently focused for chip clicks

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
const reBetBtn = document.getElementById('reBetBtn'); // This is the button we're fixing
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
 * Gets or creates a player hand container and its sub-elements.
 * @param {number} index The index of the hand (0, 1, 2, 3...)
 * @returns {Object} An object containing references to the hand's DOM elements.
 */
function getOrCreatePlayerHandElement(index) {
    let handEl = document.getElementById(`hand-${index}`);
    if (!handEl) {
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
                <button class="PP" id="pp-bet-${index}">PP</button>
                <button class="MAIN bet-area" data-hand-index="${index}"></button>
                <button class="TWENTYONE" id="213-bet-${index}">21+3</button>
            </div>
            <div class="bet-input-container">
                <input type="number" class="main-bet-input" id="main-bet-input-${index}" placeholder="Main Bet" value="500" min="500" step="500">
                <input type="number" class="side-bet-input" id="213-bet-input-${index}" placeholder="21+3" value="0" min="0" step="100">
                <input type="number" class="side-bet-input" id="pp-bet-input-${index}" placeholder="PP" value="0" min="0" step="100">
            </div>
        `;

        // Attach event listeners for bet inputs immediately
        const mainBetInput = document.getElementById(`main-bet-input-${index}`);
        const side213BetInput = document.getElementById(`213-bet-input-${index}`);
        const sidePPBetInput = document.getElementById(`pp-bet-input-${index}`);

        if (mainBetInput) mainBetInput.addEventListener('focus', () => activeBetInput = mainBetInput);
        if (side213BetInput) side213BetInput.addEventListener('focus', () => activeBetInput = side213BetInput);
        if (sidePPBetInput) sidePPBetInput.addEventListener('focus', () => activeBetInput = sidePPBetInput);

        // Attach click listeners to the bet zone buttons (PP, MAIN, 21+3)
        const mainZoneButton = document.querySelector(`#hand-${index} .MAIN`);
        const ppZoneButton = document.querySelector(`#hand-${index} .PP`);
        const twentyOneZoneButton = document.querySelector(`#hand-${index} .TWENTYONE`);

        if (mainZoneButton) mainZoneButton.addEventListener('click', () => {
            activeBetInput = mainBetInput;
            mainBetInput.focus();
        });
        if (ppZoneButton) ppZoneButton.addEventListener('click', () => {
            activeBetInput = sidePPBetInput;
            sidePPBetInput.focus();
        });
        if (twentyOneZoneButton) twentyOneZoneButton.addEventListener('click', () => {
            activeBetInput = side213BetInput;
            side213BetInput.focus();
        });

    }

    // Return an object with references to the elements for easier access
    return {
        area: handEl,
        cardsDiv: document.getElementById(`cards-hand-${index}`),
        totalSpan: document.getElementById(`total-hand-${index}`),
        messageSpan: document.getElementById(`message-hand-${index}`),
        mainBetInput: document.getElementById(`main-bet-input-${index}`),
        side213BetInput: document.getElementById(`213-bet-input-${index}`),
        sidePPBetInput: document.getElementById(`pp-bet-input-${index}`),
        // Ensure this ID matches what's in your HTML for displaying the bet value
        mainBetDisplay: document.querySelector(`#hand-${index} .MAIN.bet-area`), // It's your MAIN button that displays the bet
        betAreaBtn: document.querySelector(`#hand-${index} .bet-area[data-hand-index="${index}"]`) // This is the MAIN bet button
    };
}


/**
 * Sets the visibility of bet input fields, bet display spans, and bet zone buttons for a specific hand.
 * @param {Object} handEl - The object containing references to the hand's DOM elements.
 * @param {boolean} isBettingPhase - True if it's the betting phase, false otherwise.
 */
function toggleBetElementsVisibilityForHand(handEl, isBettingPhase) {
    const mainZoneButton = handEl.betAreaBtn; // This is the .MAIN button
    const ppZoneButton = mainZoneButton ? mainZoneButton.previousElementSibling : null; // This is the .PP button
    const twentyOneZoneButton = mainZoneButton ? mainZoneButton.nextElementSibling : null; // This is the .TWENTYONE button

    // Always ensure the bet zone buttons are visible
    if (mainZoneButton) mainZoneButton.style.display = 'inline-block'; // MAIN
    if (ppZoneButton) ppZoneButton.style.display = 'flex'; // PP (use flex as per your CSS)
    if (twentyOneZoneButton) twentyOneZoneButton.style.display = 'flex'; // 21+3 (use flex as per your CSS)

    // Control their clickability based on the phase
    if (mainZoneButton) mainZoneButton.disabled = !isBettingPhase;
    if (ppZoneButton) ppZoneButton.disabled = !isBettingPhase;
    if (twentyOneZoneButton) twentyOneZoneButton.disabled = !isBettingPhase;


    if (isBettingPhase) {
        // During betting phase:
        // Show input fields for users to type/click chips into
        if (handEl.mainBetInput) handEl.mainBetInput.style.display = 'inline-block';
        if (handEl.side213BetInput) handEl.side213BetInput.style.display = 'inline-block';
        if (handEl.sidePPBetInput) handEl.sidePPBetInput.style.display = 'inline-block';

        // Hide the main bet display span (this shows the bet *value* during play)
        // If your MAIN button is *also* the display, you'll need to handle this carefully.
        // I'm assuming it's an element that changes its text content.
        if (handEl.mainBetDisplay) {
            // Keep the button visible, but ensure it shows the current bet or nothing
            // This is crucial: the MAIN button is where the bet is displayed later
            handEl.mainBetDisplay.textContent = handEl.mainBetInput.value; // Show current input value
        }

    } else {
        // After betting phase (game in progress):
        // Hide input fields
        if (handEl.mainBetInput) handEl.mainBetInput.style.display = 'none';
        if (handEl.side213BetInput) handEl.side213BetInput.style.display = 'none';
        if (handEl.sidePPBetInput) handEl.sidePPBetInput.style.display = 'none';

        // Show the main bet display span (which is the MAIN button)
        if (handEl.mainBetDisplay) handEl.mainBetDisplay.style.display = 'inline-block';
    }
}


/**
 * Updates the UI based on the current game state.
 * @param {Object} gameState - The game state object received from the backend.
 */
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

        // Update displayed bets (the text content of the MAIN button)
        if (handEl.mainBetDisplay) {
            handEl.mainBetDisplay.textContent = `$${handData.main_bet}`;
            // You might want to update the PP and 21+3 buttons' text content too
        }

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
    setButtonsDisabled([collectBtn], !isRoundOver);

    if (!isPlayerTurn) {
        setButtonsDisabled([hitBtn, standBtn, doubleBtn, splitBtn], true);
    } else {
        if (activeHandData) {
            setButtonsDisabled([doubleBtn], !activeHandData.can_double);
        } else {
            setButtonsDisabled([hitBtn, standBtn, doubleBtn, splitBtn], true);
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
            // The handleRebet function might also return last_bets
            // We don't need to re-apply them here if updateUI handles it
            // via currentGameState, which it does.
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

    // Set initial active bet input to the first main bet input
    const initialHandEl = getOrCreatePlayerHandElement(0);
    if (initialHandEl && initialHandEl.mainBetInput) {
        activeBetInput = initialHandEl.mainBetInput;
        activeBetInput.focus();
    }
});


// Chip buttons click handler
chipButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (activeBetInput && !activeBetInput.disabled) {
            const chipValue = parseInt(button.dataset.chipValue);
            let currentValue = parseInt(activeBetInput.value) || 0;
            activeBetInput.value = currentValue + chipValue;
            // Also update the displayed bet on the main button if it's the main bet input
            if (activeBetInput.classList.contains('main-bet-input')) {
                const handIndex = activeBetInput.id.replace('main-bet-input-', '');
                const handEl = getOrCreatePlayerHandElement(parseInt(handIndex));
                if (handEl.mainBetDisplay) {
                    handEl.mainBetDisplay.textContent = `$${activeBetInput.value}`;
                }
            }
            // For side bets, you might need similar logic to update their respective display elements
        } else {
            gameMessageDiv.textContent = "Please select a bet input first.";
        }
    });
});

// Deal button handler
dealBtn.addEventListener('click', () => {
    const bets = [];
    let hasValidBet = false;

    // Use currentGameState.player_hands.length to determine how many hands to iterate over
    // If currentGameState is null (e.g., first load), default to 3
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
        
        // Also update the display on the MAIN button if it's visible
        if (handEl.mainBetDisplay) handEl.mainBetDisplay.textContent = '$0';
    }
    gameMessageDiv.textContent = "Bets cleared.";
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

// Function to handle the "Rebet" button click (This function is now called)
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
            // updateUI will handle rendering the game_state received from the backend,
            // which should already contain the 'last_bets' pre-filled into hand data.
            updateUI(data.game_state);

            // The 'last_bets' in the response is primarily for debugging or if you needed
            // to do something client-side with them specifically.
            // Since updateUI already uses game_state.player_hands[i].main_bet etc.
            // to populate the inputs when isBettingPhase is true, this section
            // is largely redundant for the core rebet functionality.
            // Keeping it commented out for clarity that updateUI does the job.
            /*
            if (data.last_bets && data.last_bets.length > 0) {
                data.last_bets.forEach((bet_info, index) => {
                    // Ensure you're getting the correct input elements for the hand
                    const handEl = getOrCreatePlayerHandElement(index);
                    if (handEl.mainBetInput) handEl.mainBetInput.value = bet_info.main_bet;
                    if (handEl.side213BetInput) handEl.side213BetInput.value = bet_info.side_21_3;
                    if (handEl.sidePPBetInput) handEl.sidePPBetInput.value = bet_info.side_pp;
                });
                console.log("Bets pre-filled with last round's values (via game_state update).");
            }
            */
            gameMessageDiv.textContent = data.message; // Display any message from the backend
        } else {
            gameMessageDiv.textContent = "Error rebetting: " + data.message;
            console.error("Error rebetting:", data.message);
        }
    } catch (error) {
        gameMessageDiv.textContent = "An error occurred during rebet.";
        console.error("Error during rebet fetch:", error);
    }
}


