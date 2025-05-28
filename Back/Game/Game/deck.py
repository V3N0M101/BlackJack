# deck.py - Creates a deck and handles the shuffling and dealing of cards

'''
author: Syed Ghazi
date-created: 5/10/2025
'''

from random import shuffle

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

RANKS = ['A','2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


class Card:
    '''
    class for individual card
    '''
    def __init__(self, rank, suit): # constructor class for Card
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{RANKS[self.rank]} of {SUITS[self.suit]}" # return (Rank of Suit) as the string representation of Card

    def __repr__(self):
        return self.__str__()

class Deck:
    def __init__(self):
        self.deck = [] # initialize deck as an empty list

    def generate_deck(self):
        '''
        Generates a deck and appends it to the deck list
        :return: none
        '''
        self.deck = [] # reset in case a deck already exists
        for i in range(4):
            for j in range(13):
                self.deck.append(Card(j,i))

    def shuffle(self):
        '''
        shuffles the deck in the deck list
        :return: none
        '''
        shuffle(self.deck) # shuffles the deck

    def dealCards(self, num=1):
        '''
        deals cards to players
        :param num: int
        :return: list
        '''
        dealt_cards = []
        if num > len(self.deck):
            print("Not Enough Cards in Deck")
            return dealt_cards
        else:
            for i in range(num):
                card = self.deck.pop()
                dealt_cards.append(card)
            return dealt_cards