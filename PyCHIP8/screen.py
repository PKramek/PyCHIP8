from PyCHIP8.conf import Constants, Config


class Screen:
    """
    This class represents screen on which emulator will display images
    """

    def __init__(self, mode: str = Constants.NORMAL_MODE, scale: int = 1):
        """
        This method is used to set screen related fields

        :param mode: Defines mode (normal or extended) in which screen is initialized
        :param scale: Defines screen size multiplier, this parameter is used to define displayed screen size in relation
                        to original CHIP-8 screen size
        """
        self._mode = None
        self._width = None
        self._height = None
        self.mode = mode
        self.scale = scale

        self.set_according_screen_size()

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
        This method sets screen width to value given is parameter multiplied by scale value
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
        This method sets screen height to value given is parameter multiplied by scale value
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
        elif self.mode == Constants.EXTENDED_MODE:
            self.width = Config.SCREEN_WIDTH_EXTENDED
            self.height = Config.SCREEN_HEIGHT_EXTENDED

    def refresh(self):
        pass

    def scroll_down(self, number_of_lines: int):
        # TODO Implement scroll_down
        pass

    def scroll_up(self, number_of_lines):
        # TODO Implement scroll_up
        pass

    def clear(self):
        # TODO Implement clear
        pass

    def scroll_right(self, mode: str):
        # TODO Implement scroll_right
        number_of_pixels = 2
        if mode == Constants.EXTENDED_MODE:
            number_of_pixels = 4

    def scroll_left(self, mode: str):
        # TODO Implement scroll_left
        number_of_pixels = 2
        if mode == Constants.EXTENDED_MODE:
            number_of_pixels = 4

    def disable_extended_screen(self):
        self.mode = Constants.NORMAL_MODE

    def enable_extended_screen(self):
        self.mode = Constants.EXTENDED_MODE

    def get_pixel_value(self, x_pos: int, y_pos: int):
        # TODO Implement get_pixel_value
        pass

    def draw_pixel(self, x_pos: int, y_pos: int, pixel: int):
        pass
