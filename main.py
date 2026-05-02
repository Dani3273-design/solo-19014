import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.ui import UIManager, GameState
from game.control import GameController
from game.engine import GameEngine


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
FPS = 60


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("记忆翻牌游戏")
    
    clock = pygame.time.Clock()
    
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_controller = GameController(ui_manager)
    game_engine = GameEngine()
    
    ui_manager.init_menu()
    game_engine.start()
    
    running = True
    last_time = pygame.time.get_ticks()
    
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        
        ui_manager.current_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEMOTION:
                ui_manager.handle_mouse_motion(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    result = ui_manager.handle_mouse_click(event.pos)
                    
                    if ui_manager.game_state == GameState.PLAYING:
                        if hasattr(result, 'state'):
                            game_controller.handle_card_click(result)
        
        game_engine.update(dt=dt)
        
        ui_manager.draw(screen)
        
        game_engine.draw_particles(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    game_engine.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
