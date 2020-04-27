from generators import WorldGenerator
from utils.Vector2D import Vector2D
import pygame
import GameManager
from generators.Room import RoomRenderer
from object_logic import Player
from utils import Camera


class TestWorldGen:
    def __init__(self, game_manager):
        # type: (GameManager.GameManager) -> None
        self.game_manager = game_manager  # type: GameManager.GameManager

        # self.rendered_image = self.world_gen.get_current_room()  # type: pygame.Surface
        # self.current_room_rendered = self.world_gen.get_current_room()  # type: RoomRenderer

        self.cam = Camera.Camera(self.game_manager)

        self.world_gen = WorldGenerator.WorldGenerator(self.game_manager, "game_data/config/world.json",
                                                       "game_data/worlds/test_world", camera=self.cam)

        self.player = Player.PlayerObject(self.game_manager, self.world_gen, position=Vector2D(1280 / 2,
                                                                                               720 / 2),
                                          camera=self.cam, obj_data=self.world_gen.load_player())

        self.cam.position = self.player.position.copy()

        self.cam.target(self.player.position)

    def main_loop(self, events):
        self.update_behaviours(events)
        self.draw()

    def update_behaviours(self, events):
        self.player.update(events)
        for obj in self.player.current_room.objects:
            obj.update(events)
        self.cam.update(self.game_manager.delta_time)

    def draw(self):
        self.player.current_room.draw(self.game_manager.screen, self.game_manager.delta_time)

        """pygame.draw.circle(self.game_manager.screen, (255, 255, 255), self.cam.position.list(),
                           5)"""

        self.player.extra_draw()
