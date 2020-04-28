import pygame
import random
import WorldGenerator
from tilemap import Tilemap
import random
from utils.Vector2D import Vector2D
from utils.Camera import Camera
import json
import math


class ConnectionGenerator:
    def __init__(self, x, y, world_generator):
        # type: (int, int, WorldGenerator.WorldGenerator) -> None
        self.is_connection = False
        self.connection_id = 0

        self.world = world_generator

        self.this_rand = random.Random()

        self.value = 0

        if x == 0 and y == -1:
            self.value = 26 / 2
            self.is_connection = True
            return
        if x == -1 and y == -1:
            self.is_connection = False
            return
        if x == 0 and y == 0:
            self.is_connection = False
            return
        if x == 0 and y == -2:
            self.is_connection = False
            return

        if self.world.world_bounds[0] <= x <= self.world.world_bounds[2]\
                and self.world.world_bounds[1] * 2 <= y <= self.world.world_bounds[3] * 2:
            self.connection_id = (x * (world_generator.world_bounds[3] + 1) + y) + self.world.seed
            self.this_rand.seed(self.connection_id)

            self.is_connection = self.this_rand.randint(0, 100) > 50

            if y % 2 == 0 and not self.is_connection:
                p1 = ConnectionGenerator.is_connection_at(x, y - 2, self.world.world_bounds, self.world.seed)
                p2 = ConnectionGenerator.is_connection_at(x, y - 1, self.world.world_bounds, self.world.seed)
                p3 = ConnectionGenerator.is_connection_at(x - 1, y - 1, self.world.world_bounds, self.world.seed)

                count = 0
                if p1:
                    count += 1
                if p2:
                    count += 1
                if p3:
                    count += 1

                if count < 2:
                    self.is_connection = True

            if self.is_connection:
                self.value = self.this_rand.randint(0, 64)

        self.position = Vector2D(self.value, self.value)

    def make_position(self):
        self.position = Vector2D(self.value, self.value)

    @staticmethod
    def is_connection_at(x, y, world_bounds, seed):
        this_rand = random.Random()
        connection_id = (x * (world_bounds[3] + 1) + y) + seed
        this_rand.seed(connection_id)
        return this_rand.randint(0, 100) > 50


