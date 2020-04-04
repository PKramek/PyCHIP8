from PyCHIP8.conf import Constants


class Screen:
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
