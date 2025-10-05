import random 

from typing import List

from scripts.card import Card
from scripts.monster import Monster
from scripts.weapon import Weapon
from scripts.potion import Potion

class Deck():
    """
    Cards are drawn from the front, inserted/appended to the back
    """
    def __init__(self):
        self.cards: List[Card] = []
        self.new_deck()

    def new_deck(self):
        # generate a deck with no jokers, no red face cards, and no red aces
        self.cards.clear()

        for suit in ["Spades", "Clubs", "Hearts", "Diamonds"]:
            ranks = [str(x) for x in range(2,11)]

            if suit in ("Spades", "Clubs"):
                ranks += ["J", "Q", "K", "A"]
                

                for rank in ranks:
                    self.cards.append(Monster(suit, rank))

            elif suit == "Hearts": # health potion
                for rank in ranks:
                    self.cards.append(Potion(suit, rank))

            elif suit == "Diamonds": # weapon
                for rank in ranks:
                    self.cards.append(Weapon(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def is_empty(self):
        return len(self.cards) <= 0

    def deal_card(self):
        if self.is_empty():
            raise Exception("[DECK] Attempted to draw more cards than are available in the deck")
        return self.cards.pop(0)
    
    def return_cards(self, cards: List[Card]):
        """
        Returns cards to the end of the deck
        """
        self.cards.extend(cards)

    def is_empty(self):
        return len(self.cards) == 0

    def __repr__(self):
        return "\n".join(str(card) for card in self.cards)
                
