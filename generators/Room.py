import pygame
import random
import WorldGenerator
from tilemap import Tilemap
import random
from utils.Vector2D import Vector2D
from utils.Camera import Camera


class ConnectionGenerator:
    def __init__(self, x, y, world_generator):
        # type: (int, int, WorldGenerator.WorldGenerator) -> None
        self.is_connection = False
        self.connection_id = 0

        self.world = world_generator

        if self.world.world_bounds[0] <= x <= self.world.world_bounds[2]\
                and self.world.world_bounds[1] <= y <= self.world.world_bounds[3]:
            self.connection_id = (x * (world_generator.world_bounds[3] + 1) + y) + self.world.seed
            random.seed(self.connection_id)

            self.is_connection = random.randint(0, 100) > 50
            if self.is_connection:
                pass
        pass


class RoomGenerator:
    def __init__(self, x, y, seed, room_bound):
        pass


class RoomTiles:
    VOID = 0
    FLOOR = 1
    WALL = 2


class RoomRenderer:
    def __init__(self, room_map, tileset, objects=[], camera=None):
        self.tilemap = Tilemap.Tilemap(tileset, map_size=(len(room_map), len(room_map[0])))
        self.room_map = room_map
        self.size = [len(room_map), len(room_map[0])]
        self.objects = objects
        self.camera = camera

    def render(self):
        self.render_tiles()
        # self.tilemap.make_scaled()
        self.tilemap.scale()

    def render_tiles(self):
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                self.render_tile(x, y)

    def render_tile(self, x, y):
        if self.room_map[x][y] == RoomTiles.VOID:
            self.render_void(x, y)
        elif self.room_map[x][y] == RoomTiles.FLOOR:
            self.render_floor(x, y)
        elif self.room_map[x][y] == RoomTiles.WALL:
            self.render_wall(x, y)

    def render_void(self, x, y):
        tile = "void"

        if self.get(x, y - 1) != RoomTiles.VOID:
            tile = "void_floor_top"

        elif self.get(x - 1, y - 1) != RoomTiles.VOID:
            tile = "void_floor_diag_left"

        elif self.get(x + 1, y - 1) != RoomTiles.VOID:
            tile = "void_floor_diag_right"

        self.tilemap.change_block_at(x, y, tile, make_scaled=False)

    def render_floor(self, x, y):
        tile = "floor"

        if self.get(x - 1, y) == RoomTiles.WALL and self.get(x, y - 1) == RoomTiles.WALL:
            tile = "floor_shadow_up_left"

        elif self.get(x - 1, y) == RoomTiles.WALL:
            tile = "floor_shadow_left"

        elif self.get(x, y - 1) == RoomTiles.WALL:
            tile = "floor_shadow_up"

        elif self.get(x - 1, y - 1) == RoomTiles.WALL:
            tile = "floor_shadow_up_left_small"

        self.tilemap.change_block_at(x, y, tile, make_scaled=False)

    def render_wall(self, x, y):
        tile = "wall_top"

        if self.get(x, y + 1) != RoomTiles.WALL and self.get(x - 1, y + 1) == RoomTiles.WALL:
            tile = "wall_front_shadow"

        elif self.get(x, y + 1) != RoomTiles.WALL:
            tile = "wall_front"

        elif self.get(x, y + 1) == RoomTiles.WALL and self.get(x + 1, y) == RoomTiles.WALL and\
                (self.get(x + 1, y + 1) == RoomTiles.WALL or self.get(x - 1, y + 1) == RoomTiles.WALL) and\
                not (self.get(x - 1, y) == RoomTiles.WALL or self.get(x, y - 1) == RoomTiles.WALL):
            tile = "wall_corner_1"

        elif self.get(x, y + 1) == RoomTiles.WALL and self.get(x - 1, y) == RoomTiles.WALL and\
                (self.get(x + 1, y + 1) == RoomTiles.WALL or self.get(x - 1, y + 1) == RoomTiles.WALL) and\
                not (self.get(x + 1, y) == RoomTiles.WALL or self.get(x, y - 1) == RoomTiles.WALL):
            tile = "wall_corner_2"

        elif self.get(x, y - 1) == RoomTiles.WALL and self.get(x, y + 1) == RoomTiles.WALL and self.get(x, y + 2) == RoomTiles.WALL:
            tile = "wall_mid"

        elif self.get(x, y + 2) != RoomTiles.WALL and self.get(x, y - 1) == RoomTiles.WALL and\
                self.get(x - 1, y) != RoomTiles.WALL and self.get(x + 1, y) != RoomTiles.WALL:
            tile = "wall_down_end"

        elif self.get(x, y - 1) != RoomTiles.WALL and self.get(x, y + 1) == RoomTiles.WALL and\
                self.get(x - 1, y) != RoomTiles.WALL and self.get(x + 1, y) != RoomTiles.WALL:
            tile = "wall_up_end"

        self.tilemap.change_block_at(x, y, tile, make_scaled=False)

    def get(self, x, y):
        if not 0 <= x < self.size[0]:
            return RoomTiles.VOID
        if not 0 <= y < self.size[1]:
            return RoomTiles.VOID
        return self.room_map[x][y]

    def draw(self, surface, delta_time):
        # type: (pygame.Surface, float) -> None
        surface.blit(self.tilemap.r_image_scaled, (max(0, -self.camera.real_position.x),
                                                   max(0, -self.camera.real_position.y)),
                     area=(max(0, self.camera.real_position.x),
                           max(0, self.camera.real_position.y),
                           min(self.tilemap.r_image_scaled.get_width(),
                               self.camera.real_position.x + surface.get_width()),
                           min(self.tilemap.r_image_scaled.get_height(),
                               self.camera.real_position.y + surface.get_height())))
        for obj in self.objects:
            obj.position_to_real()
            surface.blit(obj.get_render(delta_time), obj.real_position.list())
