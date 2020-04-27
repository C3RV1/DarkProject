import os
from utils.Vector2D import Vector2D
import json
import random
import Room
from Object import Object, ObjectUnpacker
from utils.Camera import Camera
import GameManager


class WorldGenerator:
    def __init__(self, game_manager, world_configurations, world_folder, seed=None,
                 camera=None):
        # type: (GameManager.GameManager, str, str, int, Camera) -> None

        self.game_manager = game_manager
        self.camera = camera

        if not os.path.isfile(world_configurations):
            raise Exception("Missing world configurations")

        world_configurations_file = open(world_configurations, "rb")
        self.world_configurations = json.loads(world_configurations_file.read())
        world_configurations_file.close()

        # World Configuration
        self.world_size = self.world_configurations["world_size"]
        self.world_bounds = [int(-self.world_size[0] / 2),
                             int(-self.world_size[1] / 2),
                             int(self.world_size[0] / 2),
                             int(self.world_size[1] / 2)]

        self.max_room_size = self.world_configurations["max_room_size"]

        self.world_folder = world_folder
        if not os.path.isdir(self.world_folder):
            os.mkdir(self.world_folder)
            self.new_world(seed)

        self.world_data_file = open(self.world_folder + "/world_data.json", "rb")
        self.world_data = json.loads(self.world_data_file.read())
        self.world_data_file.close()

        self.seed = self.world_data["seed"]

        if not os.path.isfile(self.world_folder + "/rooms/room_0_0.json") or True:
            self.room_0_gen()

        self.current_room = Vector2D(0, 0)
        self.current_room_obj = None

    def new_world(self, seed):
        if seed is None:
            random.seed()
            seed = random.randint(0, 65536)

        world_data = {"seed": seed}
        world_data_path = self.world_folder + "/world_data.json"
        world_data_file = open(world_data_path, "wb")
        world_data_file.write(json.dumps(world_data))
        world_data_file.close()

        room_folder = self.world_folder + "/rooms"
        os.mkdir(room_folder)

    def room_0_gen(self):
        room_folder = self.world_folder + "/rooms"
        room_1_path = room_folder + "/room_0_0.json"
        room_1_file = open(room_1_path, "wb")

        room_size = [13, 10]
        # room_size = [23, 20]

        complete_room_size = [room_size[0] + (40 - room_size[0]), room_size[1] + (26 - room_size[0])]
        # complete_room_size = [room_size[0] + (40 - room_size[0]), room_size[1] + (26 - room_size[0])]

        room_1_connections = [[0, 0], [0, 0], [0, 0], [complete_room_size[0]-1, (complete_room_size[1]-1) / 2]]

        room_1_map = []
        for x in range(0, complete_room_size[0]):
            room_1_map.append([])
            for y in range(0, complete_room_size[1]):
                room_1_map[-1].append(0)

        for x in range((complete_room_size[0] - room_size[0]) / 2, (complete_room_size[0] + room_size[0]) / 2):
            for y in range((complete_room_size[1] - room_size[1]) / 2, (complete_room_size[1] + room_size[1]) / 2):
                room_1_map[x][y] = 1

        for x in [(complete_room_size[0] - room_size[0]) / 2 - 1, (complete_room_size[0] + room_size[0]) / 2]:
            for y in range((complete_room_size[1] - room_size[1]) / 2 - 1, (complete_room_size[1] + room_size[1]) / 2 + 1):
                room_1_map[x][y] = 2

        for x in range((complete_room_size[0] - room_size[0]) / 2 - 1, (complete_room_size[0] + room_size[0]) / 2 + 1):
            for y in [(complete_room_size[1] - room_size[1]) / 2 - 2, (complete_room_size[1] - room_size[1]) / 2 - 1,
                      (complete_room_size[1] + room_size[1]) / 2, (complete_room_size[1] + room_size[1]) / 2 + 1]:
                room_1_map[x][y] = 2

        for connection in range(3, 4):
            if room_1_connections[connection] is None:
                continue
            x = room_1_connections[connection][0]
            y = room_1_connections[connection][1]
            while not (complete_room_size[0] - room_size[0]) / 2 <= x <= (complete_room_size[0] + room_size[0]) / 2 - 1:
                room_1_map[x][y] = 1
                x += -1 * int(x > (complete_room_size[0] - room_size[0]) / 2) + 1 * int(x < (complete_room_size[0] + room_size[0]) / 2 - 1)
            while not (complete_room_size[1] - room_size[1]) / 2 <= y <= (complete_room_size[1] + room_size[1]) / 2 - 1:
                room_1_map[x][y] = 1
                y += -1 * int(y > (complete_room_size[1] - room_size[1]) / 2) + 1 * int(y < (complete_room_size[1] + room_size[1]) / 2 - 1)

        objects = [ObjectUnpacker.unpack({"obj_data": {"pos": [14 * 8 * 4 + 20 * 4,
                                                               5 * 8 * 4 + 20 * 4]},
                                          "obj_id": 0}, None).pack()]

        room_1_file.write(json.dumps({"map": room_1_map, "objects": objects,
                                      "connections": room_1_connections}, indent=2))
        room_1_file.close()

    def get_current_room(self):
        room_path = self.world_folder + "/rooms/room_{}_{}.json".format(int(self.current_room.x),
                                                                        int(self.current_room.y))
        if not os.path.isfile(room_path):
            Room.RoomGenerator(self.current_room.copy(), self)

        room_file = open(room_path, "rb")
        room_json = room_file.read()
        room_file.close()

        room_data = json.loads(room_json)

        room_map = room_data["map"]
        room_objects = room_data["objects"]
        room_connections = room_data["connections"]
        for obj in range(0, len(room_objects)):
            room_objects[obj] = ObjectUnpacker.unpack(room_objects[obj], self.camera)

        room_renderer = Room.RoomRenderer(room_map, "game_data/tileset/tileset1", objects=room_objects,
                                          camera=self.camera, connections=room_connections)
        room_renderer.render()
        self.current_room_obj = room_renderer

        return room_renderer

    def save_room(self):
        if self.current_room_obj is None:
            return

        room_map = self.current_room_obj.room_map
        room_objects = self.current_room_obj.objects
        room_connections = self.current_room_obj.connections

        new_room_objects = []
        for obj in range(0, len(room_objects)):
            if room_objects[obj].obj_id == 65:
                continue
            new_room_objects.append(room_objects[obj].pack())

        room_dict = {"map": room_map,
                     "objects": new_room_objects,
                     "connections": room_connections}

        room_path = self.world_folder + "/rooms/room_{}_{}.json".format(int(self.current_room.x),
                                                                        int(self.current_room.y))
        room_file = open(room_path, "wb")

        room_file.write(json.dumps(room_dict))

    def save_player(self, player_obj):
        # type: (Object) -> None
        player_saved = player_obj.pack()
        player_path = self.world_folder + "/player.json"
        player_file = open(player_path, "wb")
        player_file.write(json.dumps(player_saved))
        player_file.close()

    def load_player(self):
        player_path = self.world_folder + "/player.json"
        if not os.path.isfile(player_path):
            return None
        player_file = open(player_path, "wb")
        player_data = json.loads(player_file.read())
        player_file.close()
        return player_data
