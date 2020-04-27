from generators.Object import Object
from generators.InteractiveObject import InteractiveObject
from utils.Vector2D import Vector2D
import pygame


class PodObject(InteractiveObject, Object):
    def __init__(self, obj_data, cam):
        Object.__init__(self, obj_id=0, camera=cam)
        InteractiveObject.__init__(self)
        self.position = Vector2D(0, 0, lst=obj_data["pos"])

        self.animation_base_folder = "game_data/sprites/objects/pod"
        self.animations_to_load = [{"name": "static",
                                    "scale": 4,
                                    "loop": True,
                                    "fps": 8}]

        self.load_animations()
        self.set_animation("static")

        self.font = pygame.font.Font("game_data/fonts/press_start_2p.ttf", 20)
        self.font2 = pygame.font.Font("game_data/fonts/press_start_2p.ttf", 12)
        self.explanation_text = self.font.render("Capsule from where you emerged", False, (255, 255, 255))

        self.exit_text = self.font2.render("Press ESC to exit", False, (255, 255, 255))

        self.background_size = 10

        self.gradient = pygame.Surface((self.explanation_text.get_width() + self.background_size * 2,
                                        self.explanation_text.get_height() + self.exit_text.get_height() + 10
                                        + self.background_size * 2))
        self.gradient.set_alpha(220)
        self.gradient.fill((0, 0, 0))

    def custom_interacting_draw(self, surface):
        # type: (pygame.Surface) -> None
        surface.blit(self.gradient, (1100 - self.explanation_text.get_width() - self.background_size,
                                     200 - self.background_size))
        surface.blit(self.explanation_text, (1100 - self.explanation_text.get_width(),
                                             200))
        surface.blit(self.exit_text, (1100 - self.explanation_text.get_width(),
                                      200 + self.explanation_text.get_height() + 10))

    def interacting_behaviour(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.interacting = False
