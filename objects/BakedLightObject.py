import pygame
from utils import math2d


class BackedLightObject:
    def __init__(self, light_image):
        self.light_image = light_image  # type: pygame.Surface
        math2d.invert_surface(self.light_image)