class RoomGenerator:
    def __init__(self, position, world_generator):
        # type: (Vector2D, WorldGenerator.WorldGenerator) -> None
        self.world_generator = world_generator
        self.position = position.copy()
        self.seed = self.world_generator.seed

        self.this_rand = random.Random()
        self.this_rand.seed(self.position.x*self.position.y + self.position.y + self.seed)

        self.is_room = True
        self.is_wall = True

        # Room
        self.room_size = Vector2D(self.this_rand.randint(3, self.world_generator.max_room_size[0]), 0)
        self.room_size.y = self.this_rand.randint(max(int(self.room_size.x / 2), 3),
                                                  self.room_size.x + int(self.room_size.x / 2))

        self.room_real_size = self.room_size.copy()
        self.room_real_size.x += 6
        self.room_real_size.y += 8

        if self.room_real_size.x < 40:
            self.room_real_size.x = 40
        if self.room_real_size.y < 26:
            self.room_real_size.y = 26

        self.room_map = []
        for x in range(0, self.room_real_size.x):
            self.room_map.append([])
            for y in range(0, self.room_real_size.y):
                self.room_map[-1].append(0)

        # Connections
        self.connections = []
        self.connections.append(ConnectionGenerator(position.x, (position.y-1)*2, self.world_generator))    # Top
        self.connections.append(ConnectionGenerator(position.x, position.y*2, self.world_generator))        # Bottom
        self.connections.append(ConnectionGenerator(position.x-1, position.y*2 - 1, self.world_generator))  # Left
        self.connections.append(ConnectionGenerator(position.x, position.y*2 - 1, self.world_generator))    # Right

        self.connections[0].value %= self.room_size.x
        self.connections[0].make_position()
        self.connections[0].position.x += (self.room_real_size.x - self.room_size.x) / 2
        self.connections[0].position.y = 0

        self.connections[1].value %= self.room_size.x
        self.connections[1].make_position()
        self.connections[1].position.x += (self.room_real_size.x - self.room_size.x) / 2
        self.connections[1].position.y = self.room_real_size.y-1

        self.connections[2].value %= self.room_size.y
        self.connections[2].make_position()
        self.connections[2].position.y += (self.room_real_size.y - self.room_size.y) / 2
        self.connections[2].position.x = 0

        self.connections[3].value %= self.room_size.y
        self.connections[3].make_position()
        self.connections[3].position.y += (self.room_real_size.y - self.room_size.y) / 2
        self.connections[3].position.x = self.room_real_size.x-1

        self.objects = []

        self.generate()
        self.save()

    def generate(self):
        self.is_room = self.this_rand.randint(0, 100) < 98
        self.is_wall = self.this_rand.randint(0, 100) < 80

        if self.is_room:  # We have a room
            self.generate_floor()

        if self.is_wall and self.is_room:
            self.generate_walls()

        self.generate_connections()

    def generate_floor(self):
        for x in range((self.room_real_size.x - self.room_size.x) / 2,
                       (self.room_real_size.x + self.room_size.x) / 2):
            for y in range((self.room_real_size.y - self.room_size.y) / 2,
                           (self.room_real_size.y + self.room_size.y) / 2):
                self.room_map[x][y] = 1

    def generate_connections(self):
        if self.is_room:
            for connection in range(0, len(self.connections)):
                if not self.connections[connection].is_connection:
                    continue
                connection_position = self.connections[connection].position.copy()
                while self.room_map[connection_position.x][connection_position.y] != RoomTiles.FLOOR:
                    self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                    if connection == 0:
                        connection_position.y += 1
                    elif connection == 1:
                        connection_position.y -= 1
                    elif connection == 2:
                        connection_position.x += 1
                    else:
                        connection_position.x -= 1
                    if connection_position.x < 0 or connection_position.x >= self.room_real_size.x:
                        break
                    if connection_position.y < 0 or connection_position.y >= self.room_real_size.y:
                        break
        else:
            for connection in range(0, len(self.connections)):
                if not self.connections[connection].is_connection:
                    continue
                connection_position = self.connections[connection].position.copy()
                if connection < 2:
                    while connection_position.y != math.floor(self.room_real_size.y / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.y > math.floor(self.room_real_size.y / 2.0):
                            connection_position.y -= 1
                        else:
                            connection_position.y += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                    while connection_position.x != math.floor(self.room_real_size.x / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.x > math.floor(self.room_real_size.x / 2.0):
                            connection_position.x -= 1
                        else:
                            connection_position.x += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                else:
                    while connection_position.x != math.floor(self.room_real_size.x / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.x > math.floor(self.room_real_size.x / 2.0):
                            connection_position.x -= 1
                        else:
                            connection_position.x += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                    while connection_position.y != math.floor(self.room_real_size.y / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.y > math.floor(self.room_real_size.y / 2.0):
                            connection_position.y -= 1
                        else:
                            connection_position.y += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR

    def generate_walls(self):
        for x in [(self.room_real_size.x - self.room_size.x) / 2 - 1,
                  (self.room_real_size.x + self.room_size.x) / 2]:
            for y in range((self.room_real_size.y - self.room_size.y) / 2 - 1,
                           (self.room_real_size.y + self.room_size.y) / 2 + 1):
                self.room_map[x][y] = 2

        for x in range((self.room_real_size.x - self.room_size.x) / 2 - 1,
                       (self.room_real_size.x + self.room_size.x) / 2 + 1):
            for y in [(self.room_real_size.y - self.room_size.y) / 2 - 2,
                      (self.room_real_size.y - self.room_size.y) / 2 - 1,
                      (self.room_real_size.y + self.room_size.y) / 2,
                      (self.room_real_size.y + self.room_size.y) / 2 + 1]:
                self.room_map[x][y] = 2

    def save(self):
        room_path = self.world_generator.world_folder + "/rooms/room_{}_{}.json".format(int(self.position.x),
                                                                                        int(self.position.y))

        connections = []
        for connection in range(0, len(self.connections)):
            if not self.connections[connection].is_connection:
                connections.append([0, 0])
                continue
            connections.append(self.connections[connection].position.list())

        room_dict = {"map": self.room_map,
                     "objects": self.objects,
                     "connections": connections}

        room_file = open(room_path, "wb")
        room_file.write(json.dumps(room_dict))
        room_file.close()


class RoomTiles:
    VOID = 0
    FLOOR = 1
    WALL = 2


class RoomRenderer:
    def __init__(self, room_map, tileset, objects=[], camera=None, connections=[None, None, None, None]):
        self.tilemap = Tilemap.Tilemap(tileset, map_size=(len(room_map), len(room_map[0])))
        self.room_map = room_map
        self.size = [len(room_map), len(room_map[0])]
        self.objects = objects
        self.camera = camera
        self.connections = connections

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

        elif self.get(x, y - 1) == RoomTiles.WALL and self.get(x, y + 1) == RoomTiles.WALL and self.get(x, y + 2) == RoomTiles.WALL:
            tile = "wall_mid"

        elif self.get(x, y + 2) != RoomTiles.WALL and self.get(x, y - 1) == RoomTiles.WALL and\
                self.get(x - 1, y) != RoomTiles.WALL and self.get(x + 1, y) != RoomTiles.WALL:
            tile = "wall_down_end"

        elif self.get(x, y - 1) != RoomTiles.WALL and self.get(x, y + 1) == RoomTiles.WALL and\
                self.get(x - 1, y) != RoomTiles.WALL and self.get(x + 1, y) != RoomTiles.WALL:
            tile = "wall_up_end"

        elif self.get(x - 1, y) != RoomTiles.WALL and self.get(x + 1, y) == RoomTiles.WALL and\
                self.get(x, y + 2) != RoomTiles.WALL and self.get(x, y - 1) != RoomTiles.WALL:
            tile = "wall_left_end"

        elif self.get(x + 1, y) != RoomTiles.WALL and self.get(x - 1, y) == RoomTiles.WALL and\
                self.get(x, y + 2) != RoomTiles.WALL and self.get(x, y - 1) != RoomTiles.WALL:
            tile = "wall_right_end"

        elif self.get(x, y + 1) == RoomTiles.WALL and self.get(x + 1, y) == RoomTiles.WALL and\
                (self.get(x + 1, y + 1) == RoomTiles.WALL or self.get(x - 1, y + 1) == RoomTiles.WALL) and\
                not (self.get(x - 1, y) == RoomTiles.WALL or self.get(x, y - 1) == RoomTiles.WALL):
            tile = "wall_corner_1"

        elif self.get(x, y + 1) == RoomTiles.WALL and self.get(x - 1, y) == RoomTiles.WALL and\
                (self.get(x + 1, y + 1) == RoomTiles.WALL or self.get(x - 1, y + 1) == RoomTiles.WALL) and\
                not (self.get(x + 1, y) == RoomTiles.WALL or self.get(x, y - 1) == RoomTiles.WALL):
            tile = "wall_corner_2"

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
