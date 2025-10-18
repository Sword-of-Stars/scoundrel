import unittest
from scripts.game import Game
from scripts.player import Player
from scripts.monster import Monster
from scripts.weapon import Weapon
from scripts.potion import Potion
from scripts.action import Action

class TestActionUndo(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game = Game()
        self.player = self.game.player

    def assert_game_state_equal(self, health, weapon, score, can_use_potion):
        """Helper method to verify game state"""
        self.assertEqual(self.player.health, health)
        self.assertEqual(self.player.weapon, weapon)
        self.assertEqual(self.player.score_so_far, score)
        self.assertEqual(self.player.can_use_potion, can_use_potion)

    def test_fight_monster_barehanded_undo(self):
        """Test that undoing a barehanded monster fight restores the game state"""
        initial_health = self.player.health
        initial_score = self.player.score_so_far
        monster = Monster("Spades", "5")  # Monster of strength 5
        
        # Create and execute fight action
        action = Action(self.player.fight_monster, monster, "Fight", rev=self.player.undo_fight_monster)
        action.execute()
        
        # State after fight: health reduced by 5, score increased by 5
        self.assertEqual(self.player.health, initial_health - 5)
        self.assertEqual(self.player.score_so_far, initial_score + 5)
        
        # Undo the action
        action.reverse()
        
        # Verify state is restored
        self.assert_game_state_equal(initial_health, None, initial_score, True)

    def test_fight_monster_with_weapon_undo(self):
        """Test that undoing a monster fight with weapon restores the game state"""
        weapon = Weapon("Diamonds", "6")  # Weapon of strength 6
        monster = Monster("Spades", "5")  # Monster of strength 5
        
        # Equip weapon first
        self.player.equip_weapon(weapon)
        initial_health = self.player.health
        initial_score = self.player.score_so_far
        
        # Create and execute fight action
        action = Action(self.player.fight_monster, monster, "Fight", rev=self.player.undo_fight_monster)
        action.execute()
        
        # State after fight: no damage taken (weapon stronger than monster), score increased
        self.assertEqual(self.player.health, initial_health)
        self.assertEqual(self.player.score_so_far, initial_score + 5)
        self.assertTrue(monster in self.player.weapon.monsters)
        
        # Undo the action
        action.reverse()
        
        # Verify state is restored
        self.assertEqual(self.player.health, initial_health)
        self.assertEqual(self.player.score_so_far, initial_score)
        self.assertFalse(monster in self.player.weapon.monsters)

    def test_equip_weapon_undo(self):
        """Test that undoing weapon equipping restores the game state"""
        initial_weapon = self.player.weapon  # None initially
        new_weapon = Weapon("Diamonds", "6")
        
        # Create and execute equip action
        action = Action(self.player.equip_weapon, new_weapon, "Equip", rev=self.player.unequip_weapon)
        action.execute()
        
        # Verify weapon is equipped
        self.assertEqual(self.player.weapon, new_weapon)
        
        # Undo the action
        action.reverse()
        
        # Verify state is restored
        self.assert_game_state_equal(20, initial_weapon, 0, True)

    def test_use_potion_drink_undo(self):
        """Test that undoing potion drinking restores the game state"""
        self.player.health = 10  # Set health to 10 to test healing
        initial_health = self.player.health
        potion = Potion("Hearts", "5")  # Healing potion of strength 5
        
        # Create and execute potion action
        action = Action(self.player.use_potion, potion, "Drink", rev=self.player.undo_use_potion)
        action.execute()
        
        # Verify potion effects
        self.assertEqual(self.player.health, 15)  # Health increased by 5
        self.assertFalse(self.player.can_use_potion)  # Can't use another potion
        
        # Undo the action
        action.reverse()
        
        # Verify state is restored
        self.assert_game_state_equal(initial_health, None, 0, True)

    def test_use_potion_discard_undo(self):
        """Test that undoing potion discard (when can't drink) restores the game state"""
        self.player.can_use_potion = False  # Set state to can't use potion
        initial_health = self.player.health
        potion = Potion("Hearts", "5")
        
        # Create and execute potion action
        action = Action(self.player.use_potion, potion, "Discard")
        action.execute()
        
        # Verify state unchanged
        self.assert_game_state_equal(initial_health, None, 0, False)
        
        # Note: No undo for discard action as it's not reversible

    def test_multiple_actions_and_reversals(self):
        """Test a sequence of different actions and their reversals"""
        # Initial state
        initial_health = self.player.health
        initial_score = self.player.score_so_far
        
        # Create test objects
        weapon1 = Weapon("Diamonds", "6")  # Weapon of strength 6
        weapon2 = Weapon("Diamonds", "8")  # Stronger weapon
        monster1 = Monster("Spades", "4")  # Weak monster
        potion = Potion("Hearts", "5")     # Healing potion
        monster2 = Monster("Spades", "7")   # Stronger monster
        
        # Create actions
        action1 = Action(self.player.equip_weapon, weapon1, "Equip", rev=self.player.unequip_weapon)
        action2 = Action(self.player.fight_monster, monster1, "Fight", rev=self.player.undo_fight_monster)
        action3 = Action(self.player.equip_weapon, weapon2, "Equip", rev=self.player.unequip_weapon)
        action4 = Action(self.player.use_potion, potion, "Drink", rev=self.player.undo_use_potion)
        action5 = Action(self.player.fight_monster, monster2, "Fight", rev=self.player.undo_fight_monster)
        
        # Execute actions in sequence
        # 1. Equip first weapon
        action1.execute()
        self.assertEqual(self.player.weapon, weapon1)
        
        # 2. Fight weak monster
        action2.execute()
        self.assertEqual(self.player.score_so_far, initial_score + 4)  # Score increased by monster rank
        self.assertTrue(monster1 in weapon1.monsters)
        
        # 3. Equip stronger weapon
        action3.execute()
        self.assertEqual(self.player.weapon, weapon2)
        
        # 4. Drink potion
        action4.execute()
        self.assertFalse(self.player.can_use_potion)
        
        # 5. Fight stronger monster
        action5.execute()
        self.assertEqual(self.player.score_so_far, initial_score + 4 + 7)  # Score increased by both monsters
        self.assertTrue(monster2 in weapon2.monsters)
        
        # Now reverse actions in LIFO order
        # 5. Undo second fight
        action5.reverse()
        self.assertEqual(self.player.score_so_far, initial_score + 4)
        self.assertFalse(monster2 in weapon2.monsters)
        
        # 4. Undo potion
        action4.reverse()
        self.assertTrue(self.player.can_use_potion)
        
        # 3. Undo second weapon equip
        action3.reverse()
        self.assertEqual(self.player.weapon, weapon1)
        
        # 2. Undo first fight
        action2.reverse()
        self.assertEqual(self.player.score_so_far, initial_score)
        self.assertFalse(monster1 in weapon1.monsters)
        
        # 1. Undo first weapon equip
        action1.reverse()
        self.assertEqual(self.player.weapon, None)
        
        # Verify final state matches initial state
        self.assert_game_state_equal(initial_health, None, initial_score, True)

    def test_mixed_weapon_monster_sequence(self):
        """Test a complex sequence involving multiple weapons and monsters"""
        initial_health = self.player.health
        initial_score = self.player.score_so_far
        
        # Create a sequence of weapons and monsters
        weapon1 = Weapon("Diamonds", "5")
        monster1 = Monster("Spades", "4")
        weapon2 = Weapon("Diamonds", "7")
        monster2 = Monster("Spades", "6")
        monster3 = Monster("Spades", "3")
        
        actions = [
            Action(self.player.equip_weapon, weapon1, "Equip", rev=self.player.unequip_weapon),
            Action(self.player.fight_monster, monster1, "Fight", rev=self.player.undo_fight_monster),
            Action(self.player.equip_weapon, weapon2, "Equip", rev=self.player.unequip_weapon),
            Action(self.player.fight_monster, monster2, "Fight", rev=self.player.undo_fight_monster),
            Action(self.player.fight_monster, monster3, "Fight", rev=self.player.undo_fight_monster)
        ]
        
        # Execute all actions
        for action in actions:
            action.execute()
            
        # Verify intermediate state
        self.assertEqual(self.player.weapon, weapon2)
        self.assertEqual(self.player.score_so_far, initial_score + 4 + 6 + 3)
        self.assertTrue(monster2 in weapon2.monsters)
        self.assertTrue(monster3 in weapon2.monsters)
        
        # Reverse all actions
        for action in reversed(actions):
            action.reverse()
            
        # Verify complete restoration of initial state
        self.assert_game_state_equal(initial_health, None, initial_score, True)
        self.assertFalse(any(weapon1.monsters))
        self.assertFalse(any(weapon2.monsters))

    def test_potion_weapon_sequence(self):
        """Test a sequence mixing potions and weapons"""
        # Set initial health lower to test potion effects
        self.player.health = 10
        initial_health = self.player.health
        
        # Create test objects
        weapon = Weapon("Diamonds", "6")
        potion1 = Potion("Hearts", "3")
        potion2 = Potion("Hearts", "4")
        
        actions = [
            Action(self.player.use_potion, potion1, "Drink", rev=self.player.undo_use_potion),
            Action(self.player.equip_weapon, weapon, "Equip", rev=self.player.unequip_weapon),
            Action(self.player.use_potion, potion2, "Discard")  # This one can't be used (no reverse)
        ]
        
        # Execute all actions
        for action in actions:
            action.execute()
            
        # Verify intermediate state
        self.assertEqual(self.player.health, 13)  # Initial 10 + 3 from first potion
        self.assertEqual(self.player.weapon, weapon)
        self.assertFalse(self.player.can_use_potion)
        
        # Reverse reversible actions (last to first, skipping non-reversible)
        actions[1].reverse()  # Undo weapon equip
        actions[0].reverse()  # Undo first potion
        
        # Verify final state
        # After reversing the drink and weapon actions, can_use_potion should be restored to True
        # even though we discarded a potion, as the discard action has no reverse effect
        self.assert_game_state_equal(initial_health, None, 0, True)

    def test_player_death_and_reversal(self):
        """Test that dying from a monster fight is properly reversed"""
        # Set up player with low health
        self.player.health = 3
        initial_health = self.player.health
        initial_score = self.player.score_so_far
        initial_weapon = self.player.weapon
        
        # Create a monster that will kill the player
        monster = Monster("Spades", "5")  # Monster does 5 damage
        
        # Create and execute fight action
        action = Action(self.player.fight_monster, monster, "Fight", rev=self.player.undo_fight_monster)
        action.execute()
        
        # Player should now be dead
        self.assertFalse(self.player.alive)
        
        # Undo the action
        action.reverse()
        
        # Player should be alive again and state restored
        self.assertTrue(self.player.alive)
        self.assertEqual(self.player.health, initial_health)
        self.assertEqual(self.player.score_so_far, initial_score)
        self.assertEqual(self.player.weapon, initial_weapon)

if __name__ == '__main__':
    unittest.main()