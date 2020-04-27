import pygame
from Ray import Ray
from Vector2D import Vector2D
import time


def draw_mask(polygons, light_point, surface):
    # need to understand https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    # need to understand https://thecodingtrain.com/CodingChallenges/145-2d-ray-casting.html

    collision_points = []

    for polygon in range(0, len(polygons)):
        polygons[polygon] = polygons[polygon].get_points()

    for polygon in polygons:
        # points = polygon.points
        for point in range(0, len(polygon)):
            for i in range(0, 3):
                point_to_light = light_point.copy()
                point_to_light -= polygon[point]
                point_to_light.x += i - 1
                ray_light_to_point = Ray(light_point, point_to_light)

                closest_point = None
                closest_distance = (1280 + 1) ** 2 + (720 + 1) ** 2
                for polygon1 in polygons:
                    for point1 in range(0, len(polygon1)):
                        wall = [polygon1[point1], polygon1[(point1 + 1) % len(polygon1)]]
                        # wall = [polygon1[(point1 + 1) % len(polygon1)], polygon1[point1]]
                        coll = ray_light_to_point.cast(wall)

                        if coll is not None:
                            coll = coll.copy()
                            coll_to_light = coll.copy()  # type: Vector2D
                            coll_to_light -= light_point
                            distance = coll_to_light.magnitude ** 2
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_point = coll

                if closest_point is not None:
                    collision_points.append(closest_point)

    polygon_points = sorted(collision_points, key=lambda x: light_point.look_at_angle(x))

    list_points = []
    for vector in polygon_points:
        list_points.append(vector.list())

    if len(list_points) > 2:
        pygame.draw.polygon(surface, (128, 128, 40), list_points)
    return
