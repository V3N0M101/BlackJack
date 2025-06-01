import random

# --- Card Class ---
class Card:
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    SUITS = ['♠', '♥', '♦', '♣']

    def __init__(self, rank_idx, suit):
        if not (0 <= rank_idx < len(self.RANKS)):
            raise ValueError(f"Invalid rank index: {rank_idx}")
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank_idx = rank_idx
        self.suit = suit

    @property
    def rank(self):
        return self.RANKS[self.rank_idx]

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "rank_idx": self.rank_idx,
            "suit": self.suit,
            "filename": self.get_filename()
        }

    @staticmethod
    def from_dict(data):
        return Card(data['rank_idx'], data['suit'])

    def get_filename(self):
        rank_str = self.rank 
        if rank_str == 'A': rank_str = 'A'
        elif rank_str == 'J': rank_str = 'J'
        elif rank_str == 'Q': rank_str = 'Q'
        elif rank_str == 'K': rank_str = 'K'
        elif rank_str == '10': rank_str = '10'
        else: rank_str = str(self.rank_idx + 1)

        suit_map = {'♠': 'S', '♥': 'D', '♦': 'H', '♣': 'C'} # Fixed suit mapping for standard card images
        suit_str = suit_map[self.suit]
        return f"{rank_str}-{suit_str}.png" # e.g., 'A-S.png', '10-H.png'


