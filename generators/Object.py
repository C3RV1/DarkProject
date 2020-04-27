from utils.Vector2D import Vector2D
from sprites.Animation import Animation
import math


class Object(object):
    def __init__(self, obj_id=0, camera=None):
        self.position = Vector2D(0, 0)  # World position
        self.real_position = Vector2D(0, 0)  # Render position on screen
        self.size = Vector2D(0, 0)
        self.obj_id = obj_id
        self.animations = {}
        self.animation_base_folder = ""
        self.current_animation = ""

        self.scaling = 1
        self.animations_to_load = []

        self.camera = camera

    def position_to_real(self):
        self.real_position.x = self.position.x
        self.real_position.y = self.position.y
        size = self.animations[self.current_animation].next_frame(addition=0).get_size()
        self.real_position.x -= size[0] / 2
        self.real_position.y -= size[1] / 2
        if self.camera is not None:
            self.real_position.relative_to(self.camera.real_position)
        else:
            print self.obj_id

    def load_animations(self):
        for animation in self.animations_to_load:
            self.animations[animation["name"]] = Animation(self.animation_base_folder + "/" + animation["name"],
                                                           scale=animation["scale"],
                                                           loop=animation["loop"],
                                                           frames_per_second=animation["fps"])

    def get_render(self, delta_time):
        return self.animations[self.current_animation].get_frame(delta_time)

    def set_animation(self, animation):
        if animation not in self.animations.keys():
            return
        self.current_animation = animation
        self.animations[self.current_animation].reset()

    def behaviour(self, events):
        pass

    def update(self, events):
        self.behaviour(events)
        self.position_to_real()

    def obj_data(self):
        pos = self.position.list()
        return {"pos": pos}

    def pack(self):
        obj_id = self.obj_id
        return {"obj_id": obj_id,
                "obj_data": self.obj_data()}


from object_logic import Pod


class ObjectUnpacker:
    @staticmethod
    def unpack(packed_data, camera):
        obj_id = packed_data["obj_id"]
        if obj_id == 0:
            return Pod.PodObject(packed_data["obj_data"], camera)

