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
        elif self.agent is not None:
            return self.agent.choose_run_away(game)

        # default for non-human without an agent
        return False

    def choose_action(self, options, game=None):
        if self.human:
            action = validate_input(f"Which action would you like to take? ({" ".join(str(i+1) for i in range(len(options)))}) ",
                                    valid_types={(str(i+1)): action for i, action in enumerate(options)})
            return action

        # agent-provided action: prefer an agent method if present
        elif self.agent is not None:
            # agent returns index; we map to Action object expected by Game
            idx = self.agent.choose_action(game, options)
            # guard
            if 0 <= idx < len(options):
                return options[idx]

        # default is to pick the first option
        return options[0]
    

    @property
    def alive(self):
        return self.health > 0
        
    def equip_weapon(self, weapon):
        prev_weapon = self.weapon
        self.weapon = weapon
        return f"You equipped {weapon}", prev_weapon
    
    def unequip_weapon(self, weapon, prev_weapon):
        """
        Undo weapon equipping
        weapon: The weapon that was equipped
        prev_weapon: The weapon that was previously equipped
        """
        self.weapon = prev_weapon

    def get_strongest_possible(self):
        if self.weapon == None:
            return 0
        return self.weapon.get_strongest_possible()

    def reset_potion_use(self):
        self.can_use_potion = True

    def use_potion(self, potion: Potion):
        if self.can_use_potion:
            prev_health = self.health
            health_gain = min(potion.n_rank, self.MAXHEALTH - self.health)
            self.health += health_gain
            self.can_use_potion = False

            return f"You drank {potion} and gained {health_gain} health!", prev_health

        else:
            return f"You discarded {potion}", self.health
        
    def undo_use_potion(self, potion: Potion, prev_health):
        self.can_use_potion = True
        self.health = prev_health
    
    def fight_monster(self, monster: Monster):
        if self.weapon != None:
            damage, barehanded = self.weapon.add_monster(monster)
        else:
            damage = monster.n_rank
            barehanded = True

        self.take_damage(damage)

        if self.alive:
            self.score_so_far += monster.n_rank

        return f"You fought {monster} {"barehanded" if barehanded else "with your weapon"} and took {damage} damage", damage, barehanded
    
    def undo_fight_monster(self, monster: Monster, damage: int, barehanded: bool):
        """
        Reverses the effects of fight_monster().
        
        Parameters:
            monster: the Monster that was fought
            damage: the damage taken during the fight
            barehanded: True if the fight was barehanded (no weapon)
        """
        # 1. Undo score gain (only if the character was alive after fight)
        if self.alive:
            self.score_so_far -= monster.n_rank

        # 2. Undo damage (heal back)
        self.health = min(self.health + damage, self.MAXHEALTH)

        # 3. Undo weapon interaction if applicable
        if not barehanded and self.weapon is not None:
            self.weapon.remove_monster(monster)
       
        # 4. Optionally recalc alive status
        self._alive = self.health > 0

    def take_damage(self, amount):
        self.health -= amount

    def show_stats(self):
        return self.__repr__()
        

    def __repr__(self):
        msg =  "================\n"
        msg += "= Player Stats =\n"
        msg += "================\n"
        msg += f"Health: {self.health}\n"
        msg += f"{"No weapon equipped" if self.weapon == None else self.weapon}\n"
        return msg

