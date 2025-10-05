import os

from typing import List

from scripts.deck import Deck, Card, Monster, Weapon, Potion
from scripts.player import Player
from scripts.action import Action
from scripts.input_validation import validate_input

class Game():
    def __init__(self, player=None):
        self.deck = Deck()
        self.player = Player() if player == None else player

        self.room: List[Card] = []

        # game variables
        self.can_run_away = True
        self.action_log = []

        self.reset()

    def set_agent(self, agent):
        self.player.agent = agent
        self.player.human = False

    def reset(self):
        self.deck.new_deck()
        self.deck.shuffle()
        self.deal_new_room()
        self.player.reset()


        self.can_run_away = True

    def deal_new_room(self):
        while len(self.room) < 4 and not self.deck.is_empty():
            self.room.append(self.deck.deal_card()) 

    def show_room(self):
        # print("================")
        # print("= Dungeon Room =")
        # print("================")
        
        for card in self.room:
            pass
            # print(card)

    def show_action_log(self):
        # print("\n===== ACTION LOG =====")
        # for action in self.action_log[-5:]:
            # pass
            # print(action)
        # print("======================\n")
        pass

    def show_game(self):
        self.player.show_stats()
        self.show_action_log()
        self.show_room()

    def run_away(self):
        assert self.can_run_away
        self.deck.return_cards(self.room)
        self.room.clear()

        self.can_run_away = False

    def handle_room(self):
        #os.system("cls")

        self.can_run_away = True
        # now, the player engages with the room
        # play continues until the player dies or there is only one card present

        while len(self.room) > (0 if self.deck.is_empty() else 1) and self.player.alive:

            self.show_game()

            if self.final_card_is_potion():
                break

            # print("\nYour options are:")
            options = []

            for card in self.room:
                if isinstance(card, Monster):
                    options.append(Action(self.player.fight_monster, card, "Fight"))

                if isinstance(card, Weapon):
                    options.append(Action(self.player.equip_weapon, card, "Equip"))

                if isinstance(card, Potion):
                    if not self.player.can_use_potion:
                        options.append(Action(self.player.use_potion, card, "Discard"))
                    else:
                        options.append(Action(self.player.use_potion, card, "Drink"))

            
            #for i, opt in enumerate(options):
                # print(f"{i+1}) {opt}")
            # print()

            action = self.player.choose_action(options, self)
            
            self.room.remove(action.arg)
            # print()
            #os.system("cls")

            self.action_log.append(action.execute())

    
        if self.player.alive:
            self.action_log.append("Room cleared! Dealing new room ...")
            self.show_game()

            if self.player.human:
                input()

        self.deal_new_room()
        self.player.reset_potion_use()

    def is_game_over(self):
        if not self.player.alive: return True # if the player died, the game's over
        if self.all_rooms_cleared(): return True # if all rooms are cleared
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
            #os.system("cls")
            
            self.show_game()

            if self.can_run_away and self.player.choose_run_away(self):
                self.run_away()
                self.action_log.append("Ran away! Entering next room ...")
                self.deal_new_room()
                self.player.show_stats()
  
            else:
                self.handle_room()

        if self.player.alive:
            score = self.player.health + self.final_card_is_potion()
            # print(f"Congrats! You cleared the dungeon. Your final score is {score}")
        else:
            score = self.player.health
            remaining_cards = self.room + self.deck.cards
            for card in remaining_cards:
                if isinstance(card, Monster):
                    score -= card.n_rank

            # print(f"You died. Your final score was {score}")

        return score