import os
from typing import List

from scripts.deck import Deck, Card, Monster, Weapon, Potion
from scripts.player import Player
from scripts.action import Action
from scripts.input_validation import validate_input


class Game():
    def __init__(self, player=None, simulation: bool = False, log_path: str = "game_log.txt"):
        self.deck = Deck()
        self.player = Player() if player is None else player
        self.room: List[Card] = []
        self.can_run_away = True
        self.action_log = []

        # --- New: Simulation mode and log file ---
        self.simulation = simulation
        self.log_path = log_path
        self._logfile = open(self.log_path, "w") if self.simulation else None

        self.reset()

    # --- Logging Helper ---
    def _log(self, msg: str = ""):
        """Internal print/log function respecting simulation mode."""
        if self.simulation:
            if self._logfile:
                self._logfile.write(str(msg) + "\n")
        else:
            print(msg)

    def close(self):
        """Close log file if open."""
        if self._logfile:
            self._logfile.close()
            self._logfile = None

    def __del__(self):
        self.close()

    def set_agent(self, agent):
        self.player.agent = agent
        self.player.human = False

    def reset(self):
        self.deck.new_deck()
        self.deck.shuffle()
        self.deal_new_room()
        self.player.reset()
        self.action_log.clear()
        self.can_run_away = True

    def deal_new_room(self):
        while len(self.room) < 4 and not self.deck.is_empty():
            self.room.append(self.deck.deal_card())

    def show_room(self):
        self._log("================")
        self._log("= Dungeon Room =")
        self._log("================")
        for card in self.room:
            self._log(card)

    def show_action_log(self):
        self._log("\n===== ACTION LOG =====")
        for action in self.action_log[-5:]:
            self._log(action)
        self._log("======================\n")

    def show_game(self):
        # Delegate to player’s show_stats (may also print)
        self._log(self.player.show_stats())
        self.show_action_log()
        self.show_room()

    def run_away(self):
        assert self.can_run_away
        self.deck.return_cards(self.room)
        self.room.clear()
        self.can_run_away = False

    def generate_options(self):
        options = []
        for card in self.room:
            if isinstance(card, Monster):
                options.append(Action(self.player.fight_monster, card, "Fight", rev=self.player.undo_fight_monster))
            if isinstance(card, Weapon):
                options.append(Action(self.player.equip_weapon, card, "Equip", rev=self.player.unequip_weapon))
            if isinstance(card, Potion):
                if not self.player.can_use_potion:
                    options.append(Action(self.player.use_potion, card, "Discard"))
                else:
                    options.append(Action(self.player.use_potion, card, "Drink", rev=self.player.undo_use_potion))
        return options

    def handle_room(self):
        if self.player.human:
            os.system("cls")

        self.can_run_away = True

        while len(self.room) > (0 if self.deck.is_empty() else 1) and self.player.alive:
            self.show_game()

            if self.final_card_is_potion():
                break

            self._log("\nYour options are:")
            options = self.generate_options()

            for i, opt in enumerate(options):
                self._log(f"{i+1}) {opt}")
            self._log()

            action = self.player.choose_action(options, self)
            self.room.remove(action.arg)
            self._log()
            if self.player.human:
                os.system("cls")
            self.action_log.append(action.execute())

        if self.player.alive:
            self.action_log.append("Room cleared! Dealing new room ...")
            self.show_game()
            if self.player.human:
                input()

        self.deal_new_room()
        self.player.reset_potion_use()

    def is_game_over(self):
        if not self.player.alive:
            return True
        if self.all_rooms_cleared():
            return True
        return False

    def all_rooms_cleared(self):
        if self.deck.is_empty():
            if len(self.room) == 0:
                return True
            elif len(self.room) == 1:
                if isinstance(self.room[0], Monster):
                    return False
            return True
        return False

    def final_card_is_potion(self):
        if self.deck.is_empty() and len(self.room) == 1:
            if isinstance(self.room[0], Potion):
                return self.room[0].n_rank
        return 0

    def run(self):
        while not self.is_game_over():
            if self.player.human:
                os.system("cls")

            self.show_game()

            if self.can_run_away and self.player.choose_run_away(self):
                self.run_away()
                self.action_log.append("Ran away! Entering next room ...")
                self.deal_new_room()
                self._log(self.player.show_stats())
            else:
                self.handle_room()

        if self.player.alive:
            score = self.player.health + self.final_card_is_potion()
            self._log(f"Congrats! You cleared the dungeon. Your final score is {score}")
        else:
            score = self.player.health
            remaining_cards = self.room + self.deck.cards
            for card in remaining_cards:
                if isinstance(card, Monster):
                    score -= card.n_rank
            self._log(f"You died. Your final score was {score}")

        self.close()
        return score, self.player.alive
