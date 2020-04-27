import pygame
import GameManager
from utils import math2d
import math
from utils import Ray
from utils import Polygon
from utils.Vector2D import Vector2D
from utils import Shadow


class TestLevel:
    def __init__(self, game_manager):
        # type: (GameManager.GameManager) -> None
        self.game_manager = game_manager  # type: GameManager.GameManager

        self.polygons = [Polygon.Polygon(Vector2D(0, 0), [Vector2D(100, 100),
                                                          Vector2D(100, 250),
                                                          Vector2D(200, 200),
                                                          Vector2D(200, 100)])]

        self.polygons.append(Polygon.Polygon(Vector2D(200, 0), [Vector2D(100, 100),
                                                                Vector2D(100, 250),
                                                                Vector2D(200, 200),
                                                                Vector2D(200, 100)]))

        self.polygons.append(Polygon.Polygon(Vector2D(400, 0), [Vector2D(100, 100),
                                                                Vector2D(100, 250),
                                                                Vector2D(200, 200),
                                                                Vector2D(200, 100)]))

        self.light_point = Vector2D(0, 0)
        self.light_move_speed = 200
        self.view_angle = 60

        self.view_angle_change = 360

        self.view_distance = 300

        self.smoother = 0.25

        self.distance_angle_inverse_relation = self.view_angle**self.smoother * self.view_distance

        self.background = pygame.image.load("game_data/levels/test_level_background.png").convert_alpha()

        self.rotation = 0
        self.rotation_speed = 90

        self.surface_to_screen = pygame.Surface((self.game_manager.screen.get_width(),
                                                 self.game_manager.screen.get_height()), pygame.HWSURFACE)

        self.circle_gradient_size = 500
        self.circle_gradient = pygame.Surface([self.circle_gradient_size * 2,
                                               self.circle_gradient_size * 2], pygame.HWSURFACE)

        self.current_target_point = Vector2D(0, 0)

        for x in range(self.circle_gradient_size*2):
            for y in range(self.circle_gradient_size*2):
                d_x = x - self.circle_gradient_size
                d_y = y - self.circle_gradient_size
                d = (d_x**2 + d_y**2)**0.5
                value = 180 * (1 - (d / self.circle_gradient_size))
                if value < 0:
                    self.circle_gradient.set_at((x, y), 0)
                else:
                    self.circle_gradient.set_at((x, y), (value, value, value))

        """self.view_angle = 10
        self.view_distance = (self.distance_angle_inverse_relation / (self.view_angle**self.smoother))"""

    def set_point_distance(self, point, length):
        # type: (Vector2D, float) -> Vector2D
        point_relative_light = point.copy()

        point_relative_light.normalize()
        point_relative_light *= length
        point_relative_light.rotate(-self.rotation)

        if point_relative_light.y == 0:
            point_relative_light.y += 1

        visible = 1
        if point_relative_light.y < 0:
            visible = -1

        aug_1 = (length + 2) * visible / point_relative_light.y

        point_relative_light.x *= aug_1
        point_relative_light.y *= aug_1

        point_relative_light.rotate(self.rotation)

        return point_relative_light

    def main_loop(self, events):
        # self.game_manager.screen.fill((255, 255, 255))
        self.game_manager.screen.blit(self.background, (0, 0))
        self.surface_to_screen.fill((0, 0, 0, 0))

        mouse_pos = Vector2D(0, 0, lst=pygame.mouse.get_pos())

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    self.view_angle -= self.view_angle_change * self.game_manager.delta_time
                elif event.button == 4:
                    self.view_angle += self.view_angle_change * self.game_manager.delta_time
                elif event.button == 1:
                    self.current_target_point = mouse_pos.copy()

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_w]:
            self.light_point.y -= self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_s]:
            self.light_point.y += self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_a]:
            self.light_point.x -= self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_d]:
            self.light_point.x += self.light_move_speed * self.game_manager.delta_time
        """if keys_pressed[pygame.K_q]:
            self.rotation -= self.rotation_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_e]:
            self.rotation += self.rotation_speed * self.game_manager.delta_time"""

        self.rotation = (self.light_point.look_at_angle(mouse_pos) + 90) % 360

        """if self.light_point.distance_to(self.current_target_point) > 10:
            movement = Vector2D(0, 1)
            movement.rotate((self.light_point.look_at_angle(self.current_target_point) + 90) % 360)
            movement *= self.light_move_speed * self.game_manager.delta_time

            self.light_point += movement"""

        if self.view_angle > 40:
            self.view_angle = 40
        elif self.view_angle < 10:
            self.view_angle = 10

        self.view_angle = math2d.to360rotation(self.view_angle)
        self.rotation = math2d.to360rotation(self.rotation)
        self.view_distance = (self.distance_angle_inverse_relation / (self.view_angle ** self.smoother))

        self.light_point.x = int(self.light_point.x)
        self.light_point.y = int(self.light_point.y)

        triangle_point_1_ang = self.rotation + self.view_angle
        triangle_point_2_ang = self.rotation - self.view_angle

        triangle_point_1 = Vector2D(0, self.view_distance)
        triangle_point_2 = Vector2D(0, self.view_distance)

        triangle_point_1.rotate(triangle_point_1_ang)
        triangle_point_2.rotate(triangle_point_2_ang)

        triangle_point_1 = self.set_point_distance(triangle_point_1, self.view_distance-2)
        triangle_point_2 = self.set_point_distance(triangle_point_2, self.view_distance-2)

        back_light = Vector2D(0, -10)
        back_light.rotate(self.rotation)

        self.view_distance = int(self.view_distance)

        polygons = list(self.polygons)
        polygons.append(Polygon.Polygon(self.light_point, [back_light, triangle_point_1, triangle_point_2]))

        Shadow.draw_mask(polygons, self.light_point, self.surface_to_screen)

        self.surface_to_screen.blit(self.circle_gradient,
                                    [self.light_point.x - self.circle_gradient.get_width() / 2,
                                     self.light_point.y - self.circle_gradient.get_height() / 2],
                                    special_flags=pygame.BLEND_RGB_MULT)

        self.game_manager.screen.blit(self.surface_to_screen, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        pygame.draw.circle(self.game_manager.screen, (0, 0, 128), self.light_point.list(), 5)
