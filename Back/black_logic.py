from deck import Deck
from player import Player

def card_value(card):
    rank = card.rank
    if rank >= 10:
        return 10
    elif rank == 0:
        return 11
    return rank + 1

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        val = card_value(card)
        total += val
        if card.rank == 0:
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

def evaluate_side_bets(player_hand, dealer_upcard):
    result = {
        "21+3": {"hand": None, "payout": 0},
        "Perfect Pair": {"type": None, "payout": 0}
    }

    if len(player_hand) != 2:
        return result

    combo = player_hand + [dealer_upcard]
    suits = [card.suit for card in combo]
    ranks = sorted([card.rank for card in combo])

    def is_flush():
        return suits[0] == suits[1] == suits[2]

    def is_straight():
        possible = [ranks, [r if r != 0 else 13 for r in ranks]]
        for r in possible:
            r.sort()
            if r[2] - r[1] == 1 and r[1] - r[0] == 1:
                return True
        return False

    def is_three_of_a_kind():
        return ranks[0] == ranks[1] == ranks[2]

    if is_three_of_a_kind() and is_flush():
        result["21+3"] = {"hand": "Suited Trips", "payout": 100}
    elif is_straight() and is_flush():
        result["21+3"] = {"hand": "Straight Flush", "payout": 40}
    elif is_three_of_a_kind():
        result["21+3"] = {"hand": "Three of a Kind", "payout": 30}
    elif is_straight():
        result["21+3"] = {"hand": "Straight", "payout": 10}
    elif is_flush():
        result["21+3"] = {"hand": "Flush", "payout": 5}

    c1, c2 = player_hand
    if c1.rank == c2.rank:
        if c1.suit == c2.suit:
            result["Perfect Pair"] = {"type": "Perfect Pair", "payout": 25}
        elif (c1.suit in ['♦', '♥'] and c2.suit in ['♦', '♥']) or (c1.suit in ['♠', '♣'] and c2.suit in ['♠', '♣']):
            result["Perfect Pair"] = {"type": "Colored Pair", "payout": 12}
        else:
            result["Perfect Pair"] = {"type": "Mixed Pair", "payout": 6}

    return result

