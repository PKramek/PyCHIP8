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

    @staticmethod
    def refresh():
        """
        Refresh image displayed on screen
        """
        display.flip()

    def clear(self):
        self.bitmap = np.zeros((self.width, self.height), dtype="int8")
        self.surface.fill(Config.SCREEN_COLORS[0])

    def scroll_down(self, number_of_lines: int):
        """
        Moves every line down by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved down
        """
        self.bitmap = np.roll(self.bitmap, number_of_lines, axis=0)
        self.bitmap[:number_of_lines, :] = 0

    def scroll_up(self, number_of_lines):
        """
        Moves every line up by a number defined in number_of_lines parameter
        :param number_of_lines: Defines number of lines each line should be moved up
        """
        height = self.bitmap.shape[0]
        self.bitmap = np.roll(self.bitmap, -number_of_lines, axis=0)
        self.bitmap[height - number_of_lines:, :] = 0

    def scroll_right(self):
        """
        Moves every vertical line right by 4
        """
        self.bitmap = np.roll(self.bitmap, 4, axis=1)
        self.bitmap[:, :4] = 0

    def scroll_left(self):
        """
        Moves every vertical line left by 4
        """
        width = self.bitmap.shape[1]
        self.bitmap = np.roll(self.bitmap, -4, axis=1)
        self.bitmap[:, width - 4:] = 0

    def disable_extended_screen(self):
        self.mode = Constants.NORMAL_MODE
        self.set_according_screen_size()
        self.clear()

    def enable_extended_screen(self):
        self.mode = Constants.EXTENDED_MODE
        self.set_according_screen_size()
        self.clear()

    def get_pixel(self, x: int, y: int) -> int:
        return self.bitmap[x, y]

    def draw_pixel(self, x: int, y: int, pixel: int):
        draw.rect(self.surface, Config.SCREEN_COLORS[pixel],
                  (x * self.scale, y * self.scale, self.scale, self.scale))

    def xor_pixel_value(self, x, y, pixel: int) -> int:
        self.bitmap[x, y] ^= pixel

        return self.bitmap[x, y]

    def draw_frame(self):
        """This method is not used, it was only used for testing purposes"""
        # scaled_bitmap = np.kron(self.bitmap, (self.scale,self.scale))
        scaled_bitmap = np.repeat(np.repeat(self.bitmap, self.scale, axis=1), self.scale, axis=0)

        surface = pygame.surfarray.make_surface(scaled_bitmap)
        self.surface.blit(surface, (0, 0))
