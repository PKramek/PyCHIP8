from typing import Tuple

from pygame import display, draw
from pygame.constants import HWSURFACE, DOUBLEBUF

from PyCHIP8.conf import Constants, Config
import numpy as np

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

        self.mode = mode
        self.scale = scale
        display.init()

        self.set_according_screen_size()
        self.surface = display.set_mode((self.width * self.scale, self.height * self.scale), HWSURFACE | DOUBLEBUF, 8)
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

    def refresh(self):
        """
        Refresh image displayed on screen
        """
        display.flip()

    def clear(self):
        self.surface.fill(Config.SCREEN_COLORS[0])

    def scroll_down(self, number_of_lines: int):
        """
        Moves every line down by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved down
        """
        for y in range(self.height - number_of_lines, number_of_lines, -1):
            for x in range(self.width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(number_of_lines):
            for x in range(self.width):
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    Config.SCREEN_COLORS[0]
                )


    def scroll_up(self, number_of_lines):
        """
        Moves every line up by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved up
        """
        for y in range(number_of_lines, self.height):
            for x in range(self.width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x,
                    y - number_of_lines,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(self.height - number_of_lines, self.height):
            for x in range(self.width):
                self.draw_pixel(
                    x,
                    y + number_of_lines,
                    Config.SCREEN_COLORS[0]
                )


    def scroll_right(self):
        """
        Moves every vertical line right by 4
        """
        for y in range(self.height):
            for x in range(self.width - 4, -1, -1):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x + 4,
                    y,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(self.height):
            for x in range(4):
                self.draw_pixel(
                    x,
                    y,
                    Config.SCREEN_COLORS[0]
                )


    def scroll_left(self):
        """
        Moves every vertical line left by 4
        """
        for y in range(self.height):
            for x in range(4, self.width):
                pixel_color = self.get_pixel(x, y)
                self.draw_pixel(
                    x - 4,
                    y,
                    pixel_color
                )

        # Fill remaining lines with color zero
        for y in range(self.height):
            for x in range(self.width - 4, self.width):
                self.draw_pixel(
                    x,
                    y,
                    Config.SCREEN_COLORS[0]
                )


    def disable_extended_screen(self):
        self.mode = Constants.NORMAL_MODE
        self.set_according_screen_size()

    def enable_extended_screen(self):
        self.mode = Constants.EXTENDED_MODE
        self.set_according_screen_size()

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        color = self.surface.get_at((x * self.scale, y * self.scale))
        return color

    def draw_pixel(self, x: int, y: int, pixel: Tuple[int, int, int, int]):
        width = height = self.scale
        draw.rect(self.surface, pixel,
                  (x * self.scale, y * self.scale, width, height))

    def get_pixel_value(self, x, y) -> int:
        pixel = self.get_pixel(x, y)
        if pixel == Config.SCREEN_COLORS[0]:
            return 0
        return 1
