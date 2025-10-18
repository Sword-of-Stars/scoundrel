# value reference
lut = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

sut = {
    "Spades": 0,
    "Clubs": 0,
    "Diamonds": 1,
    "Hearts": 2,
}

class Card():
    def __init__(self, suit, rank):
        self.suit = suit

        self.n_suit = sut[suit]

        self.rank = rank
        self.n_rank = lut[rank]

    def __repr__(self):
        return f"{self.rank}{self.suit}"