import random

class Agent():
    def __init__(self, name="null"):
        self.name = name

    def choose_run_away(self, state):
        pass

    def choose_action(self, state, options):
        pass

class RandomAgent(Agent):
    def __init__(self):
        super().__init__(name="random")
    
    def choose_run_away(self, state):
        return random.choice([True, False])
    
    def choose_action(self, state, options):
        return random.choice(options)