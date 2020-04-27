from Vector2D import Vector2D
import GameManager


class Camera:
    def __init__(self, game_manager, position=Vector2D(0, 0),
                 world_size=Vector2D(0, 0)):
        self.game_manager = game_manager  # type: GameManager.GameManager
        self.position = position.copy()
        self.real_position = Vector2D(0, 0)
        self.__target = None  # type: Vector2D

        self.move_time = 2
        self.position_to_real()
        self.world_size = world_size

    def position_to_real(self):
        self.real_position = self.position.copy()
        self.real_position -= Vector2D(self.game_manager.screen.get_width() / 2,
                                       self.game_manager.screen.get_height() / 2)

    def target(self, target):
        self.__target = target

    def update(self, time_step):
        if self.__target is not None:
            d = self.__target.copy()
            d.relative_to(self.position)
            d *= self.move_time * time_step
            self.position += d
        self.position_to_real()

        if self.real_position.x + self.game_manager.screen.get_width() > self.world_size.x:
            self.position.x = self.world_size.x - (self.game_manager.screen.get_width() / 2)
        if self.real_position.y + self.game_manager.screen.get_height() > self.world_size.y:
            self.position.y = self.world_size.y - (self.game_manager.screen.get_height() / 2)
        if self.real_position.x < 0:
            self.position.x = self.game_manager.screen.get_width() / 2
        if self.real_position.y < 0:
            self.position.y = self.game_manager.screen.get_height() / 2

        self.position_to_real()
