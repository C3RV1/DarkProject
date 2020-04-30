import pygame
import random
import WorldGenerator
from tilemap import Tilemap
import random
from utils.Vector2D import Vector2D
from utils.Camera import Camera
import json
import math
import time

from objects.BakedLightObject import BackedLightObject
from objects.Object import Object
from objects.RealtimeLightObject import RealtimeLightObject
from utils import Shadow


# INNER ROOM CONNECTIONS
# When we are generating inner walls this class will save all the connections to the rooms next to this one.
class InnerRoomConnections:
    def __init__(self):
        self.has_entrance = False
        self.connections = []

    def add_connection(self, other_connection, door_position, vertical=True):
        self.connections.append({"obj": other_connection,
                                 "position": door_position,
                                 "vertical": vertical})

    def get_connection(self):
        return self.connections


# CONNECTION GENERATOR
# This class will be used to set the position of the connections between screens.
class ConnectionGenerator:
    def __init__(self, x, y, world_generator):
        # type: (int, int, WorldGenerator.WorldGenerator) -> None

        self.is_connection = False  # Is there a connection?

        # Used to generate random numbers (that way it does not depend on the screen)
        self.connection_id = 0

        # World generator used to get the seed
        self.world = world_generator

        # Random for this class
        self.this_rand = random.Random()

        # Random (pos x or pos y, depending if it's vertical or horizontal) of the connection
        self.value = 0

        # Special values for spawn room (0, 0)
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

        # Check that the connection is in the bounds
        if self.world.world_bounds[0] <= x <= self.world.world_bounds[2]\
                and self.world.world_bounds[1] * 2 <= y <= self.world.world_bounds[3] * 2:

            # Calculate connection id
            self.connection_id = (x * (world_generator.world_bounds[3] + 1) + y) + self.world.seed
            self.this_rand.seed(self.connection_id)

            self.is_connection = self.this_rand.randint(0, 100) > 50

            # If it's vertical we check that the screen has at least two entrances or exits.
            # In case it doesn't, we put a connection. It's very likely that by doing this the room now
            # has two entrances and the worst case it's a dead end, but the probability of a dead end
            # gets reduced a lot.
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

            # If there is a connection, we have a random value between 0 and the maximum size of a room.
            if self.is_connection:
                self.value = self.this_rand.randint(0, self.world.max_room_size[0])

        # We make the position equal to x = value and y = value
        # In RoomGenerator we "stick" it to a side.
        self.position = Vector2D(self.value, self.value)

    def make_position(self):
        self.position = Vector2D(self.value, self.value)

    # Gets if there's a connection at a point without checking anything else.
    @staticmethod
    def is_connection_at(x, y, world_bounds, seed):
        this_rand = random.Random()
        connection_id = (x * (world_bounds[3] + 1) + y) + seed
        this_rand.seed(connection_id)
        return this_rand.randint(0, 100) > 50