class BlackjackGame:
    def __init__(self, player_name="You"):
        self.deck = Deck()
        self.deck.generate_deck()
        self.deck.shuffle()

        self.player = Player(player_name)
        self.dealer = Player("Dealer", is_Bot=True)
        self.bet_amount = 0
        self.side_bet_21_3 = 0
        self.side_bet_perfect_pair = 0
        self.player_blackjack = False
        self.dealer_blackjack = False
        self.finished = False
        self.side_bets = {}  # To store results

    def place_bets(self):
        while True:
            try:
                main_bet = int(input(f"You have {self.player.chips} chips. Enter your main bet: "))
                if main_bet <= 0 or main_bet > self.player.chips:
                    print("Invalid bet amount.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        # Side bets (optional)
        side_bet_21_3 = 0
        side_bet_pp = 0

        def get_side_bet(name):
            while True:
                try:
                    bet = input(f"Enter your side bet amount for {name} (or 0 to skip): ")
                    bet = int(bet)
                    if bet < 0 or bet > self.player.chips - main_bet:
                        print(f"Invalid amount. You have {self.player.chips - main_bet} chips available for side bets.")
                        continue
                    return bet
                except ValueError:
                    print("Please enter a valid number.")

        side_bet_21_3 = get_side_bet("21+3")
        side_bet_pp = get_side_bet("Perfect Pair")

        total_bets = main_bet + side_bet_21_3 + side_bet_pp
        if total_bets > self.player.chips:
            print("Not enough chips to cover all bets. Please bet again.")
            return self.place_bets()

        # Deduct all bets from chips now
        self.player.chips -= total_bets

        self.bet_amount = main_bet
        self.side_bet_21_3 = side_bet_21_3
        self.side_bet_perfect_pair = side_bet_pp

        print(f"\nMain bet: {main_bet} chips")
        if side_bet_21_3 > 0:
            print(f"Side bet 21+3: {side_bet_21_3} chips")
        if side_bet_pp > 0:
            print(f"Side bet Perfect Pair: {side_bet_pp} chips")

    def deal(self):
        self.player.receive_cards(self.deck.dealCards(2))
        self.dealer.receive_cards(self.deck.dealCards(2))

        # Evaluate side bets only if player placed them
        self.side_bets = evaluate_side_bets(self.player.hand, self.dealer.hand[0])
        
        # Payout side bets based on user's bet
        payout_21_3 = self.side_bets["21+3"]["payout"] * self.side_bet_21_3
        payout_pp = self.side_bets["Perfect Pair"]["payout"] * self.side_bet_perfect_pair

        if payout_21_3 > 0:
            print(f"\nYou won {payout_21_3} chips on 21+3 side bet! ({self.side_bets['21+3']['hand']})")
            self.player.chips += payout_21_3
        elif self.side_bet_21_3 > 0:
            print("\nYou lost your 21+3 side bet.")

        if payout_pp > 0:
            print(f"\nYou won {payout_pp} chips on Perfect Pair side bet! ({self.side_bets['Perfect Pair']['type']})")
            self.player.chips += payout_pp
        elif self.side_bet_perfect_pair > 0:
            print("\nYou lost your Perfect Pair side bet.")

        self.player_blackjack = is_blackjack(self.player.hand)
        self.dealer_blackjack = is_blackjack(self.dealer.hand)

    def show_hands(self, reveal_dealer=False):
        print("\nDealer's Hand:")
        if reveal_dealer:
            for card in self.dealer.hand:
                print(f"  {card}")
            print(f"Dealer total: {hand_value(self.dealer.hand)}")
        else:
            print(f"  {self.dealer.hand[0]}")
            print("  [Hidden card]")

        print("\nYour Hand:")
        for card in self.player.hand:
            print(f"  {card}")
        print(f"Your total: {hand_value(self.player.hand)}")
        print(f"Your chips: {self.player.chips}")

    def hit(self):
        self.player.hand += self.deck.dealCards(1)
        print("\nYou chose to hit.")
        self.show_hands()

        if hand_value(self.player.hand) > 21:
            print("\nYou busted! Dealer wins.")
            self.finished = True

    def stand(self):
        print("\nYou chose to stand.")
        self.finished = True

        # Dealer hits until 17 or more
        while hand_value(self.dealer.hand) < 17:
            self.dealer.hand += self.deck.dealCards(1)

        self.show_hands(reveal_dealer=True)

        player_total = hand_value(self.player.hand)
        dealer_total = hand_value(self.dealer.hand)

        if self.dealer_blackjack:
            print("\nDealer has blackjack!")
        if self.player_blackjack:
            print("\nYou have blackjack!")

        if dealer_total > 21:
            print("\nDealer busted! You win!")
            self.player.chips += self.bet_amount * 2
        elif player_total > dealer_total:
            print("\nYou win!")
            self.player.chips += self.bet_amount * 2
        elif player_total == dealer_total:
            print("\nPush. Bet returned.")
            self.player.chips += self.bet_amount
        else:
            print("\nDealer wins.")

    def play(self):
        print(f"Welcome {self.player.name} to Blackjack!\n")
        self.place_bets()
        self.deal()
        self.show_hands()

        # Handle blackjack cases immediately
        if self.player_blackjack:
            if self.dealer_blackjack:
                print("\nBoth you and dealer have blackjack! Push.")
                self.player.chips += self.bet_amount  # Return main bet
            else:
                print("\nBlackjack! You win 1.5x your bet!")
                self.player.chips += int(self.bet_amount * 2.5)
            self.finished = True
            return

        if self.dealer_blackjack:
            print("\nDealer has blackjack. You lose.")
            self.finished = True
            return

        # Main player loop
        while not self.finished:
            choice = input("\nDo you want to Hit or Stand? (h/s): ").lower()
            if choice == 'h':
                self.hit()
            elif choice == 's':
                self.stand()
            else:
                print("Invalid choice, please enter 'h' or 's'.")

        print(f"\nGame over! You have {self.player.chips} chips remaining.")

class BlackjackMultiGame:
    def __init__(self, player_name="You", num_games=3):
        self.deck = Deck()
        self.deck.generate_deck()
        self.deck.shuffle()

        self.dealer = Player("Dealer", is_Bot=True)
        self.player = Player(player_name)  # Add a single main player instance here

        self.num_games = num_games

        self.games = [
            {
                "player": self.player,
                "hand": [],
                "bet": 0,
                "side_21_3": 0,
                "side_pp": 0,
                "side_bets": {},
                "blackjack": False,
                "finished": False
            }
            for i in range(num_games)
        ]

    def place_bets(self, player):
        for idx, game in enumerate(self.games):
            print(f"\n--- Placing bets for Game {idx + 1} ---")
            
            # MAIN BET
            while True:
                try:
                    main_bet = int(input(f"Enter main bet for Hand {idx + 1} (chips available: {player.chips}): "))
                    if main_bet <= player.chips:
                        game["bet"] = main_bet
                        player.chips -= main_bet
                        break
                    else:
                        print("Not enough chips for that bet.")
                except ValueError:
                    print("Invalid bet. Please enter a number.")

            # SIDE BET FUNCTION
            def get_side_bet(name):
                while True:
                    try:
                        amount = int(input(f"Side bet for {name} (0 to skip, chips available: {player.chips}): "))
                        if amount == 0:
                            return 0
                        elif amount <= player.chips:
                            player.chips -= amount
                            return amount
                        else:
                            print("Not enough chips for that side bet.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            game["side_21_3"] = get_side_bet("21+3")
            game["side_pp"] = get_side_bet("Perfect Pair")

    def deal_initial_cards(self):
        # Deal to dealer
        self.dealer.receive_cards(self.deck.dealCards(2))

        # Deal to each player hand
        for game in self.games:
            cards = self.deck.dealCards(2)
            game["hand"] = cards
            game["player"].hand = cards

            # Evaluate side bets
            game["side_bets"] = evaluate_side_bets(game["hand"], self.dealer.hand[0])

            # Apply side bet payouts
            sb = game["side_bets"]
            payout_21 = sb["21+3"]["payout"] * game["side_21_3"]
            payout_pp = sb["Perfect Pair"]["payout"] * game["side_pp"]
            game["player"].chips += payout_21 + payout_pp

            # Blackjack check
            game["blackjack"] = is_blackjack(game["hand"])

    def play_hand(self, idx, game):
        print(f"\n--- Playing Hand {idx + 1} ---")
        player = game["player"]

        if game["blackjack"]:
            print("Blackjack!")
            player.chips += int(game["bet"] * 2.5)
            game["finished"] = True
            return

        while not game["finished"]:
            print(f"\nYour hand: {', '.join(str(c) for c in game['hand'])} (Total: {hand_value(game['hand'])})")
            choice = input("Hit or Stand? (h/s): ").lower()
            if choice == "h":
                game["hand"].append(self.deck.dealCards(1)[0])
                if hand_value(game["hand"]) > 21:
                    print("Busted!")
                    game["finished"] = True
            elif choice == "s":
                game["finished"] = True
            else:
                print("Invalid input.")

    def resolve_dealer(self):
        print("\n--- Dealer's Turn ---")
        while hand_value(self.dealer.hand) < 17:
            self.dealer.hand.append(self.deck.dealCards(1)[0])
        print(f"Dealer's hand: {', '.join(str(c) for c in self.dealer.hand)} (Total: {hand_value(self.dealer.hand)})")

    def settle_bets(self):
        dealer_total = hand_value(self.dealer.hand)
        for idx, game in enumerate(self.games):
            if game["blackjack"]:
                continue  # Already settled
            player_total = hand_value(game["hand"])
            print(f"\n--- Result for Hand {idx + 1} ---")
            if player_total > 21:
                print("You busted.")
            elif dealer_total > 21 or player_total > dealer_total:
                print("You win!")
                game["player"].chips += game["bet"] * 2
            elif player_total == dealer_total:
                print("Push.")
                game["player"].chips += game["bet"]
            else:
                print("Dealer wins.")

    def play(self):
        self.place_bets(self.player)
        self.deal_initial_cards()

        # Show dealer's upcard before player decisions
        print("\nDealer's upcard is:", self.dealer.hand[0])

        # List to store chip count before each hand
        chips_before_hand = []

        # Store chip count before first hand
        chips_before_hand.append(self.player.chips)

        for idx, game in enumerate(self.games):
            self.play_hand(idx, game)

        self.resolve_dealer()
        self.settle_bets()

        print("\n--- Round Results ---")
        print(f"\nFinal chip count: {self.player.chips}")

if __name__ == "__main__":
    game = BlackjackMultiGame()
    game.play()