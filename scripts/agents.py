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
        inpt = [
        self.player.health,
        self.player.score_so_far
        ]

        # give it the highest card the weapon can handle
        weapon_capacity = 0 if self.player.weapon == None else self.player.weapon.get_strongest_possible()
        inpt.append(weapon_capacity)
        inpt.append(self.player.can_use_potion) # should always be true here

        # create encoded card representations
        for i in range(4):
            if i <= (len(state.room) - 1):
                card = state.room[i]
                rep = [card.n_rank, 0, 0, 0]
                rep[card.n_suit] = 1
                inpt.extend(rep)

            # handle rooms with less than 3 cards
            else: 
                inpt.extend([0,0,0,0])
        
        return inpt
