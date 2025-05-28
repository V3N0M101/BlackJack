# player.py - Player Class managing the Hand, Chips, and Fold Status

'''
author: Syed Ghazi
date-created: 5/10/2025
'''

class Player:
    '''
    Player Class for Black Jack
    '''
    def __init__(self, name, chips=1000, is_Bot=False):
        self.name = name
        self.chips = chips
        self.hand = [] # Cards in player hand
        self.current_bet = 0 # Player's Bet
        self.folded = False
        self.is_Bot = is_Bot

    def receive_cards(self, cards):
        '''
        Cards dealt by dealer for the player
        :param cards: list
        :return: none
        '''
        self.hand = cards

    def bet(self, amount):
        '''
        The amount that the player bets
        :param amount: int
        :return: int
        '''
        if amount > self.chips:
            print("Not Enough Chips!\nGoing All-In!")
            amount = self.chips
        self.chips -= amount
        self.current_bet += amount
        return amount

    def fold(self):
        '''
        sets the players status as folded
        :return: none
        '''
        self.folded = True

    def reset_round(self):
        '''
        Resets the hand, bet amount, and fold status after each round
        :return: none
        '''
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def __str__(self):
        return (
        f"Player: {self.name}\n"
        f"Chips: {self.chips} | Current Bet: {self.current_bet:}\n"
        f"Hand: {', '.join(str(card) for card in self.hand)}\n"
        f"Folded: {'Yes' if self.folded else 'No'}"
    )

    def __repr__(self):
        return self.__str__()