# ROOM GENERATOR
# Main class where screens (called rooms here) are generated
class ScreenGenerator:
    def __init__(self, position, world_generator):
        # type: (Vector2D, WorldGenerator.WorldGenerator) -> None

        # World generator (seed)
        self.world_generator = world_generator

        # Screen position
        self.position = position.copy()

        # Seed
        self.seed = self.world_generator.seed

        # Random number generator
        self.this_rand = random.Random()
        self.this_rand.seed(self.position.x*self.position.y + self.position.y + self.seed)

        # Is there a screen?
        self.is_screen = True

        # Screen Size
        self.screen_size = Vector2D(self.this_rand.randint(3, self.world_generator.max_room_size[0]), 0)
        self.screen_size.y = self.this_rand.randint(max(int(self.screen_size.x / 2), 3),
                                                    self.screen_size.x + int(self.screen_size.x / 2))

        # Screen size with borders
        self.screen_real_size = self.screen_size.copy()

        # We add the borders
        self.screen_real_size.x += 6
        self.screen_real_size.y += 8

        # We make the screen at least as large as the render screen
        if self.screen_real_size.x < 40:
            self.screen_real_size.x = 40
        if self.screen_real_size.y < 26:
            self.screen_real_size.y = 26

        # We create the map
        self.room_map = []
        for x in range(0, self.screen_real_size.x):
            self.room_map.append([])
            for y in range(0, self.screen_real_size.y):
                self.room_map[-1].append(0)

        # Connections
        self.connections = []
        self.connections.append(ConnectionGenerator(position.x, (position.y-1)*2, self.world_generator))    # Top
        self.connections.append(ConnectionGenerator(position.x, position.y*2, self.world_generator))        # Bottom
        self.connections.append(ConnectionGenerator(position.x-1, position.y*2 - 1, self.world_generator))  # Left
        self.connections.append(ConnectionGenerator(position.x, position.y*2 - 1, self.world_generator))    # Right

        self.connections[0].value %= self.screen_size.x
        self.connections[0].make_position()
        self.connections[0].position.x += (self.screen_real_size.x - self.screen_size.x) / 2
        self.connections[0].position.y = 0

        self.connections[1].value %= self.screen_size.x
        self.connections[1].make_position()
        self.connections[1].position.x += (self.screen_real_size.x - self.screen_size.x) / 2
        self.connections[1].position.y = self.screen_real_size.y - 1

        self.connections[2].value %= self.screen_size.y
        self.connections[2].make_position()
        self.connections[2].position.y += (self.screen_real_size.y - self.screen_size.y) / 2
        self.connections[2].position.x = 0

        self.connections[3].value %= self.screen_size.y
        self.connections[3].make_position()
        self.connections[3].position.y += (self.screen_real_size.y - self.screen_size.y) / 2
        self.connections[3].position.x = self.screen_real_size.x - 1

        # Objects (items...)
        self.objects = []

        # Generate and save the room
        self.generate()
        self.save()

    def generate(self):
        # Is there a room? 98 % probability that there is
        self.is_screen = self.this_rand.randint(0, 100) < 98

        if self.is_screen:  # We have a screen
            self.generate_floor()
            self.generate_walls()
            self.generate_inner_rooms()

        self.generate_connections()

    def generate_floor(self):
        # Fill the floor
        for x in range((self.screen_real_size.x - self.screen_size.x) / 2,
                       (self.screen_real_size.x + self.screen_size.x) / 2):
            for y in range((self.screen_real_size.y - self.screen_size.y) / 2,
                           (self.screen_real_size.y + self.screen_size.y) / 2):
                self.room_map[x][y] = 1

    def generate_connections(self):
        if self.is_screen:
            # We make the connections only as long as they need to be to get to the room.
            for connection in range(0, len(self.connections)):
                if not self.connections[connection].is_connection:
                    continue
                connection_position = self.connections[connection].position.copy()

                if connection == 0:
                    while connection_position.y < (self.screen_real_size.y - self.screen_size.y) / 2 + 2:
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        connection_position.y += 1
                elif connection == 1:
                    while connection_position.y > (self.screen_real_size.y + self.screen_size.y) / 2 - 2:
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        connection_position.y -= 1
                elif connection == 2:
                    while connection_position.x < (self.screen_real_size.x - self.screen_size.x) / 2 + 2:
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        connection_position.x += 1
                elif connection == 3:
                    while connection_position.x > (self.screen_real_size.x + self.screen_size.x) / 2 - 2:
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        connection_position.x -= 1
        else:
            # We make the connections get to the center of the screen.
            for connection in range(0, len(self.connections)):
                if not self.connections[connection].is_connection:
                    continue
                connection_position = self.connections[connection].position.copy()
                if connection < 2:
                    while connection_position.y != math.floor(self.screen_real_size.y / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.y > math.floor(self.screen_real_size.y / 2.0):
                            connection_position.y -= 1
                        else:
                            connection_position.y += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                    while connection_position.x != math.floor(self.screen_real_size.x / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.x > math.floor(self.screen_real_size.x / 2.0):
                            connection_position.x -= 1
                        else:
                            connection_position.x += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                else:
                    while connection_position.x != math.floor(self.screen_real_size.x / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.x > math.floor(self.screen_real_size.x / 2.0):
                            connection_position.x -= 1
                        else:
                            connection_position.x += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                    while connection_position.y != math.floor(self.screen_real_size.y / 2.0):
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR
                        if connection_position.y > math.floor(self.screen_real_size.y / 2.0):
                            connection_position.y -= 1
                        else:
                            connection_position.y += 1
                        self.room_map[connection_position.x][connection_position.y] = RoomTiles.FLOOR

    def generate_walls(self):
        # We fill in the walls
        for x in [(self.screen_real_size.x - self.screen_size.x) / 2 - 1,
                  (self.screen_real_size.x + self.screen_size.x) / 2]:
            for y in range((self.screen_real_size.y - self.screen_size.y) / 2 - 1,
                           (self.screen_real_size.y + self.screen_size.y) / 2 + 1):
                self.room_map[x][y] = 2

        for x in range((self.screen_real_size.x - self.screen_size.x) / 2 - 1,
                       (self.screen_real_size.x + self.screen_size.x) / 2 + 1):
            for y in [(self.screen_real_size.y - self.screen_size.y) / 2 - 2,
                      (self.screen_real_size.y - self.screen_size.y) / 2 - 1,
                      (self.screen_real_size.y + self.screen_size.y) / 2,
                      (self.screen_real_size.y + self.screen_size.y) / 2 + 1]:
                self.room_map[x][y] = 2

    def generate_inner_rooms(self):
        # We generate the inner rooms by dividing the rooms vertically and horizontally
        rectangles = [[(self.screen_real_size.x - self.screen_size.x) / 2,
                       (self.screen_real_size.y - self.screen_size.y) / 2,
                       self.screen_size.x,
                       self.screen_size.y]]

        iterations = self.this_rand.randint(2, 4)

        # Do iterations dividing vertically and horizontally
        for i in range(0, iterations):
            rectangles = self.inner_room_vertical_division(rectangles)
            rectangles = self.inner_room_horizontal_division(rectangles)

        # Create the doors between rooms
        self.inner_rooms_doors(rectangles)

    def inner_room_vertical_division(self, rectangles):
        # New_ractangles are the rooms after dividing them
        new_rectangles = []

        # For every room
        for rectangle in rectangles:
            # Random to not make values so sequential
            self.this_rand.random()

            # Do we divide?
            is_division = self.this_rand.randint(0, 100) > 30

            # Minimum size to divide (at this size it would be divided into 2 equal sized rectangles)
            if rectangle[2] < 9:
                is_division = False

            if is_division:  # If we have a division
                # Width of the first room we are creating
                division_width = self.this_rand.randint(4, rectangle[2] - 4 - 1)

                # Position where we have to put the wall
                division_position = division_width + rectangle[0]

                # New 2 rooms
                new_rectangles.append([rectangle[0], rectangle[1],
                                       division_width, rectangle[3]])
                new_rectangles.append([rectangle[0] + division_width, rectangle[1],
                                       rectangle[2] - division_width, rectangle[3]])

                # The wall dividing both rooms
                for y in range(0, rectangle[3]):
                    self.room_map[division_position][y + rectangle[1]] = RoomTiles.WALL
            else:
                # If we don't have a division we leave the room as it is.
                new_rectangles.append(rectangle)
        return new_rectangles

    def inner_room_horizontal_division(self, rectangles):
        # See vertical
        new_rectangles = []
        for rectangle in rectangles:
            self.this_rand.random()
            is_division = self.this_rand.randint(0, 100) > 30
            if rectangle[3] < 9:
                is_division = False

            if is_division:
                division_width = self.this_rand.randint(4, rectangle[3] - 4 - 1)
                division_position = division_width + rectangle[1]
                new_rectangles.append([rectangle[0], rectangle[1],
                                       rectangle[2], division_width])
                new_rectangles.append([rectangle[0], rectangle[1] + division_width,
                                       rectangle[2], rectangle[3] - division_width])

                # Vertical has double wall
                for x in range(0, rectangle[2]):
                    self.room_map[x + rectangle[0]][division_position] = RoomTiles.WALL
                for x in range(0, rectangle[2]):
                    self.room_map[x + rectangle[0]][division_position + 1] = RoomTiles.WALL
            else:
                new_rectangles.append(rectangle)
        return new_rectangles

    def inner_rooms_doors(self, rectangles):
        # Every one represents a room and it's connection with its sorroundings
        inner_room_connections = [InnerRoomConnections() for rectangle in rectangles]

        for rectangle in rectangles:
            for rectangle2 in rectangles:
                if rectangle == rectangle2:
                    continue

                # We add a connection to both involved rooms because a door is two directional

                # Top door
                if rectangle[1] == rectangle2[1] + rectangle2[3]:
                    if rectangle[0] >= rectangle2[0] and rectangle[0] + rectangle[2] <= rectangle2[0] + rectangle2[2]:
                        position = Vector2D((rectangle[0] * 2 + rectangle[2]) / 2, rectangle[1])
                        inner_room_connections[rectangles.index(rectangle)].add_connection(
                            inner_room_connections[rectangles.index(rectangle2)],
                            position, vertical=True)
                        inner_room_connections[rectangles.index(rectangle2)].add_connection(
                            inner_room_connections[rectangles.index(rectangle)],
                            position, vertical=True)

                # Bottom door
                if rectangle2[1] == rectangle[1] + rectangle[3]:
                    if rectangle[0] >= rectangle2[0] and rectangle[0] + rectangle[2] <= rectangle2[0] + rectangle2[2]:
                        position = Vector2D((rectangle[0] * 2 + rectangle[2]) / 2, rectangle2[1])
                        inner_room_connections[rectangles.index(rectangle)].add_connection(
                            inner_room_connections[rectangles.index(rectangle2)],
                            position, vertical=True)
                        inner_room_connections[rectangles.index(rectangle2)].add_connection(
                            inner_room_connections[rectangles.index(rectangle)],
                            position, vertical=True)

                # Left door
                if rectangle[0] == rectangle2[0] + rectangle2[2]:
                    if rectangle[1] >= rectangle2[1] and rectangle[1] + rectangle[3] <= rectangle2[1] + rectangle2[3]:
                        position = Vector2D(rectangle[0], (rectangle[1] * 2 + rectangle[3]) / 2)
                        inner_room_connections[rectangles.index(rectangle)].add_connection(
                            inner_room_connections[rectangles.index(rectangle2)],
                            position, vertical=False)
                        inner_room_connections[rectangles.index(rectangle2)].add_connection(
                            inner_room_connections[rectangles.index(rectangle)],
                            position, vertical=False)

                # Right door
                if rectangle2[0] == rectangle[0] + rectangle[2]:
                    if rectangle[1] >= rectangle2[1] and rectangle[1] + rectangle[3] <= rectangle2[1] + rectangle2[3]:
                        position = Vector2D(rectangle2[0], (rectangle[1] * 2 + rectangle[3]) / 2)
                        inner_room_connections[rectangles.index(rectangle)].add_connection(
                            inner_room_connections[rectangles.index(rectangle2)],
                            position, vertical=True)
                        inner_room_connections[rectangles.index(rectangle2)].add_connection(
                            inner_room_connections[rectangles.index(rectangle)],
                            position, vertical=True)

        # Connections to process
        # Once we walk a room, its connections get added to this list to get processed.
        connections_to_process = []

        # Start with the connections from room 0
        for connection in inner_room_connections[0].get_connection():
            connections_to_process.append(connection)
        inner_room_connections[0].has_entrance = True

        # While there are still connections to process. This way we make sure we walk all connections.
        while len(connections_to_process) > 0:
            connection = connections_to_process.pop()

            if connection["obj"].has_entrance:
                # This connection was in the list but its destination has already an entrance
                continue

            connection["obj"].has_entrance = True

            # We make the door
            position = connection["position"]
            self.room_map[position.x][position.y] = RoomTiles.FLOOR
            if connection["vertical"]:
                # If the door is vertical we have to clear another position under it because we have a double wall.
                self.room_map[position.x][position.y + 1] = RoomTiles.FLOOR

            # We get the connections of the next room we "walk" into.
            connections_to_add = connection["obj"].get_connection()

            # We go over all new connections and if their destination has already an entrance we skip that connection.
            for connection_to_add in connections_to_add:
                if connection_to_add["obj"].has_entrance:
                    connections_to_add.remove(connection_to_add)

            # We append the new connections at the front because then we continue creating the doors from the room
            # we just "walked" into.
            new_connections_to_process = connections_to_add
            new_connections_to_process.extend(connections_to_process)
            connections_to_process = new_connections_to_process

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
        # type: (list, str, list, Camera, list) -> None
        self.tilemap = Tilemap.Tilemap(tileset, map_size=(len(room_map), len(room_map[0])))
        self.room_map = room_map
        self.size = [len(room_map), len(room_map[0])]

        self.objects = objects          # Objects in the room
        self.camera = camera            # Camera (we have to draw relative to it)
        self.connections = connections  # Connections (used when the player changes the screen he is in)

        self.light_map = None

        self.display_surface = None

    def render(self):
        self.render_tiles()
        self.tilemap.scale()
        self.make_light_map()
        self.render_light_map()

    def fix(self):
        # We remove any wall which does not have another one below it (because to render we need double vertical wall)
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                if self.room_map[x][y] == RoomTiles.WALL:
                    if self.get(x, y - 1) != RoomTiles.WALL and self.get(x, y + 1) != RoomTiles.WALL:
                        self.room_map[x][y] = self.get(x, y + 1)

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

        surface.blit(self.light_map, (max(0, -self.camera.real_position.x),
                                      max(0, -self.camera.real_position.y)),
                     area=(max(0, self.camera.real_position.x),
                           max(0, self.camera.real_position.y),
                           min(self.light_map.get_width(),
                               self.camera.real_position.x + surface.get_width()),
                           min(self.light_map.get_height(),
                               self.camera.real_position.y + surface.get_height())),
                     special_flags=pygame.BLEND_RGB_MULT)

    def make_light_map(self):
        self.light_map = pygame.Surface((self.tilemap.r_image_scaled.get_width(),
                                         self.tilemap.r_image_scaled.get_height()),
                                        flags=pygame.HWSURFACE)

    def render_light_map(self):
        temp_screen = pygame.Surface((self.tilemap.r_image_scaled.get_width(),
                                      self.tilemap.r_image_scaled.get_height()), flags=pygame.HWSURFACE)
        for obj in self.objects:  # type: Object
            if isinstance(obj, BackedLightObject):
                temp_screen.fill((0, 0, 0))
                position = obj.position.copy()
                position.x -= obj.light_image.get_width() / 2
                position.y -= obj.light_image.get_height() / 2
                temp_screen.blit(obj.light_image, position.list())
                self.light_map.blit(temp_screen, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        pixels2 = pygame.surfarray.array2d(self.light_map)
        del pixels2

