import numpy as np
import pygame
from pygame import display, draw

from PyCHIP8.conf import Constants, Config


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
        self.set_according_screen_size()

        self.scale = scale
        display.init()

        self.surface = display.set_mode((self.width * self.scale, self.height * self.scale), depth=8)
        self.clear()

    @property
    def mode(self) -> str:
        """
        This mode property getter return current screen mode (Normal or Extended)
        """
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

    @staticmethod
    def refresh():
        """
        Refresh image displayed on screen
        """
        display.flip()

    def clear(self):
        """
        This method is used to clear graphics memory and clear displayed screen (set color to color 0)
        """
        self.bitmap = np.zeros((self.width, self.height), dtype="int8")
        self.surface.fill(Config.SCREEN_COLORS[0])

    def scroll_down(self, number_of_lines: int):
        """
        Moves every line of bitmap down by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved down
        """
        self.bitmap = np.roll(self.bitmap, number_of_lines, axis=0)
        self.bitmap[:number_of_lines, :] = 0

    def scroll_up(self, number_of_lines):
        """
        Moves every line of bitmap up by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved up
        """
        height = self.bitmap.shape[0]
        self.bitmap = np.roll(self.bitmap, -number_of_lines, axis=0)
        self.bitmap[height - number_of_lines:, :] = 0

    def scroll_right(self):
        """
        Moves every vertical line of bitmap right by 4
        """
        self.bitmap = np.roll(self.bitmap, 4, axis=1)
        self.bitmap[:, :4] = 0

    def scroll_left(self):
        """
        Moves every vertical line of bitmap left by 4
        """
        width = self.bitmap.shape[1]
        self.bitmap = np.roll(self.bitmap, -4, axis=1)
        self.bitmap[:, width - 4:] = 0

    def disable_extended_screen(self):
        """
        This method sets screen mode to normal, sets according size and clears screen
        """
        self.mode = Constants.NORMAL_MODE
        self.set_according_screen_size()
        self.clear()

    def enable_extended_screen(self):
        """
        This method sets screen mode to extended, sets according size and clears screen
        """
        self.mode = Constants.EXTENDED_MODE
        self.set_according_screen_size()
        self.clear()

    def get_pixel(self, x: int, y: int) -> int:
        """
        Return current value (0 or 1) of pixel at position (x, y)
        :param x: x-coordinate of pixel in bitmap
        :param y: y-coordinate of pixel in bitmap
        """
        return self.bitmap[x, y]

    def draw_pixel(self, x: int, y: int, pixel: int):
        """
        Set pixel at position (x, y) to color defined in Config.SCREEN_COLORS, color is selected using value of
        pixel argument
        :param x: x-coordinate of pixel in bitmap
        :param y: y-coordinate of pixel in bitmap
        :param pixel: value of pixel (0 or 1) to be set at position (x, y)
        """
        draw.rect(self.surface, Config.SCREEN_COLORS[pixel],
                  (x * self.scale, y * self.scale, self.scale, self.scale))

    def xor_pixel_value(self, x: int, y: int, pixel: int) -> int:
        """
        This method uses XOR operation on pixel at position (x, y) and value given in pixel argument

        CHIP-8 draws pixels on the screen using XOR operation to simplify many screen related operations
        :param x: x-coordinate of pixel in bitmap
        :param y: y-coordinate of pixel in bitmap
        :param pixel: value of pixel (0 or 1), this parameter will be used in XOR operation with current pixel value

        :return: value of pixel at position (x, y) after XOR operation
        """
        self.bitmap[x, y] ^= pixel

        return self.bitmap[x, y]

    def draw_frame(self, *, scaling_method: str = "repeat"):

        """
        This method could be used in place of draw pixel method, it draws whole frames from bitmap, after scaling them
        to accurate screen size

        :param scaling_method: Method used for scaling bitmap to screen size, available methods are 'repeat' and 'kron',
         defaults to 'repeat'
        :throws ValueError: When scaling_method is not either 'repeat' or 'kron' Value error is raised
        """

        if scaling_method == "repeat":
            scaled_bitmap = np.repeat(np.repeat(self.bitmap, self.scale, axis=1), self.scale, axis=0)
        elif scaling_method == "kron":
            scaled_bitmap = np.kron(self.bitmap, (self.scale, self.scale))
        else:
            raise ValueError("Unknown scaling method")
        surface = pygame.surfarray.make_surface(scaled_bitmap)
        self.surface.blit(surface, (0, 0))
