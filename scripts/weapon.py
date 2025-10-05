from typing import List
from scripts.card import Card
from scripts.monster import Monster

class Weapon(Card):
    def __init__(self, suit, rank):
        super().__init__(suit, rank)
        self.monsters: List[Monster] = []

    def can_add_monster(self, monster: Monster):
        """
        Checks whether a given weapon can accept a monster
        """
        # if the weapon has no monsters on it, it can take one
        if self.monsters == []: return True 

        # you can only fight monsters lesser than the monster already on your weapon
        return monster.n_rank < min(m.n_rank for m in self.monsters)
    
    def get_strongest_possible(self):
        if self.monsters == []: return 14
        return min(m.n_rank for m in self.monsters)

    
    def add_monster(self, monster: Monster):
        """
        Adds a monster to the weapon, if legal

        Returns (damage taken, barehanded or not)
        """
        if self.monsters == []:
            self.monsters.append(monster)
            return max(0, monster.n_rank - self.n_rank), False

        if self.can_add_monster(monster):
            self.monsters.append(monster)
            return 0, False # if the weapon can take the monster, no damage is taken
        
        return monster.n_rank, True # otherwise, the player fights it barehanded
    
    def __repr__(self):
        m_string = "no monsters" if len(self.monsters) == 0 else self.monsters[-1] #" ".join(str(m) for m in self.monsters)
        return f"Weapon ({self.rank}) with {m_string} attached"