import pygame
from utils.Vector2D import Vector2D
from utils import math2d


class RealtimeLightObject:
    def __init__(self, light_image, offset):
        self.light_image = light_image  # type: pygame.Surface
        math2d.invert_surface(self.light_image)
        self.light_offset = offset  # type: Vector2D
