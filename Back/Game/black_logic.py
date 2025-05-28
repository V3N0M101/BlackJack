# blackjack_logic.py - Handles the core logic of the Blackjack game
'''
author: Syed Ghazi
date-created: 5/28/2025
'''

from deck import Deck
from player import Player

def card_value(card):
    """Returns the Blackjack value of a card."""
    rank = card.rank
    if rank >= 10:  # J, Q, K
        return 10
    elif rank == 0:  # Ace
        return 11
    return rank + 1  # 2-10

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

    # Initial deal
    player.receive_cards(deck.dealCards(2))
    dealer.receive_cards(deck.dealCards(2))

    print(f"\n{player}")
    print(f"Dealer shows: {dealer.hand[0]}\n")

    # Player turn
    while hand_value(player.hand) < 21:
        move = input("Hit or Stand? (h/s): ").lower()
        if move == 'h':
            player.hand += deck.dealCards(1)
            print(f"\nYour hand: {', '.join(str(card) for card in player.hand)} (Value: {hand_value(player.hand)})")
        elif move == 's':
            break
        else:
            print("Invalid input. Type 'h' to Hit or 's' to Stand.")

    player_total = hand_value(player.hand)
    if player_total > 21:
        print("\nYou busted! Dealer wins.")
        return

    # Dealer turn
    print(f"\nDealer's hand: {', '.join(str(card) for card in dealer.hand)} (Value: {hand_value(dealer.hand)})")
    while hand_value(dealer.hand) < 17:
        dealer.hand += deck.dealCards(1)
        print(f"Dealer hits: {dealer.hand[-1]} (Total: {hand_value(dealer.hand)})")

    dealer_total = hand_value(dealer.hand)
    print(f"\nFinal Hands:\n{player.name}: {hand_value(player.hand)}\nDealer: {dealer_total}")

    # Determine winner
    if dealer_total > 21 or player_total > dealer_total:
        print("You win!")
    elif dealer_total == player_total:
        print("Push. It's a tie!")
    else:
        print("Dealer wins.")

if __name__ == "__main__":
    play_blackjack()