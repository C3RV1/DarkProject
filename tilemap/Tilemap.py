import pygame
import json


class Tilemap:
    def __init__(self, tileset_folder_path, map_size=(128, 128), map_data=None):
        self.map_size = map_size
        if map_data is None:
            self.map_data = []
            for x in range(0, self.map_size[0]):
                self.map_data.append([])
                for y in range(0, self.map_size[1]):
                    self.map_data[-1].append(0)
        else:
            self.map_data = map_data

        self.set_tilemap(tileset_folder_path)

        self.rendered_image = pygame.Surface((int(self.map_size[0] * self.tileset_data["tile_size"][0]),
                                              int(self.map_size[1] * self.tileset_data["tile_size"][1])))
        self.r_image_scaled = pygame.Surface((self.map_size[0] * self.tileset_data["tile_size"][0] * 4,
                                              self.map_size[1] * self.tileset_data["tile_size"][1] * 4))

        self.scaling = 4
        self.make_scaled()

        self.render()

        self.fill_next_blocks_to_do = []
        self.fill_blocks_done = []
        self.fill_x = 0
        self.fill_y = 0
        self.fill_blocks_to_do = []
        self.fill_current_block = 0
        self.fill_new_block = 0

    def zoom_in(self):
        if self.scaling == 8:
            return False
        self.scaling *= 2
        self.make_scaled()
        self.scale()
        return True

    def zoom_out(self):
        if self.scaling == 1:
            return False
        self.scaling /= 2
        self.make_scaled()
        self.scale()
        return True

    def make_scaled(self):
        self.r_image_scaled = pygame.Surface((self.map_size[0] * self.tileset_data["tile_size"][0] * self.scaling,
                                              self.map_size[1] * self.tileset_data["tile_size"][1] * self.scaling))

    def render(self):
        for x in range(0, self.map_size[0]):
            for y in range(0, self.map_size[1]):
                self.render_tile(x, y)
        self.scale()

    def render_tile(self, x, y):
        try:
            tile = self.tiles_keys[self.map_data[x][y]]
        except:
            return
        self.rendered_image.blit(self.tiles_surfaces[tile],
                                 (x * self.tileset_data["tile_size"][0],
                                  y * self.tileset_data["tile_size"][1]))

    def scale(self):
        pygame.transform.scale(self.rendered_image, (self.rendered_image.get_width()*self.scaling,
                                                     self.rendered_image.get_height()*self.scaling),
                               self.r_image_scaled)

    def get_scale(self):
        return self.scaling

    def change_block_at(self, x, y, new_tile, make_scaled=True):
        if x >= self.map_size[0] or x < 0:
            return
        if y >= self.map_size[1] or y < 0:
            return
        x = int(x)
        y = int(y)
        self.map_data[x][y] = self.tiles_keys.index(new_tile)
        self.render_tile(x, y)
        if make_scaled:
            self.scale()

    def start_fill(self, fill_x, fill_y, new_block):
        if fill_x >= self.map_size[0] or fill_x < 0:
            return False
        if fill_y >= self.map_size[1] or fill_y < 0:
            return False
        self.fill_next_blocks_to_do = []
        self.fill_blocks_done = []
        self.fill_x = int(fill_x)
        self.fill_y = int(fill_y)
        self.fill_blocks_to_do = [[self.fill_x, self.fill_y]]
        self.fill_current_block = self.map_data[self.fill_x][self.fill_y]
        self.fill_new_block = new_block
        return True

    def continue_fill(self):
        if not self.fill_blocks_to_do:
            self.render()
            return True

        fill_next_blocks_to_do = []
        for block in self.fill_blocks_to_do:
            self.fill_blocks_done.append([block[0], block[1]])
            self.map_data[block[0]][block[1]] = self.fill_new_block
            arround = [[[self.fill_new_block - 1, self.fill_new_block - 1, self.fill_new_block - 1],
                           [self.fill_new_block - 1, self.fill_new_block, self.fill_new_block - 1],
                           [self.fill_new_block - 1, self.fill_new_block - 1, self.fill_new_block - 1]]]
            for x_off in range(0, 3):
                for y_off in range(0, 3):
                    if x_off == 1 and y_off == 1:
                        continue
                    if block[0] + x_off - 1 < 0 or block[0] + x_off - 1 >= self.map_size[
                        0] or block[1] + y_off - 1 < 0 or block[1] + y_off - 1 >= \
                            self.map_size[1]:
                        continue
                    arround[x_off][y_off] = self.map_data[block[0] + x_off - 1][block[1] + y_off - 1]

            for block_x in range(0, 3):
                for block_y in range(0, 3):
                    if block_x == 1 and block_y == 1:
                        continue
                    if arround[block_x][block_y] == self.fill_current_block:
                        if block[1] + block_y - 1 >= self.map_size[1]:
                            continue
                        if block[1] + block_y - 1 < 0:
                            continue
                        if block[0] + block_x - 1 >= self.map_size[0]:
                            continue
                        if block[0] + block_x - 1 < 0:
                            continue
                        if [block[0] + block_x - 1, block[1] + block_y - 1] not in self.fill_blocks_done:
                            if [block[0] + block_x - 1, block[1] + block_y - 1] not in fill_next_blocks_to_do:
                                fill_next_blocks_to_do.append([block[0] + block_x - 1, block[1] + block_y - 1])
        self.fill_blocks_to_do = fill_next_blocks_to_do
        return False

    def set_tilemap(self, new_tilemap_folder):
        self.tileset_folder = new_tilemap_folder

        tilemap_data_file = open(self.tileset_folder + "/tilemap_data.json", "r")
        tilemap_data_json = tilemap_data_file.read()
        tilemap_data_file.close()

        self.tileset_data = json.loads(tilemap_data_json)

        tilemap_image = pygame.image.load(self.tileset_folder + "/tileset.png")  # type: pygame.Surface
        tilemap_image = tilemap_image.convert()

        self.tiles_keys = sorted(self.tileset_data["tiles"].keys())

        self.tiles_surfaces = {}

        tile_size = list(self.tileset_data["tile_size"])

        for tile in self.tiles_keys:
            self.tiles_surfaces[tile] = pygame.Surface((tile_size[0],
                                                        tile_size[1]))
            self.tiles_surfaces[tile].blit(tilemap_image, (0, 0),
                                           area=(
                                               self.tileset_data["tiles"][tile][0] * tile_size[0],
                                               self.tileset_data["tiles"][tile][1] * tile_size[1],
                                               tile_size[0],
                                               tile_size[1]))
            pygame.transform.scale(self.tiles_surfaces[tile],
                                   (self.tileset_data["tile_size"][0] * 8,
                                    self.tileset_data["tile_size"][1] * 8))

        # self.render()
