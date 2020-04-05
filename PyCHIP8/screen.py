from PyCHIP8.conf import Constants


class Screen:
    def __init__(self):
        self._width = None
        self._height = None

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._height

    @width.setter
    def width(self, width):
        self._width = width

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
        # TODO Implement disable_extended_screen
        pass

    def enable_extended_screen(self):
        # TODO Implement enable_extended_screen
        pass

    def get_pixel_value(self, x_pos: int, y_pos: int):
        # TODO Implement get_pixel_value
        pass

    def draw_pixel(self, x_pos: int, y_pos: int, pixel: int):
        pass
