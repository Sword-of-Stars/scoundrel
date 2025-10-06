import random
from scripts.player import Player

class Agent():
    def __init__(self):
        pass

    def set_player(self):
        self.player = self

    def choose_run_away(self, state):
        return random.choice([True, False])
    
    def choose_action(self, state, options):
        return random.choice(options)
    

class NEAT_Agent():
    def __init__(self, net):
        self.net = net

        self.player = None

    def set_player(self, player: Player):
        self.player = player

    def choose_run_away(self, state):
        
        inpt = self.get_repr(state)

        choice = self.net.activate(inpt)[0]

        print(len(inpt))

        # return choice
        return choice > 0.5
    
    def choose_action(self, state, options):
        inpt = self.get_repr(state)

        choices = self.net.activate(inpt)[1:len(options)+1]
        max_index = max(choices)
        choice = choices.index(max_index)

        # return choice
        return options[choice]
    
    def get_repr(self, state):
        """
        Get normalized input representation for the neural network.
        All values scaled to roughly [-1, 1] or [0, 1] range.
        """
        inpt = []

        # Normalize health (0-20 -> 0-1)
        inpt.append(self.player.health / 20.0)

        # Normalize score (assume max reasonable score ~100, can adjust)
        inpt.append(min(self.player.score_so_far / 100.0, 1.0))

        # Normalize weapon capacity (1-14 -> 0-1, 0 if no weapon)
        weapon_capacity = 0 if self.player.weapon == None else self.player.weapon.get_strongest_possible()
        inpt.append(weapon_capacity / 14.0)

        # Boolean for potion availability (0 or 1)
        inpt.append(float(self.player.can_use_potion))

        # Encode up to 4 cards in the room
        for i in range(4):
            if i < len(state.room):
                card = state.room[i]
                # Normalize rank (1-14 -> 0-1)
                inpt.append(card.n_rank / 14.0)
                # One-hot encode suit (3 binary values)
                inpt.append(1.0 if card.n_suit == 0 else 0.0)  # Spades/Clubs
                inpt.append(1.0 if card.n_suit == 1 else 0.0)  # Diamonds
                inpt.append(1.0 if card.n_suit == 2 else 0.0)  # Hearts
            else:
                # No card in this slot
                inpt.extend([0.0, 0.0, 0.0, 0.0])

        return inpt