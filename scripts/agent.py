import random
import itertools
from scripts.game import Game, Player, Monster, Weapon, Potion

class Agent():
    def __init__(self, name="null"):
        self.name = name

    def choose_run_away(self, state):
        return random.choice([True, False])
    
    def choose_action(self, state, options):
        return random.randint(0, len(options))
    
    def lookahead(self, state: Game):
        """
        Given our current health, weapons, and room config, 
        is it possible to beat the room?

        Basically, we can defeat the room if the descending 
        monster cards 
        """
        player = state.player
    
        # simulate all possible orders of taking cards
        options = state.generate_options()

        orders = list(itertools.permutations(list(range(0, len(state.room))), min(len(state.room), 3))) # all three possibilities of options
        metrics = {}
        for i, actionSet in enumerate(orders):
            for a in actionSet:
                options[a].execute()
            metrics[actionSet] = {
                "health": player.health/player.MAXHEALTH,
                "score": player.score_so_far/208,
            }
            for a in reversed(actionSet):
                options[a].reverse()

        return metrics

class RandomAgent(Agent):
    def __init__(self):
        super().__init__(name="random")
    
    def choose_run_away(self, state):
        return random.choice([True, False])
    
    def choose_action(self, state, options):
        return random.randint(0, len(options)) 
    
        
class IntelAgent(Agent):
    """
    This agent will seek to minimize its loss of health.

    Run Away strategy:
        If the expected room value is higher than average risk, run away.
    """
    def __init__(self, health_weight = 0.5, STAY_AND_FIGHT_THRESHOLD=1.0):
        super().__init__(name="intel")
        
        self.health_weight = health_weight
        self.score_weight = 1 - health_weight
        self.STAY_AND_FIGHT_THRESHOLD = STAY_AND_FIGHT_THRESHOLD

        self.eval_func = lambda stats: (
            stats["health"] * self.health_weight +
            stats["score"] * self.score_weight
        )

    def evaluate_options(self, metrics):
        """
        Given a dict {action_sequence: {"health": x, "score": y}}, 
        pick the best viable one (player must survive).
        """
        viable = {k: v for k, v in metrics.items() if v["health"] > 0}
        if not viable:
            # all options lead to death
            return None, None

        best_action = max(viable, key=lambda k: self.eval_func(viable[k]))
        best_stats = viable[best_action]
        return best_action, best_stats

    def choose_run_away(self, state):
        metrics = self.lookahead(state)
        best_action, best_stats = self.evaluate_options(metrics)

        if best_stats is None:
            return True  # all options lethal → run away

        # stay if the evaluation is above threshold
        return self.eval_func(best_stats) <= self.STAY_AND_FIGHT_THRESHOLD

    def choose_action(self, state, options):
        metrics = self.lookahead(state)
        best_action, best_stats = self.evaluate_options(metrics)

        if best_action is None:
            return random.randint(0, len(options))  # fallback

        # choose the first action in the best sequence
        return best_action[0]


class IntelAgent2(Agent):
    """
    This agent will seek to minimize its loss of health.

    Run Away strategy:
        If the expected room value is higher than average risk, run away.
    """
    def __init__(self, health_weight = 0.4, score_weight=0.4, STAY_AND_FIGHT_THRESHOLD=1.0):
        super().__init__(name="intel")
        
        self.health_weight = health_weight
        self.score_weight = score_weight
        self.weapon_weight = 1 - self.health_weight - self.score_weight
        self.STAY_AND_FIGHT_THRESHOLD = STAY_AND_FIGHT_THRESHOLD

        self.eval_func = lambda stats: (
            stats["health"] * self.health_weight +
            stats["score"] * self.score_weight +
            stats["weapon"] * self.weapon_weight
        )

    def evaluate_options(self, metrics):
        """
        Given a dict {action_sequence: {"health": x, "score": y}}, 
        pick the best viable one (player must survive).
        """
        viable = {k: v for k, v in metrics.items() if v["health"] > 0}
        if not viable:
            # all options lead to death
            return None, None

        best_action = max(viable, key=lambda k: self.eval_func(viable[k]))
        best_stats = viable[best_action]
        return best_action, best_stats

    def choose_run_away(self, state):
        metrics = self.lookahead(state)
        best_action, best_stats = self.evaluate_options(metrics)

        if best_stats is None:
            return True  # all options lethal → run away

        # stay if the evaluation is above threshold
        return self.eval_func(best_stats) <= self.STAY_AND_FIGHT_THRESHOLD

    def choose_action(self, state, options):
        metrics = self.lookahead(state)
        best_action, best_stats = self.evaluate_options(metrics)

        if best_action is None:
            return random.randint(0, len(options))  # fallback

        # choose the first action in the best sequence
        return best_action[0]
    
    def lookahead(self, state: Game):
        """
        Given our current health, weapons, and room config, 
        is it possible to beat the room?

        Basically, we can defeat the room if the descending 
        monster cards 
        """
        player = state.player
    
        # simulate all possible orders of taking cards
        options = state.generate_options()

        orders = list(itertools.permutations(list(range(0, len(state.room))), min(len(state.room), 3))) # all three possibilities of options
        metrics = {}
        for i, actionSet in enumerate(orders):
            for a in actionSet:
                options[a].execute()
            metrics[actionSet] = {
                "health": player.health/player.MAXHEALTH,
                "score": player.score_so_far/208,
                "weapon": player.get_strongest_possible()/14
            }
            for a in reversed(actionSet):
                options[a].reverse()

        return metrics