from scripts.card import Card

class Potion(Card):
    def __init__(self, suit, rank):
        super().__init__(suit, rank)

    def __repr__(self):
        return f"Potion ({self.rank})"