import GameManager
import pygame


class TextBoxTypes:
    def __init__(self):
        pass

    STRING = 0
    INTEGER = 1


class TextBox:
    def __init__(self, game_manager, rect, input_text, text_color, type=TextBoxTypes.STRING,
                 default_text="", font="game_data/fonts/press_start_2p.ttf",
                 font_size=30, max_value=None):
        self.game_manager = game_manager  # type: GameManager.GameManager

        self.font = pygame.font.Font(font, font_size)

        self.current_text = default_text

        self.input_text = self.font.render(input_text, False, text_color)  # type: pygame.Surface

        self.rect = list(rect)
        self.rect.append(self.input_text.get_height() + 30)

        self.input_text_pos = [self.rect[0] + 10, self.rect[1] + (self.rect[3] - self.input_text.get_height()) / 2]

        self.input_box_pos = [10 + self.input_text.get_width() + 20,
                              (self.rect[3] - self.input_text.get_height()) / 2]

        self.input_box_width = self.rect[2] - self.input_box_pos[0] - 10

        self.input_box_pos[0] += self.rect[0]
        self.input_box_pos[1] += self.rect[1]

        self.text_color = text_color

        self.shift = False

        self.type = type

        self.max_value = max_value

    def key_down(self, key):
        if key == pygame.K_BACKSPACE:
            if len(self.current_text) > 0:
                self.current_text = self.current_text[:-1]
            return
        elif key == pygame.K_LSHIFT:
            self.shift = True
        elif key <= 127:
            char = chr(key)
            if self.type == TextBoxTypes.INTEGER:
                if char not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    return
            else:
                if self.shift:
                    char = char.upper()
                if self.max_value is not None:
                    if len(self.current_text) + 1 > self.max_value:
                        return
            self.current_text += char
            if self.type == TextBoxTypes.INTEGER:
                if self.max_value is not None:
                    try:
                        if int(self.current_text) > self.max_value:
                            self.current_text = int(self.max_value)
                    except:
                        self.current_text = ""

    def key_up(self, key):
        if key == pygame.K_LSHIFT:
            self.shift = False

    def draw(self):
        current_text_rendered = self.font.render(self.current_text, False, self.text_color)

        while current_text_rendered.get_width() > self.input_box_width - 10:
            if len(self.current_text) == 0:
                break
            self.current_text = self.current_text[:-1]
            current_text_rendered = self.font.render(self.current_text, False, self.text_color)

        self.game_manager.screen.blit(self.input_text, self.input_text_pos)

        self.game_manager.screen.blit(current_text_rendered, self.input_box_pos)

        pygame.draw.rect(self.game_manager.screen,
                         (255, 255, 255),
                         (self.input_box_pos[0] - 10,
                          self.input_box_pos[1] - 10,
                          self.input_box_width,
                          current_text_rendered.get_height() + 10),
                         2)

    def check_box(self, point):
        if self.rect[0] < point[0] < self.rect[0] + self.rect[2] and self.rect[1] < point[1] < self.rect[1] + self.rect[3]:
            return True
        return False

    def get_text(self):
        return str(self.current_text)