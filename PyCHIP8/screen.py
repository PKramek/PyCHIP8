from typing import Tuple

from pygame import display, draw
from pygame.constants import HWSURFACE, DOUBLEBUF

from PyCHIP8.conf import Constants, Config

import logging


class Screen:
    """
    This class represents screen on which emulator will display images
    """

    def __init__(self, mode: str = Constants.NORMAL_MODE, scale: int = 10):
        """
        This method is used to set screen related fields

        :param mode: Defines mode (normal or extended) in which screen is initialized, defaults to normal
        :param scale: Defines screen size multiplier, this parameter is used to define displayed screen size in relation
                        to original CHIP-8 screen size, defaults to 10
        """
        self._mode = None
        self._width = None
        self._height = None
        self.mode = mode
        self.scale = scale

        self.set_according_screen_size()

        display.init()
        self.surface = display.set_mode((self.width, self.height), HWSURFACE | DOUBLEBUF, 8)
        self.clear()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """
        This mode property setter checks if given mode is one of modes defined in Constants class
        :param mode: Value used to define what mode should screen be in (normal or extended)
        :throws ValueError: When given mode is not equal to either extended or normal mode defined in Config class
        """
        correct_modes = [Constants.NORMAL_MODE, Constants.EXTENDED_MODE]
        if mode in correct_modes:
            self._mode = mode
        else:
            raise ValueError("Mode must be either extended or normal")

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: int):
        """
        This method sets screen width to value given in parameter multiplied by scale value
        :param width: Defines screen width, value given in this parameter will be multiplied by scale factor and then
        assigned to width field of screen class
        """
        self._width = width * self.scale

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: int):
        """
        This method sets screen height to value given in parameter multiplied by scale value
        :param height: Defines screen width, value given in this parameter will be multiplied by scale factor and then
        assigned to height field of screen class
        """
        self._height = height * self.scale

    def set_according_screen_size(self):
        """
        This method is used to set screen size according to current screen mode
        """
        if self.mode == Constants.NORMAL_MODE:
            self.width = Config.SCREEN_WIDTH_NORMAL
            self.height = Config.SCREEN_HEIGHT_NORMAL
        else:
            self.width = Config.SCREEN_WIDTH_EXTENDED
            self.height = Config.SCREEN_HEIGHT_EXTENDED

        self.update_screen()

    def refresh(self):
        """
        Refresh image displayed on screen
        """
        display.flip()

    @staticmethod
    def update_screen():
        display.quit()
        display.init()

    def clear(self):
        self.surface.fill(Config.SCREEN_COLORS[0])

    def scroll_down(self, number_of_lines: int):
        """
        Moves every line down by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved down
        """
        # TODO refactor height and width to not be calculated each time this method is called
        height = self.height / self.scale
        width = self.width / self.scale

        for y in range(height - number_of_lines, number_of_lines, -1):
            for x in range(width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(number_of_lines):
            for x in range(width):
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    Config.SCREEN_COLORS[0]
                )

        self.refresh()

    def scroll_up(self, number_of_lines):
        """
        Moves every line up by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved up
        """
        height = self.height / self.scale
        width = self.width / self.scale

        for y in range(number_of_lines, height):
            for x in range(width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x,
                    y - number_of_lines,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(height - number_of_lines, height):
            for x in range(width):
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    Config.SCREEN_COLORS[0]
                )

        self.refresh()

    def scroll_right(self):
        """
        Moves every vertical line right by 4
        """
        height = self.height / self.scale
        width = self.width / self.scale

        for y in range(height):
            for x in range(width - 4, -1, -1):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x + 4,
                    y,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(height):
            for x in range(4):
                self.draw_pixel(
                    x,
                    y,
                    Config.SCREEN_COLORS[0]
                )

        self.refresh()

    def scroll_left(self):
        """
        Moves every vertical line left by 4
        """
        height = self.height / self.scale
        width = self.width / self.scale

        for y in range(height):
            for x in range(4, width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x - 4,
                    y,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(height):
            for x in range(width - 4, width):
                self.draw_pixel(
                    x,
                    y,
                    Config.SCREEN_COLORS[0]
                )

        self.refresh()

    def disable_extended_screen(self):
        self.mode = Constants.NORMAL_MODE

    def enable_extended_screen(self):
        self.mode = Constants.EXTENDED_MODE

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        return self.surface.get_at((x * self.scale, y * self.scale))

    def draw_pixel(self, x: int, y: int, pixel: Tuple[int, int, int, int]):
        width = height = self.scale
        draw.rect(self.surface, pixel,
                  (x * self.scale, y * self.scale, width, height))

    def get_pixel_value(self, x, y) -> int:
        pixel = self.get_pixel(x, y)
        logging.info("index:{} {}".format(pixel, Config.SCREEN_COLORS))

        return Config.SCREEN_COLORS.index(pixel)
