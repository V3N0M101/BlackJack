# blackjack_logic.py - Updated for 3:2 blackjack payout

from deck import Deck
from player import Player

def card_value(card):
    """Returns the Blackjack value of a card."""
    rank = card.rank
    if rank >= 10:
        return 10
    elif rank == 0:
        return 11
    return rank + 1

def hand_value(hand):
    """Calculates the total value of a hand, adjusting for Aces."""
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

def play_blackjack():
    deck = Deck()
    deck.generate_deck()
    deck.shuffle()

    player = Player("You")
    dealer = Player("Dealer", is_Bot=True)

    print(f"\nWelcome to Blackjack! You have {player.chips} chips.")
    try:
        bet_amount = int(input("Place your bet: "))
    except ValueError:
        print("Invalid input. Betting 100 by default.")
        bet_amount = 100

    bet_amount = player.bet(bet_amount)

    # Deal initial cards
    player.receive_cards(deck.dealCards(2))
    dealer.receive_cards(deck.dealCards(2))

    print(f"\n{player}")
    print(f"Dealer shows: {dealer.hand[0]}\n")

    # Check for immediate blackjacks
    player_blackjack = is_blackjack(player.hand)
    dealer_blackjack = is_blackjack(dealer.hand)

    if player_blackjack or dealer_blackjack:
        print(f"Your hand: {', '.join(str(card) for card in player.hand)} (Value: {hand_value(player.hand)})")
        print(f"Dealer's hand: {', '.join(str(card) for card in dealer.hand)} (Value: {hand_value(dealer.hand)})")

        if player_blackjack and dealer_blackjack:
            print("Both have Blackjack! Push.")
            player.chips += bet_amount  # Return bet
        elif player_blackjack:
            print("Blackjack! You win 3:2 payout!")
            player.chips += int(bet_amount * 2.5)
        else:
            print("Dealer has Blackjack. You lose.")
        return

    # Player's turn
    while hand_value(player.hand) < 21:
        move = input("Hit or Stand? (h/s): ").lower()
        if move == 'h':
            player.hand += deck.dealCards(1)
            print(f"Your hand: {', '.join(str(card) for card in player.hand)} (Value: {hand_value(player.hand)})")
        elif move == 's':
            break
        else:
            print("Invalid input. Type 'h' or 's'.")

    player_total = hand_value(player.hand)
    if player_total > 21:
        print("You busted! Dealer wins.")
        return

    # Dealer's turn
    print(f"\nDealer's hand: {', '.join(str(card) for card in dealer.hand)} (Value: {hand_value(dealer.hand)})")
    while hand_value(dealer.hand) < 17:
        dealer.hand += deck.dealCards(1)
        print(f"Dealer hits: {dealer.hand[-1]} (Total: {hand_value(dealer.hand)})")

    dealer_total = hand_value(dealer.hand)
    print(f"\nFinal Hands:\n{player.name}: {player_total}\nDealer: {dealer_total}")

    # Determine outcome
    if dealer_total > 21 or player_total > dealer_total:
        print("You win!")
        player.chips += bet_amount * 2
    elif dealer_total == player_total:
        print("Push.")
        player.chips += bet_amount
    else:
        print("Dealer wins.")

    print(f"\nYour current chip count: {player.chips}")

if __name__ == "__main__":
    play_blackjack()
