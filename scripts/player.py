from scripts.monster import Monster
from scripts.weapon import Weapon
from scripts.potion import Potion
from scripts.input_validation import validate_input


class Player():
    def __init__(self, name="Elric", human=True, agent=None):
        self.name = name

        self.MAXHEALTH = 20
        self.health = self.MAXHEALTH
        self._alive = True

        self.score_so_far = 0

        self.weapon: Weapon = None

        self.can_use_potion = True # has the player consumed a potion in the current room?

        # compatibility: human flag (True means prompts for input)
        self.human = human

        # optional agent object to automate choices
        self.agent = None if agent is None else agent.set_player(self)

    def reset(self):
        self.health = self.MAXHEALTH
        self._alive = True

        self.weapon: Weapon = None

        self.can_use_potion = True # has the player consumed a potion in the current room

        self.score_so_far = 0


    def choose_run_away(self, game=None):
        # human player prompts
        if self.human:
            return validate_input("\nWould you like to run away from this room? (y/n): ")

        # automated agent decides
        if self.agent is not None and hasattr(self.agent, "choose_run_away"):
            return self.agent.choose_run_away(game)

        # default for non-human without an agent
        return False

    def choose_action(self, options, game=None):
        if self.human:
            action = validate_input(f"Which action would you like to take? ({" ".join(str(i+1) for i in range(len(options)))}) ",
                                    valid_types={(str(i+1)): action for i, action in enumerate(options)})
            return action

        # agent-provided action: prefer an agent method if present
        if self.agent is not None and hasattr(self.agent, "choose_action"):
            # agent returns index; we map to Action object expected by Game
            idx = self.agent.choose_action(game, options)
            # guard
            if isinstance(idx, int) and 0 <= idx < len(options):
                return options[idx]

        # default is to pick the first option
        #print("Agent failed")
        return options[0]

    @property
    def alive(self):
        return self.health > 0
        
    def equip_weapon(self, weapon):
        self.weapon = weapon
        return f"You equipped {weapon}"

    def reset_potion_use(self):
        self.can_use_potion = True

    def use_potion(self, potion: Potion):
        if self.can_use_potion:
            tmp = self.health
            self.health = min(self.health + potion.n_rank, self.MAXHEALTH)
            self.can_use_potion = False

            return f"You drank {potion} and gained {self.health - tmp} health!"

        else:
            return f"You discarded {potion}"
    
    def fight_monster(self, monster: Monster):
        if self.weapon != None:
            damage, barehanded = self.weapon.add_monster(monster)
        else:
            damage = monster.n_rank
            barehanded = True

        self.take_damage(damage)

        if self.alive:
            self.score_so_far += monster.n_rank

        return f"You fought {monster} {"barehanded" if barehanded else "with your weapon"} and took {damage} damage"

    def take_damage(self, amount):
        self.health -= amount

    def show_stats(self):
        #print(self)
        pass

    def __repr__(self):
        msg =  "================\n"
        msg += "= Player Stats =\n"
        msg += "================\n"
        msg += f"Health: {self.health}\n"
        msg += f"{"No weapon equipped" if self.weapon == None else self.weapon}\n"
        return msg

