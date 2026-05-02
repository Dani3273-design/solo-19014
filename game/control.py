import threading
import time
import pygame
from .ui import GameState, CardState


class AnimationThread(threading.Thread):
    def __init__(self, target_func, *args, **kwargs):
        super().__init__(daemon=True)
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        self.target_func(*self.args, **self.kwargs)


class GameController:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.selected_cards = []
        self.is_locked = False
        self.lock_event = threading.Event()
        self.lock_event.set()
        self.current_time = 0
    
    def update_time(self):
        self.current_time = pygame.time.get_ticks()
    
    def handle_card_click(self, card):
        self.update_time()
        
        if self.is_locked:
            return False
        
        if len(self.selected_cards) >= 2:
            return False
        
        if card in self.selected_cards:
            return False
        
        if card.start_flip_to_front(self.current_time):
            self.selected_cards.append(card)
            
            if len(self.selected_cards) == 2:
                self._check_match_async()
        
        return True
    
    def _check_match_async(self):
        self.ui_manager.moves += 1
        thread = AnimationThread(self._wait_and_check_match)
        thread.start()
    
    def _wait_and_check_match(self):
        self.is_locked = True
        self.lock_event.clear()
        
        card1, card2 = self.selected_cards
        
        time.sleep(0.5)
        
        self.update_time()
        
        if card1.pattern_index == card2.pattern_index:
            card1.set_matched()
            card2.set_matched()
            card1.match_animation_start = self.current_time
            card2.match_animation_start = self.current_time
            
            self.selected_cards = []
            
            time.sleep(0.3)
            self.update_time()
            
            if self.ui_manager.is_game_complete():
                self.ui_manager.init_game_over()
        else:
            time.sleep(0.5)
            self.update_time()
            
            card1.start_flip_to_back(self.current_time)
            card2.start_flip_to_back(self.current_time)
            
            time.sleep(0.5)
            self.selected_cards = []
        
        self.is_locked = False
        self.lock_event.set()
    
    def wait_for_unlock(self, timeout=0.1):
        self.lock_event.wait(timeout=timeout)
    
    def reset(self):
        self.selected_cards = []
        self.is_locked = False
        self.lock_event.set()
