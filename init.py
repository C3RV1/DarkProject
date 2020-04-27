import pygame
import GameManager
from generators import WorldGenerator


def main():
    pygame.init()
    game_manager = GameManager.GameManager()
    game_manager.main_loop()
    pygame.quit()


if __name__ == "__main__":
    # WorldGenerator.WorldGenerator.new_world(None)
    main()
