import pygame
import sys
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIPanel
from pygame_gui.core import ObjectID

def end_game_screen(manager, window, clock, set_gui_visibility, high_score):
    padding = 48
    set_gui_visibility(False)

    # Erstellt ein Panel, das das gesamte Fenster abdeckt
    endgame_panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, window.get_width(), window.get_height()),
        manager=manager
    )

    # Header
    endgame_title = UILabel(
        relative_rect=pygame.Rect((padding, padding), (window.get_width() - padding * 2, 300)),
        text=f"Game Over",
        manager=manager,
        container=endgame_panel,
        object_id=ObjectID(class_id='@label', object_id='#endgame_title')
    )
    
    # Final score
    final_score_label = UILabel(
        relative_rect=pygame.Rect((window.get_width() / 2 - 200, window.get_height() - 400), (400, 150)),
        text=f"Final Score: {high_score}",
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
        window.fill((5, 5, 5))  
        manager.draw_ui(window)
        pygame.display.flip()