# --- Deck Class ---
class Deck:
    def __init__(self, num_decks=4, cards_data=None):
        self.num_decks = num_decks
        if cards_data is None:
            self.cards = []
            self.generate_deck()
        else:
            self.cards = [Card.from_dict(card_dict) for card_dict in cards_data]

    def generate_deck(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Card.SUITS:
                for rank_idx in range(len(Card.RANKS)):
                    self.cards.append(Card(rank_idx, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def dealCards(self, num_cards):
        dealt = []
        for _ in range(num_cards):
            if not self.cards:
                self.generate_deck() # Reshuffle if deck runs out
                self.shuffle()
            dealt.append(self.cards.pop())
        return dealt

    def to_dict(self):
        return {
            "num_decks": self.num_decks,
            "cards": [card.to_dict() for card in self.cards]
        }

    @staticmethod
    def from_dict(data):
        return Deck(data['num_decks'], data['cards'])


# --- Player Class (Used for the main player's chips and the dealer) ---
class Player:
    def __init__(self, name, is_bot=False, hand_data=None, chips=None):
        self.name = name
        self.is_bot = is_bot
        self.hand = [] # This will be the dealer's hand
        if hand_data is not None:
            self.hand = [Card.from_dict(card_dict) for card_dict in hand_data]
        self.chips = chips if chips is not None else 10000

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def clear_hand(self):
        self.hand = []

    def to_dict(self):
        return {
            "name": self.name,
            "is_bot": self.is_bot,
            "hand": [card.to_dict() for card in self.hand],
            "chips": self.chips
        }

    @staticmethod
    def from_dict(data):
        return Player(data['name'], data['is_bot'], data['hand'], data['chips'])


# --- Helper Functions ---
def card_value(card):
    if card.rank_idx >= 9: # 10, J, Q, K
        return 10
    elif card.rank_idx == 0: # Ace
        return 11
    return card.rank_idx + 1 # 2-9

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        val = card_value(card)
        total += val
        if card.rank_idx == 0: # Ace
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

def evaluate_side_bets(player_hand, dealer_upcard):
    result = {
        "21+3": {"hand": None, "payout": 0, "won": False},
        "Perfect Pair": {"type": None, "payout": 0, "won": False}
    }

    if len(player_hand) != 2:
        return result
    
    c1, c2 = player_hand
    if c1.rank_idx == c2.rank_idx:
        if c1.suit == c2.suit:
            result["Perfect Pair"] = {"type": "Perfect Pair", "payout": 25, "won": True}
        elif (c1.suit in ['♦', '♥'] and c2.suit in ['♦', '♥']) or \
             (c1.suit in ['♠', '♣'] and c2.suit in ['♠', '♣']):
            result["Perfect Pair"] = {"type": "Colored Pair", "payout": 12, "won": True}
        else:
            result["Perfect Pair"] = {"type": "Mixed Pair", "payout": 6, "won": True}

    combo = player_hand + [dealer_upcard]
    suits = [card.suit for card in combo]
    ranks_idx = sorted([card.rank_idx for card in combo])

    def is_flush_check():
        return suits[0] == suits[1] == suits[2]

    def is_straight_check():
        poker_ranks = []
        for r_idx in ranks_idx:
            if r_idx == 0: # Ace can be 1 or 14 for straight
                poker_ranks.append(1)
                poker_ranks.append(14) 
            else:
                poker_ranks.append(r_idx + 1)
        poker_ranks = sorted(list(set(poker_ranks)))

        for i in range(len(poker_ranks) - 2):
            if poker_ranks[i+1] == poker_ranks[i] + 1 and \
               poker_ranks[i+2] == poker_ranks[i+1] + 1:
                return True
        return False

    def is_three_of_a_kind_check():
        return ranks_idx[0] == ranks_idx[1] == ranks_idx[2]

    if is_three_of_a_kind_check() and is_flush_check():
        result["21+3"] = {"hand": "Suited Trips", "payout": 100, "won": True}
    elif is_straight_check() and is_flush_check():
        result["21+3"] = {"hand": "Straight Flush", "payout": 40, "won": True}
    elif is_three_of_a_kind_check():
        result["21+3"] = {"hand": "Three of a Kind", "payout": 30, "won": True}
    elif is_straight_check():
        result["21+3"] = {"hand": "Straight", "payout": 10, "won": True}
    elif is_flush_check():
        result["21+3"] = {"hand": "Flush", "payout": 5, "won": True}

    
    return result


# --- BlackjackMultiGame Class ---
class BlackjackMultiGame:
    def __init__(self, player_name="You", initial_chips=10000, num_hands=3, game_state_data=None):
        if game_state_data is None:
            # Initialize a new multi-hand game
            self.deck = Deck()
            self.deck.shuffle()
            self.player = Player(player_name, chips=initial_chips) # Main player for chips
            self.dealer = Player("Dealer", is_bot=True)

            self.num_hands = num_hands
            self.player_hands = [] # List of dictionaries, each representing a hand
            for i in range(self.num_hands):
                self.player_hands.append(self._create_new_hand_state())

            self.current_active_hand_index = -1 # -1 means betting phase, 0-2 for player turns
            self.game_phase = "betting" # 'betting', 'dealing', 'player_turns', 'dealer_turn', 'settlement', 'round_over'
            self.game_message = "Welcome! Place your bets for all hands."
        else:
            # Reconstruct game from serialized data
            self.deck = Deck.from_dict(game_state_data['deck'])
            self.player = Player.from_dict(game_state_data['player'])
            self.dealer = Player.from_dict(game_state_data['dealer'])
            self.num_hands = game_state_data['num_hands']
            
            self.player_hands = []
            for hand_data in game_state_data['player_hands']:
                # Reconstruct cards in hand
                hand_data['hand'] = [Card.from_dict(c) for c in hand_data['hand']]
                self.player_hands.append(hand_data)

            self.current_active_hand_index = game_state_data['current_active_hand_index']
            self.game_phase = game_state_data['game_phase']
            self.game_message = game_state_data['game_message']

    
    
    def _create_new_hand_state(self):
        return {
            "hand": [],
            "main_bet": 0,
            "side_bet_21_3": 0,
            "side_bet_perfect_pair": 0,
            "side_bets_results": {},
            "busted": False,
            "stood": False,
            "blackjack": False,
            "can_double": False,
            "can_split": False,
            "can_resplit": True, # NEW: Indicates if this hand can be split again
            "is_active": False,
            "result_message": ""
        }

    def to_dict(self):
        # Converts the entire BlackjackMultiGame object to a dictionary for serialization
        serializable_player_hands = []
        for hand_state in self.player_hands:
            # Convert cards in hand to serializable dicts
            hand_state_copy = hand_state.copy()
            hand_state_copy['hand'] = [card.to_dict() for card in hand_state['hand']]
            serializable_player_hands.append(hand_state_copy)

        return {
            "deck": self.deck.to_dict(),
            "player": self.player.to_dict(),
            "dealer": self.dealer.to_dict(),
            "num_hands": self.num_hands,
            "player_hands": serializable_player_hands,
            "current_active_hand_index": self.current_active_hand_index,
            "game_phase": self.game_phase,
            "game_message": self.game_message,
        }

    @staticmethod
    def from_dict(data):
        # This is the new method you need to add!
        # It reconstructs a BlackjackMultiGame object from its dictionary representation.
        return BlackjackMultiGame(
            player_name=data['player']['name'], # You can pass player_name and initial_chips
            initial_chips=data['player']['chips'], # These are defaults if not present
            num_hands=data['num_hands'],
            game_state_data=data # Pass the entire data to the __init__ to reconstruct
        )

    def reset_round(self):
        self.num_hands = 3 # Reset to default number of hands
        self.player_hands = []
        for i in range(self.num_hands):
            self.player_hands.append(self._create_new_hand_state())
        self.dealer.clear_hand()
        self.current_active_hand_index = -1
        self.game_phase = "betting"
        self.game_message = "Place your bets for all hands."
        
        # Reshuffle if deck is low (e.g., less than 20% left)
        if len(self.deck.cards) < (0.2 * self.deck.num_decks * 52):
             self.deck.generate_deck()
             self.deck.shuffle()
        return True # Indicate success

    def place_bets(self, bets_data):
        # bets_data expected format:
        # [{ "main_bet": x, "side_21_3": y, "side_pp": z }, ...] for each hand
        if self.game_phase != "betting":
            self.game_message = "Bets can only be placed during the betting phase."
            return False

        if not isinstance(bets_data, list) or len(bets_data) != self.num_hands:
            self.game_message = "Invalid bets data format. Expected list of bets for each hand."
            return False

        total_bet_amount = 0
        at_least_one_bet = False
        bet_hands = []
        bet_infos = []

        # Do NOT shrink player_hands. Always keep 3 hands.
        for i, bet_info in enumerate(bets_data):
            main_b = bet_info.get("main_bet", 0)
            side_21 = bet_info.get("side_21_3", 0)
            side_pp = bet_info.get("side_pp", 0)

            # Validate individual bets
            if not (isinstance(main_b, int) and main_b >= 0 and
                    isinstance(side_21, int) and side_21 >= 0 and
                    isinstance(side_pp, int) and side_pp >= 0):
                self.game_message = f"Invalid bet amounts for hand {i+1}. Bets must be non-negative integers."
                return False

            if main_b > 0: 
                at_least_one_bet = True

            total_bet_amount += (main_b + side_21 + side_pp)

        if not at_least_one_bet:
            self.game_message = "At least one main bet must be placed."
            return False   

        if total_bet_amount < 500:
            self.game_message = "Total bet must be at least $500."
            return False
        if total_bet_amount > 500000:
            self.game_message = "Total bet cannot exceed $500,000."
            return False

        if total_bet_amount > self.player.chips:
            self.game_message = "Not enough chips to cover all bets."
            return False

        # Deduct chips and store bets for all hands
        self.player.chips -= total_bet_amount
        for i, bet_info in enumerate(bets_data):
            self.player_hands[i]["main_bet"] = bet_info.get("main_bet", 0)
            self.player_hands[i]["side_bet_21_3"] = bet_info.get("side_21_3", 0)
            self.player_hands[i]["side_bet_perfect_pair"] = bet_info.get("side_pp", 0)
            self.player_hands[i]["result_message"] = "Bets placed." # Reset messages

        self.game_message = "Bets placed. Dealing cards..."
        self.game_phase = "dealing"
        return True

    def deal_initial_cards(self):
        if self.game_phase != "dealing":
            self.game_message = "Cards can only be dealt after bets are placed."
            return False
        
        self.dealer.clear_hand()
        self.dealer.receive_cards(self.deck.dealCards(2))

        for hand_state in self.player_hands:
            hand_state["hand"] = self.deck.dealCards(2) # Assign cards to this specific hand
            hand_state["busted"] = False
            hand_state["stood"] = False
            hand_state["blackjack"] = is_blackjack(hand_state["hand"])
            hand_state["result_message"] = "" # Clear previous messages

            # Evaluate and pay side bets for each hand
            if not self.dealer.hand: # Safety check
                self.game_message = "Error: Dealer has no cards for side bet evaluation."
                return False
            
            hand_state["side_bets_results"] = evaluate_side_bets(hand_state["hand"], self.dealer.hand[0])

            payout_21_3 = hand_state["side_bets_results"]["21+3"]["payout"] * hand_state["side_bet_21_3"]
            payout_pp = hand_state["side_bets_results"]["Perfect Pair"]["payout"] * hand_state["side_bet_perfect_pair"]
            
            if payout_21_3 > 0:
                self.player.chips += payout_21_3
                hand_state["result_message"] += f"Won ${payout_21_3} on 21+3 ({hand_state['side_bets_results']['21+3']['hand']}). "
            elif hand_state["side_bet_21_3"] > 0:
                hand_state["result_message"] += "Lost 21+3. "

            if payout_pp > 0:
                self.player.chips += payout_pp
                hand_state["result_message"] += f"Won ${payout_pp} on Perfect Pair ({hand_state['side_bets_results']['Perfect Pair']['type']}). "
            elif hand_state["side_bet_perfect_pair"] > 0:
                hand_state["result_message"] += "Lost Perfect Pair. "
            
            # Check for initial blackjack
            if hand_state["blackjack"]:
                if is_blackjack(self.dealer.hand):
                    hand_state["result_message"] += "Both have Blackjack! Push. "
                    self.player.chips += hand_state["main_bet"]
                    hand_state["stood"] = True # Effectively finished
                else:
                    hand_state["result_message"] += "Blackjack! Win 1.5x. "
                    self.player.chips += int(hand_state["main_bet"] * 2.5)
                    hand_state["stood"] = True # Effectively finished
        
        # If dealer has blackjack from start, all non-player-blackjack hands lose immediately
        if is_blackjack(self.dealer.hand):
            for hand_state in self.player_hands:
                if not hand_state["blackjack"]: # If player didn't also have blackjack
                    hand_state["result_message"] += "Dealer has Blackjack! You lose. "
                hand_state["stood"] = True # Mark all hands as finished
            self.game_phase = "round_over" # Go directly to end of round
            self.game_message = "Dealer has Blackjack! Round over."
        else:
            self.game_phase = "player_turns"
            self.game_message = "Your turn. Act on your hands."
            self.find_next_active_hand() # Set the first active hand

        return True

    def _get_hand_by_index(self, hand_index):
        if not (0 <= hand_index < self.num_hands):
            self.game_message = "Invalid hand index."
            return None
        return self.player_hands[hand_index]

    def find_next_active_hand(self):
        # Clear active status for all hands first
        for hand_state in self.player_hands:
            hand_state["is_active"] = False
            # Reset action eligibility for the next turn for all hands
            hand_state["can_double"] = False
            hand_state["can_split"] = False

        # Get list of hands with MAIN bets only (not just any bet)
        hands_with_main_bets = [(i, hand_state) for i, hand_state in enumerate(self.player_hands)
                          if hand_state["main_bet"] > 0]  # Only consider hands with main bets

        # Find the first unfinished hand with a main bet
        for bet_index, (hand_index, hand_state) in enumerate(hands_with_main_bets):
            if not hand_state["busted"] and not hand_state["stood"] and not hand_state["blackjack"]:
                self.current_active_hand_index = hand_index
                hand_state["is_active"] = True
                # Use bet_index + 1 for display numbering of active hands
                self.game_message = f"It's Hand {bet_index + 1}'s turn. "

                # Determine can_double eligibility for this specific hand
                if len(hand_state["hand"]) == 2 and 0 <= hand_value(hand_state["hand"]) <= 11 and hand_state["main_bet"] <= self.player.chips:
                    hand_state["can_double"] = True

                # Determine can_split eligibility for this specific hand
                max_total_hands = 4
                if (len(hand_state["hand"]) == 2 and
                    hand_state["hand"][0].rank_idx == hand_state["hand"][1].rank_idx and
                    hand_state["main_bet"] <= self.player.chips and
                    hand_state["can_resplit"] and
                    len(self.player_hands) < max_total_hands):
                    hand_state["can_split"] = True

                return True  # Found an active hand

        # If no active hands, all player hands are finished
        self.current_active_hand_index = -1
        self.game_phase = "dealer_turn"
        self.game_message = "All player hands finished. Dealer's turn."
        return False  # No active hand found
    
    def split(self, hand_index):
        hand_state = self._get_hand_by_index(hand_index)
        if not hand_state or self.game_phase != "player_turns" or not hand_state["is_active"] or not hand_state["can_split"]:
            self.game_message = "Cannot split this hand at this time."
            return False

        if hand_state["main_bet"] > self.player.chips:
            self.game_message = "Not enough chips to split this hand."
            return False

        # Deduct the new bet for the split hand
        self.player.chips -= hand_state["main_bet"]

        # Create a new hand state for the second split hand
        new_hand_state = self._create_new_hand_state()
        new_hand_state["main_bet"] = hand_state["main_bet"]
        new_hand_state["side_bet_21_3"] = hand_state["side_bet_21_3"] # Side bets carry over
        new_hand_state["side_bet_perfect_pair"] = hand_state["side_bet_perfect_pair"]

        # Move one card from the original hand to the new hand
        new_hand_state["hand"].append(hand_state["hand"].pop())

        # Deal one new card to the original hand
        hand_state["hand"].extend(self.deck.dealCards(1))
        # Deal one new card to the new split hand
        new_hand_state["hand"].extend(self.deck.dealCards(1))

        # Check for Aces special rule: if splitting Aces, they each get only one card and stand automatically.
        if hand_state["hand"][0].rank == 'A': # Check original hand's first card (it was an Ace)
            hand_state["stood"] = True
            new_hand_state["stood"] = True
            hand_state["can_resplit"] = False # Cannot re-split Aces
            new_hand_state["can_resplit"] = False # Cannot re-split Aces
            hand_state["result_message"] += "Stood on Ace split."
            new_hand_state["result_message"] += "Stood on Ace split."

        # After splitting, neither hand can split or double down again immediately
        hand_state["can_double"] = False
        hand_state["can_split"] = False
        new_hand_state["can_double"] = False
        new_hand_state["can_split"] = False

        # Insert the new hand immediately after the hand that was split
        self.player_hands.insert(hand_index + 1, new_hand_state)
        # Update the number of total hands
        self.num_hands = len(self.player_hands)

        self.game_message = f"Hand {hand_index+1} split. Play the first hand."
        # No need to call find_next_active_hand immediately here.
        # The current hand (hand_index) remains active for player's action
        # unless it was an Ace split (which auto-stands).
        if hand_state["stood"]: # If it was an Ace split, move to next hand
            self.find_next_active_hand()
        # Otherwise, the current hand (hand_index) remains active, and renderGameState will update it.

        return True

    def hit(self, hand_index):
        hand_state = self._get_hand_by_index(hand_index)
        if not hand_state or self.game_phase != "player_turns" or not hand_state["is_active"] or hand_state["busted"] or hand_state["stood"] or hand_state["blackjack"]:
            self.game_message = "Cannot hit this hand at this time."
            return False

        hand_state["hand"].extend(self.deck.dealCards(1))
        current_total = hand_value(hand_state["hand"])
        hand_state["can_double"] = False # Can't double after hitting

        # Get the display index (1-based) for this hand
        display_index = self._get_display_index(hand_index)

        if current_total > 21:
            hand_state["busted"] = True
            hand_state["result_message"] = "Busted!"
            self.game_message = f"Hand {display_index} busted!"
            self.find_next_active_hand() # Move to next hand
        elif current_total == 21:
            hand_state["stood"] = True # Automatically stands on 21
            hand_state["result_message"] = "Stood on 21."
            self.game_message = f"Hand {display_index} reached 21 and stood."
            self.find_next_active_hand() # Move to next hand
        else:
            self.game_message = f"Hand {display_index} hit. " # Keep the turn on this hand
        
        return True

    def stand(self, hand_index):
        hand_state = self._get_hand_by_index(hand_index)
        if not hand_state or self.game_phase != "player_turns" or not hand_state["is_active"] or hand_state["busted"] or hand_state["stood"] or hand_state["blackjack"]:
            self.game_message = "Cannot stand this hand at this time."
            return False
        
        display_index = self._get_display_index(hand_index)
        hand_state["stood"] = True
        hand_state["result_message"] = "Stood."
        self.game_message = f"Hand {display_index} stood."
        self.find_next_active_hand() # Move to next hand
        return True

    def double_down(self, hand_index):
        hand_state = self._get_hand_by_index(hand_index)
        if not hand_state or self.game_phase != "player_turns" or not hand_state["is_active"] or not hand_state["can_double"]:
            self.game_message = "Cannot double down at this time."
            return False
        
        # Check if player has enough chips for the additional bet
        if hand_state["main_bet"] > self.player.chips:
            self.game_message = "Not enough chips to double down this hand."
            return False

        display_index = self._get_display_index(hand_index)
        self.player.chips -= hand_state["main_bet"] # Deduct original bet again
        hand_state["main_bet"] *= 2 # Double the main bet
        hand_state["hand"].extend(self.deck.dealCards(1)) # Player gets one more card
        
        current_total = hand_value(hand_state["hand"])
        hand_state["can_double"] = False # Cannot double again

        if current_total > 21:
            hand_state["busted"] = True
            hand_state["result_message"] = "Doubled down and busted!"
            self.game_message = f"Hand {display_index} doubled down and busted!"
        else:
            hand_state["stood"] = True # Automatically stands after doubling
            hand_state["result_message"] = "Doubled down and stood."
            self.game_message = f"Hand {display_index} doubled down."

        self.find_next_active_hand() # Move to next hand
        return True

    def dealer_play(self):
        if self.game_phase != "dealer_turn":
            self.game_message = "It's not the dealer's turn."
            return False
        
        while hand_value(self.dealer.hand) < 17:
            self.dealer.receive_cards(self.deck.dealCards(1))
        
        self.game_message = "Dealer has finished playing."
        self.game_phase = "settlement"
        return True

    def settle_all_bets(self):
        if self.game_phase != "settlement" and self.game_phase != "round_over":
            self.game_message = "Game not in a state to settle bets."
            return False
        
        dealer_total = hand_value(self.dealer.hand)
        dealer_busted = dealer_total > 21
        
        for i, hand_state in enumerate(self.player_hands):
            # If hand already settled by blackjack or bust in deal_initial_cards
            if "result_message" in hand_state and ("Blackjack" in hand_state["result_message"] or "Busted!" in hand_state["result_message"]):
                continue # Already handled

            player_total = hand_value(hand_state["hand"])

            if hand_state["busted"]:
                hand_state["result_message"] = "Busted!"
            elif dealer_busted:
                hand_state["result_message"] = "Dealer busted! You win!"
                self.player.chips += hand_state["main_bet"] * 2
            elif player_total > dealer_total:
                hand_state["result_message"] = "You win!"
                self.player.chips += hand_state["main_bet"] * 2
            elif player_total == dealer_total:
                hand_state["result_message"] = "Push. Bet returned."
                self.player.chips += hand_state["main_bet"]
            else: # dealer_total > player_total
                hand_state["result_message"] = "Dealer wins."
        
        self.game_phase = "round_over"
        self.game_message = "Round finished. View results and start a new round."
        return True

    def get_game_state(self, reveal_dealer_card=False):
        # Prepare dealer hand data for JSON serialization
        dealer_hand_data = [card.to_dict() for card in self.dealer.hand]
        dealer_score = 0
        if self.dealer.hand:
            if reveal_dealer_card or self.game_phase in ["dealer_turn", "settlement", "round_over"]:
                dealer_score = hand_value(self.dealer.hand)
            else:
                dealer_score = card_value(self.dealer.hand[0])
                # Hide the second card
                if len(dealer_hand_data) > 1:
                    dealer_hand_data[1] = {"rank": "Hidden", "suit": "Hidden", "filename": "back.png"}
        
        # Prepare player hands data
        player_hands_for_display = []
        if self.game_phase == "betting":
            # During betting phase, show all hands
            for i, hand_state in enumerate(self.player_hands):
                hand_copy = hand_state.copy()
                hand_copy["hand"] = [card.to_dict() for card in hand_state["hand"]]
                hand_copy["total"] = hand_value(hand_state["hand"])
                hand_copy["hand_index"] = i  # Add the hand index
                player_hands_for_display.append(hand_copy)
        else:
            # During gameplay, only include hands with main bets
            hands_with_main_bets = [(i, hand_state) for i, hand_state in enumerate(self.player_hands)
                              if hand_state["main_bet"] > 0]  # Only consider hands with main bets
            
            # Create display data for each hand with main bets
            for bet_index, (i, hand_state) in enumerate(hands_with_main_bets):
                hand_copy = hand_state.copy()
                hand_copy["hand"] = [card.to_dict() for card in hand_state["hand"]]
                hand_copy["total"] = hand_value(hand_state["hand"])
                hand_copy["hand_index"] = i  # Keep original index for internal tracking
                hand_copy["display_index"] = bet_index  # Add display index for UI
                hand_copy["is_active"] = (i == self.current_active_hand_index)  # Set active state
                player_hands_for_display.append(hand_copy)

        return {
            "dealer_hand": dealer_hand_data,
            "dealer_total": dealer_score,
            "player_chips": self.player.chips,
            "num_hands": len(player_hands_for_display),  # Only count hands we're actually displaying
            "player_hands": player_hands_for_display,
            "current_active_hand_index": self.current_active_hand_index,
            "game_phase": self.game_phase,
            "game_message": self.game_message
        }

    def _get_display_index(self, hand_index):
        """Helper method to get the display index (1-based) for a hand based on its position among hands with main bets."""
        hands_with_main_bets = [(i, hand) for i, hand in enumerate(self.player_hands)
                          if hand["main_bet"] > 0]  # Only consider hands with main bets
        for display_index, (i, _) in enumerate(hands_with_main_bets, 1):
            if i == hand_index:
                return display_index
        return hand_index + 1  # Fallback to original index + 1 if not found