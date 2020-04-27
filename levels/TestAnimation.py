import GameManager
import pygame
from sprites.Animation import Animation
import math


class TestAnimation:
    def __init__(self, game_manager):
        # type: (GameManager.GameManager) -> None
        self.game_manager = game_manager  # type: GameManager.GameManager

        self.animation = Animation("game_data/sprites/objects/pod/static", scale=8)
        frame_rate = 8
        self.seconds_between_frame = 1.0 / frame_rate

        self.time_since_last = 0

    def main_loop(self, events):
        self.game_manager.screen.fill((0, 0, 0))

        self.time_since_last += self.game_manager.delta_time
        tmp_time = self.time_since_last
        if self.time_since_last > self.seconds_between_frame:
            self.time_since_last = 0.0

        image_to_render = self.animation.next_frame(addition=math.floor(tmp_time / self.seconds_between_frame))
        self.game_manager.screen.blit(image_to_render, (100, 100))
