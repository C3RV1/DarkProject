import pygame
import GameManager
from utils import Button, TextBox
from levels import TestLevel2


class MainMenu:
    def __init__(self, game_manager):
        # type: (GameManager.GameManager) -> None
        self.game_manager = game_manager  # type: GameManager.GameManager

        self.focus = 0

        self.font = pygame.font.Font("game_data/fonts/press_start_2p.ttf", 20)

    def main_loop(self, events):
        self.game_manager.load_scene(TestLevel2.TestLevel, (self.game_manager, ))
