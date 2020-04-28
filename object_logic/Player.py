from generators.Object import Object
from utils.Vector2D import Vector2D
from generators.WorldGenerator import WorldGenerator
from generators.InteractiveObject import InteractiveObject, InteractionType
from sprites.Animation import Animation
import GameManager
import pygame


class PlayerObject(Object):
    def __init__(self, game_manager, world_generator, camera, obj_data=None, position=Vector2D(0, 0)):
        Object.__init__(self, 65, camera=camera)
        if obj_data is None:
            self.position = position
            self.screen = Vector2D(0, 0)
        else:
            self.position = Vector2D(0, 0, lst=obj_data["position"])
            self.screen = Vector2D(0, 0, lst=obj_data["screen"])

        self.animation_base_folder = "game_data/sprites/player"
        self.animations_to_load = [{"name": "wake_up",
                                    "scale": 4,
                                    "loop": False,
                                    "fps": 12},
                                   {"name": "idle",
                                    "scale": 4,
                                    "loop": True,
                                    "fps": 2}]

        self.load_animations()
        self.set_animation("wake_up")

        self.world_generator = world_generator  # type: WorldGenerator
        self.current_room = None
        self.change_current_room(self.screen.x, self.screen.y)

        self.game_manager = game_manager  # type: GameManager.GameManager

        self.move_speed = 100

        self.interacting_distance = 100

        self.interacting = False
        self.interacting_object = 0
        self.interactive_close = False
        self.interactive_close_num = 0

        self.interactive_ui_animation = Animation("game_data/sprites/ui/interact_text",
                                                  loop=True,
                                                  scale=2,
                                                  frames_per_second=2)

        # Fade in
        self.fade_in_surface = pygame.Surface(self.game_manager.screen.get_size())
        self.fade_in_surface.fill((0, 0, 0))

    def behaviour(self, events):
        if not self.interacting and not self.current_animation == "wake_up":
            self.interactive_close = False
            self.interactive_close_num = -1
            closest_d = 10000

            for obj in range(0, len(self.current_room.objects)):
                d = self.current_room.objects[obj].position.copy()  # type: Vector2D
                d.relative_to(self.position)
                d = d.magnitude  # type: float
                if d < self.interacting_distance and isinstance(self.current_room.objects[obj], InteractiveObject):
                    if d < closest_d:
                        self.interactive_close_num = obj
                        self.interactive_close = True
                        closest_d = d

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        if self.interactive_close:
                            self.interacting = True
                            self.interacting_object = self.interactive_close_num
                            self.current_room.objects[self.interacting_object].interacting = True
                            self.current_room.objects[self.interacting_object].interacting_type = InteractionType.MENU
                    if event.key == pygame.K_ESCAPE:
                        self.world_generator.save_room()
                        self.world_generator.save_player(self)
                        self.game_manager.exit()

            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_w]:
                self.position.y -= self.move_speed * self.game_manager.delta_time
            if pressed_keys[pygame.K_s]:
                self.position.y += self.move_speed * self.game_manager.delta_time
            if pressed_keys[pygame.K_a]:
                self.position.x -= self.move_speed * self.game_manager.delta_time
            if pressed_keys[pygame.K_d]:
                self.position.x += self.move_speed * self.game_manager.delta_time

        if self.position.x >= self.current_room.tilemap.r_image_scaled.get_width():
            self.screen.x += 1
            self.change_current_room(self.screen.x, self.screen.y)
            self.position.set(self.current_room.connections[2][0] * 8 * 4, self.current_room.connections[2][1] * 8 * 4)
        elif self.position.x < 0:
            self.screen.x -= 1
            self.change_current_room(self.screen.x, self.screen.y)
            self.position.set(self.current_room.connections[3][0] * 8 * 4, self.current_room.connections[3][1] * 8 * 4)
        if self.position.y >= self.current_room.tilemap.r_image_scaled.get_height():
            self.screen.y += 1
            self.change_current_room(self.screen.x, self.screen.y)
            self.position.set(self.current_room.connections[0][0] * 8 * 4, self.current_room.connections[0][1] * 8 * 4)
        elif self.position.y < 0:
            self.screen.y -= 1
            self.change_current_room(self.screen.x, self.screen.y)
            self.position.set(self.current_room.connections[1][0] * 8 * 4, self.current_room.connections[1][1] * 8 * 4)

        if self.interacting:
            if self.current_room.objects[self.interacting_object].interacting:
                self.current_room.objects[self.interacting_object].interacting_behaviour(events)
            else:
                self.interacting = False

        if self.current_animation == "wake_up" and self.animations[self.current_animation].finished:
            self.set_animation("idle")

    def extra_draw(self):
        if self.interactive_close and not self.interacting:
            self.game_manager.screen.blit(self.interactive_ui_animation.get_frame(self.game_manager.delta_time),
                                          (self.real_position.x + 50, self.real_position.y + 50))
        if self.interacting:
            self.current_room.objects[self.interacting_object].custom_interacting_draw(self.game_manager.screen)
            pygame.draw.circle(self.game_manager.screen, (255, 0, 0), (100, 100), 5)

        if self.current_animation == "wake_up":
            self.fade_in_surface.set_alpha(255 - int(255 * self.animations[self.current_animation].percentage))
            self.game_manager.screen.blit(self.fade_in_surface, (0, 0))

    def change_current_room(self, x, y):
        self.world_generator.save_room()
        self.world_generator.current_room.x = x
        self.world_generator.current_room.y = y
        self.current_room = self.world_generator.get_current_room()
        self.current_room.objects.append(self)

        self.camera.world_size.x = self.current_room.tilemap.r_image_scaled.get_width()
        self.camera.world_size.y = self.current_room.tilemap.r_image_scaled.get_height()

    def pack(self):
        packed_dict = {}
        packed_dict["position"] = self.position.list()
        packed_dict["screen"] = self.screen.list()
        return packed_dict
