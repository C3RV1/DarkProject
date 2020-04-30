import pygame
from utils.Vector2D import Vector2D


class RealtimeLightObject:
    def __init__(self, light_image, offset):
        self.light_image = light_image  # type: pygame.Surface
        self.offset = offset  # type: Vector2D
