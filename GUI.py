import math
import pygame as pg
import pygame_render as pr
import game_engine
from numpy2048 import UP, DOWN, LEFT, RIGHT


# TODO not only square
# TODO fix colors
# TODO undo score dec
# TODO AI for not 4x4 map
# TODO pruning


def get_color(number):
    return 250, 255 * (15 - (math.log(number, 2))) // 15, 90


class GameGUI:
    class AnimatedCell:
        max_pump = 10

        def __init__(self, spacing, speed, height, width, start, finish, value, new_value=None):
            self._x = start[1] * (width + spacing) + spacing
            self._y = start[0] * (height + spacing) + spacing
            self._height = height
            self._width = width
            self.value = value
            self.speed = speed
            self.merge_speed = 0.5
            self.grow_speed = 175 // self.speed
            self.new_value = new_value
            self.dx = (finish[1] - start[1]) * (width + spacing)
            self.dy = (finish[0] - start[0]) * (height + spacing)
            self.pump = 0
            if self.is_growing:
                self.pump = -min(self.height // 2, self.width // 2)

        @property
        def x(self):
            return self._x - self.pump

        @x.setter
        def x(self, value):
            self._x = value

        @property
        def y(self):
            return self._y - self.pump

        @y.setter
        def y(self, value):
            self._y = value

        @property
        def height(self):
            return self._height + self.pump * 2

        @property
        def width(self):
            return self._width + self.pump * 2

        @property
        def is_growing(self):
            return self.value == self.new_value

        @property
        def is_merging(self):
            return not self.is_moving and self.new_value is not None and self.new_value != self.value

        @property
        def is_moving(self):
            return not (abs(self.dx) < self.speed and abs(self.dy) < self.speed)

        def merge(self):
            if not self.is_merging:
                return False
            if self.value == self.new_value:
                self.pump -= self.merge_speed
            else:
                self.pump += self.merge_speed
            if self.pump >= self.max_pump:
                self.pump = self.max_pump
                self.value = self.new_value
            if self.pump <= 0:
                self.new_value = None
                self.pump = 0
            return True

        def move(self):
            if not self.is_moving:
                return False
            if self.dx < 0:
                self.dx += self.speed
                self.x -= self.speed
            elif self.dx > 0:
                self.dx -= self.speed
                self.x += self.speed
            if self.dy < 0:
                self.dy += self.speed
                self.y -= self.speed
            elif self.dy > 0:
                self.dy -= self.speed
                self.y += self.speed
            if not self.is_moving:
                self.x += self.dx
                self.dx = 0
                self.y += self.dy
                self.dy = 0
            return True

        def grow(self):
            if not self.is_growing:
                return False
            if self.pump >= 0:
                self.new_value = None
                self.pump = 0
            else:
                self.pump += self.grow_speed
            return True

    def __init__(self, game_size):
        # game attributes
        self.main_color = (180, 170, 160)
        self.display_width = 498  # int(498 * 1.5)
        self.display_height = 650

        # cell and grid of cells attributes
        self.game_size = game_size
        self.spacing = 7
        self.cell_speed = self.display_width // 80 * self.game_size
        self.cell_width = (self.display_width - (self.game_size + 1) * self.spacing) // self.game_size
        self.cell_height = self.cell_width  # (self.display_width - (self.game_size + 1) * self.spacing) // self.game_size
        self.grid_pixel_size = self.spacing + self.game_size * (self.spacing + self.cell_height)
        self.AnimatedCell.max_pump = abs(self.spacing - 1)
        self.cell_font_size = self.cell_height // 2
        self.cell_font = pg.font.SysFont("arial.ttf", self.cell_font_size)
        self.game_over_font_size = self.grid_pixel_size // 6

        # button attributes
        self.buttons = {"New game": (0, self.new_game), "Undo": (1, self.undo), "Run AI": (2, self.run_ai)}
        self.buttons_number = len(self.buttons)
        self.button_height = (self.display_height - self.grid_pixel_size - self.spacing * 2) // 2
        self.button_width = (self.display_width - (self.buttons_number + 1) * self.spacing) // self.buttons_number
        self.button_font_size = self.button_height // 2
        self.button_font = pg.font.SysFont("arial.ttf", self.button_font_size)
        self.button_active_color = (180, 170, 230)
        self.button_inactive_color = (180, 190, 180)

        # score attributes
        self._max_score = 0
        self.score_text_size = self.button_height // 2
        self.score_font = pg.font.SysFont("arial.ttf", self.score_text_size)

        # ai attributes
        self._ai_is_running = False

        self.clock = pg.time.Clock()
        self.game_display = pg.display.set_mode((self.display_width, self.display_height))
        pg.display.set_caption("2048")

        self.engine = game_engine.Engine(self.game_size)

        self.game_loop()

    @property
    def ai_is_running(self):
        return self._ai_is_running

    @ai_is_running.setter
    def ai_is_running(self, value):
        if value:
            del self.buttons["Run AI"]
            self.buttons["Stop AI"] = 2, self.stop_ai
        else:
            del self.buttons["Stop AI"]
            self.buttons["Run AI"] = 2, self.run_ai
        self._ai_is_running = value

    @property
    def score(self):
        return self.engine.score

    @property
    def max_score(self):
        self._max_score = max(self._max_score, self.score)
        return self._max_score

    def draw_scores(self):
        pr.label(self.game_display, "Max score : " + str(self.max_score),
                 (self.spacing, self.grid_pixel_size + self.spacing * 2 + self.button_height), self.score_font)
        pr.label(self.game_display, "Scores : " + str(self.score),
                 (self.spacing, self.grid_pixel_size + self.spacing * 2 + self.button_height + self.score_text_size),
                 self.score_font)

    def draw_buttons(self):
        for button_name in self.buttons.keys():
            pr.button(self.game_display, button_name,
                      self.buttons[button_name][0] * (self.spacing + self.button_width) + self.spacing,
                      self.grid_pixel_size, self.button_width,
                      self.button_height, self.button_inactive_color, self.button_active_color,
                      action=self.buttons[button_name][1],
                      font=self.button_font)

    def draw_cell(self, x, y, w, h, number):
        number = 2 ** number
        pr.aa_rounded_rect_with_text(str(number), self.game_display, (x, y, h, w), get_color(number), rad=5,
                                     font=self.cell_font)

    def draw_grid(self):
        for i, line in enumerate(self.engine.board.tolist()):
            for j, cell in enumerate(line):
                if cell:
                    self.draw_cell(j * self.cell_width + self.spacing * (j + 1),
                                   i * self.cell_height + self.spacing * (i + 1),
                                   self.cell_width, self.cell_height,
                                   cell)

    def new_game(self):
        self.engine.restart()

    def undo(self):
        self.engine.undo()

    def run_ai(self):
        # CAUTION! AI WORKS PROPERLY ONLY FOR 4 x 4 BOARD!
        if self.game_size == 4:
            self.ai_is_running = True

    def stop_ai(self):
        self.ai_is_running = False

    def game_over_loop(self):
        inactive_surface = pg.Surface((self.grid_pixel_size, self.grid_pixel_size))
        inactive_surface.set_alpha(128)
        inactive_surface.fill((255, 255, 255))
        font = pg.font.SysFont("arial.ttf", self.game_over_font_size)
        text_surf = font.render("Game over...", True, (0, 0, 0))
        text_rect = text_surf.get_rect()
        text_rect.center = (self.grid_pixel_size // 2, self.grid_pixel_size // 2)
        inactive_surface.blit(text_surf, text_rect)

        while not self.engine.is_working:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    pg.event.post(event)

            self.game_display.fill(self.main_color)
            self.draw_buttons()
            self.draw_scores()
            self.draw_grid()
            self.game_display.blit(inactive_surface, (0, 0))
            pg.display.update()
            self.clock.tick(60)

    def animation_loop(self, slides, remember=False):
        animations = []
        for slide in slides:
            animations.append(
                self.AnimatedCell(self.spacing, self.cell_speed, self.cell_height, self.cell_width, *slide))

        while any(animation.is_moving or animation.is_merging for animation in animations):
            self.game_display.fill(self.main_color)
            for animation in animations:
                if animation.is_moving:
                    animation.move()
                if animation.is_merging:
                    animation.merge()

                if not animation.is_growing:
                    self.draw_cell(animation.x, animation.y, animation.width, animation.height, animation.value)

            self.draw_buttons()
            self.draw_scores()
            if not remember:
                pg.event.get()
            pg.display.update()
            self.clock.tick(60)
        while any(animation.is_growing for animation in animations):
            self.game_display.fill(self.main_color)
            for animation in animations:
                if animation.is_growing:
                    animation.grow()

                self.draw_cell(animation.x, animation.y, animation.width, animation.height, animation.value)
            self.draw_buttons()
            self.draw_scores()

            if not remember:
                pg.event.get()

            pg.display.update()
            self.clock.tick(60)

    def game_loop(self):
        while True:
            if not self.engine.is_working:
                self.game_over_loop()
                # self.engine.restart()
            if self.ai_is_running:
                self.engine.let_ai_move()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    pg.event.post(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.animation_loop(self.engine.move(LEFT))
                    if event.key == pg.K_RIGHT:
                        self.animation_loop(self.engine.move(RIGHT))
                    if event.key == pg.K_UP:
                        self.animation_loop(self.engine.move(UP))
                    if event.key == pg.K_DOWN:
                        self.animation_loop(self.engine.move(DOWN))

            self.game_display.fill(self.main_color)
            self.draw_buttons()
            self.draw_scores()
            self.draw_grid()
            pg.display.update()
            self.clock.tick(120)


if __name__ == '__main__':
    pg.init()
    gameGUI = GameGUI(4)
