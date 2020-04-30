import pygame
import time
from menus import MainMenu
from scenes import TestWorldGen
from scenes import TestAnimation
from scenes import TestLevel2
from scenes import MainGame
import random


class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720),
                                              flags=pygame.FULLSCREEN |
                                                    pygame.HWSURFACE |
                                                    pygame.DOUBLEBUF)  # type: pygame.Surface

        self.running = True

        self.delta_time = 1

        self.active_scene = None
        # self.load_scene(MainMenu.MainMenu, (self,))
        # self.load_scene(TestWorldGen.TestWorldGen, (self,))
        # self.load_scene(TestAnimation.TestAnimation, (self,))
        # self.load_scene(TestLevel2.TestLevel, (self, ))
        self.load_scene(MainGame.MainGame, (self,))

        self.fps_font = pygame.font.Font("game_data/fonts/calling_code.ttf", 14)

        self.pygame_clock = pygame.time.Clock()  # type: pygame
        self.pygame_clock.tick()
        pygame.joystick.init()
        self.joystick = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in self.joystick:
            joystick.init()

        random.seed(time.time())

        self.player_joy = -1

    def __del__(self):
        self.exit()

    def main_loop(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.exit()

            self.delta_time = float(self.pygame_clock.tick(60)) / (10 ** 3)

            fps_text = self.fps_font.render("FPS: {}".format(round(1 / self.delta_time)), False, (255, 255, 255))

            self.active_scene.main_loop(events)

            self.screen.blit(fps_text, (self.screen.get_width() - fps_text.get_width(), 0))

            pygame.display.flip()

    def load_scene(self, scene_object, scene_parameters):
        self.active_scene = scene_object(*scene_parameters)

    def exit(self):
        self.running = False
