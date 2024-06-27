import pygame
import sys
import pygame_gui
from config import *
import pygame_gui.data
from pygame_gui.elements import UIButton, UILabel, UIPanel
from pygame_gui.core import ObjectID

gameover_image = pygame.image.load('data/gameover_bg.png')

def end_game_screen(manager, window, clock, set_gui_visibility, score):
    padding = 48
    set_gui_visibility(False)

    pause_surface = pygame.Surface((WIDTH, HEIGHT))
    pause_surface.blit(gameover_image, (0, 0))

    # Erstellt ein Panel, das das gesamte Fenster abdeckt
    endgame_panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, window.get_width(), window.get_height()),
        manager=manager
    )
    
    # Final score
    final_score_label = UILabel(
        relative_rect=pygame.Rect(((window.get_width() / 2) - (WIDTH / 2), window.get_height() - 290), (WIDTH, 150)),
        text=f"{score}",
        manager=manager,
        container=endgame_panel,
        object_id=ObjectID(class_id='@label', object_id='#final_score_label')
    )

    # Fügt den "Neues Spiel"-Button hinzu
    new_game_button = UIButton(
        relative_rect=pygame.Rect((window.get_width() / 2 - 200, window.get_height() - 100), (225, 60)),
        text="New Game",
        manager=manager,
        container=endgame_panel,
        object_id=ObjectID(class_id='', object_id='#play_button')
    )

    # Fügt den "Beenden"-Button hinzu
    quit_button = UIButton(
        relative_rect=pygame.Rect((window.get_width() / 2 + 50, window.get_height() - 98), (150, 56)),
        text="Quit",
        manager=manager,
        container=endgame_panel,
        object_id=ObjectID(class_id='', object_id='#quit_button')
    )

    # Aktiviert das Menü
    is_running = True
    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == new_game_button:
                    is_running = False
                    endgame_panel.kill()
                    return 'new_game'
                elif event.ui_element == quit_button:
                    pygame.quit()
                    sys.exit()

            manager.process_events(event)

        manager.update(time_delta)
        window.blit(pause_surface, (0, 0))
        manager.draw_ui(window)
        pygame.display.flip()
