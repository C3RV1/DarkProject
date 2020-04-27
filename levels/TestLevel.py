import pygame
import GameManager
from utils import math2d
import math


class TestLevel:
    def __init__(self, game_manager):
        # type: (GameManager.GameManager) -> None
        self.game_manager = game_manager  # type: GameManager.GameManager

        self.polygon = [[100, 100], [100, 200], [200, 200], [200, 100]]

        self.light_point = [0, 0]
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
                                                 self.game_manager.screen.get_height()))

        self.circle_gradient_size = 470
        self.circle_gradient = pygame.Surface([self.circle_gradient_size * 2,
                                               self.circle_gradient_size * 2], pygame.HWSURFACE)

        for x in range(self.circle_gradient_size*2):
            for y in range(self.circle_gradient_size*2):
                d_x = x - self.circle_gradient_size
                d_y = y - self.circle_gradient_size
                d = (d_x**2 + d_y**2)**0.5
                value = 255 * (1 - (d / self.circle_gradient_size))
                if value < 0:
                    self.circle_gradient.set_at((x, y), 0)
                else:
                    self.circle_gradient.set_at((x, y), (value, value, value))

        self.view_angle = 10
        self.view_distance = (self.distance_angle_inverse_relation / (self.view_angle**self.smoother))

    def draw_mask(self, polygon):
        # need to understand https://stackoverflow.com/questions/3120357/get-closest-point-to-a-line

        polygon_points_projected = list(polygon)

        for i in range(0, len(polygon_points_projected)):
            point_to_light_1 = math2d.relative_to(polygon_points_projected[i], self.light_point)
            point_to_light_2 = math2d.relative_to(polygon_points_projected[(i + 1) % len(polygon)], self.light_point)

            point_1_copy = list(point_to_light_1)
            point_2_copy = list(point_to_light_2)

            math2d.set_vector_length(point_1_copy, self.view_distance)
            math2d.set_vector_length(point_2_copy, 300)

            """mid_point = [(point_1_copy[0] + point_2_copy[0]) / 2,
                         (point_1_copy[1] + point_2_copy[1]) / 2]

            mid_point_length = mid_point[0]**2 + mid_point[1]**2
            math2d.set_vector_length(mid_point, self.view_distance)

            augment = abs((mid_point[0]**2 + mid_point[1]**2) / mid_point_length)

            math2d.set_vector_length(point_to_light_1, self.view_distance*augment)
            math2d.set_vector_length(point_to_light_2, self.view_distance*augment)"""

            math2d.set_vector_length(point_to_light_1, self.view_distance)
            math2d.set_vector_length(point_to_light_2, self.view_distance)

            distance = [0, self.view_distance+2]
            math2d.vector_rotate(point_to_light_1, -self.rotation)
            math2d.vector_rotate(point_to_light_2, -self.rotation)

            aug_1 = distance[1] / point_to_light_1[1]
            if aug_1 < 0:
                aug_1 = 0
            aug_2 = distance[1] / point_to_light_2[1]
            if aug_2 < 0:
                aug_2 = 0

            point_to_light_1[0] *= aug_1
            point_to_light_1[1] *= aug_1
            point_to_light_2[0] *= aug_2
            point_to_light_2[1] *= aug_2

            math2d.vector_rotate(point_to_light_1, self.rotation)
            math2d.vector_rotate(point_to_light_2, self.rotation)

            point_to_light_1 = math2d.make_global(point_to_light_1, self.light_point)
            point_to_light_2 = math2d.make_global(point_to_light_2, self.light_point)

            polygon_points = [polygon[i], point_to_light_1, point_to_light_2, polygon[(i + 1) % len(polygon)]]
            pygame.draw.polygon(self.surface_to_screen, (0, 0, 0), polygon_points)
        return

    def main_loop(self, events):
        self.game_manager.screen.fill((255, 255, 255))
        self.game_manager.screen.blit(self.background, (0, 0))
        self.surface_to_screen.fill((0, 0, 0))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    self.view_angle -= self.view_angle_change * self.game_manager.delta_time
                elif event.button == 4:
                    self.view_angle += self.view_angle_change * self.game_manager.delta_time

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_w]:
            self.light_point[1] -= self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_s]:
            self.light_point[1] += self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_a]:
            self.light_point[0] -= self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_d]:
            self.light_point[0] += self.light_move_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_q]:
            self.rotation -= self.rotation_speed * self.game_manager.delta_time
        if keys_pressed[pygame.K_e]:
            self.rotation += self.rotation_speed * self.game_manager.delta_time

        self.light_point[0] = int(self.light_point[0])
        self.light_point[1] = int(self.light_point[1])

        triangle_point_1_ang = self.view_angle
        triangle_point_2_ang = -self.view_angle

        triangle_point_1 = [0, self.view_distance]
        triangle_point_2 = [0, self.view_distance]

        math2d.vector_rotate(triangle_point_1, triangle_point_1_ang)
        math2d.vector_rotate(triangle_point_2, triangle_point_2_ang)

        distance = [0, self.view_distance]

        aug_1 = abs(distance[1] / triangle_point_1[1])
        aug_2 = abs(distance[1] / triangle_point_2[1])

        triangle_point_1[0] *= aug_1
        triangle_point_1[1] *= aug_1
        triangle_point_2[0] *= aug_2
        triangle_point_2[1] *= aug_2

        math2d.vector_rotate(triangle_point_1, self.rotation)
        math2d.vector_rotate(triangle_point_2, self.rotation)

        if triangle_point_1[0] > self.circle_gradient_size-1:
            triangle_point_1[0] = self.circle_gradient_size-1
        if triangle_point_1[0] < -self.circle_gradient_size+1:
            triangle_point_1[0] = -self.circle_gradient_size+1

        if triangle_point_1[1] > self.circle_gradient_size-1:
            triangle_point_1[1] = self.circle_gradient_size-1
        if triangle_point_1[1] < -self.circle_gradient_size+1:
            triangle_point_1[1] = -self.circle_gradient_size+1

        if triangle_point_2[0] > self.circle_gradient_size-1:
            triangle_point_2[0] = self.circle_gradient_size-1
        if triangle_point_2[0] < -self.circle_gradient_size+1:
            triangle_point_2[0] = -self.circle_gradient_size+1

        if triangle_point_2[1] > self.circle_gradient_size-1:
            triangle_point_2[1] = self.circle_gradient_size-1
        if triangle_point_2[1] < -self.circle_gradient_size+1:
            triangle_point_2[1] = -self.circle_gradient_size+1

        triangle_point_1 = math2d.make_global(triangle_point_1, self.light_point)
        triangle_point_2 = math2d.make_global(triangle_point_2, self.light_point)

        pygame.draw.polygon(self.surface_to_screen, (255, 255, 255), [self.light_point,
                                                                      triangle_point_1,
                                                                      triangle_point_2])

        self.surface_to_screen.blit(self.circle_gradient,
                                    [self.light_point[0] - self.circle_gradient.get_width() / 2,
                                     self.light_point[1] - self.circle_gradient.get_height() / 2],
                                    special_flags=pygame.BLEND_RGBA_MULT)

        self.view_distance = int(self.view_distance)

        self.draw_mask(self.polygon)
        self.game_manager.screen.blit(self.surface_to_screen, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        pygame.draw.polygon(self.game_manager.screen, (0, 255, 0), self.polygon)
        pygame.draw.circle(self.game_manager.screen, (0, 0, 128), self.light_point, 5)
