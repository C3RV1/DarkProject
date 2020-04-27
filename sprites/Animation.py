import pygame
import os
import math


class Animation(object):
    def __init__(self, animation_folder, scale=1, loop=True, frames_per_second=1):
        if not os.path.isdir(animation_folder):
            raise Exception("Missing animation: {}".format(animation_folder))

        self.animation_folder = animation_folder
        self.frames = []

        frames_to_load = os.listdir(self.animation_folder)
        frames_to_load.sort()

        for frame in frames_to_load:
            image = pygame.image.load("{}/{}".format(self.animation_folder, frame)).convert_alpha()
            self.frames.append(pygame.Surface((image.get_width() * scale, image.get_height() * scale),
                                              pygame.HWSURFACE | pygame.SRCALPHA))
            pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale), self.frames[-1])

        self.current_frame = 0

        self.loop = loop
        self.finished = False

        self.seconds_between_frame = 1.0 / frames_per_second
        self.time_since_last = 0.0

    def next_frame(self, addition=1):
        if len(self.frames) < 1:
            return None
        ret_surface = self.frames[self.current_frame].copy()
        self.current_frame += int(addition)
        if self.loop:
            self.current_frame %= len(self.frames)
        else:
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
                self.finished = True
        return ret_surface

    def get_frame(self, delta_time):
        self.time_since_last += delta_time

        return_frame = self.next_frame(addition=math.floor(self.time_since_last / self.seconds_between_frame))

        while self.time_since_last > self.seconds_between_frame:
            self.time_since_last -= self.seconds_between_frame

        return return_frame

    @property
    def frames_per_second(self):
        return 1.0 / self.seconds_between_frame

    @frames_per_second.setter
    def frames_per_second(self, value):
        self.seconds_between_frame = 1.0 / value

    def reset(self):
        self.time_since_last = 0
        self.current_frame = 0
