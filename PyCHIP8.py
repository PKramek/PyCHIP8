import logging

import pygame

from PyCHIP8.conf import Config
from PyCHIP8.cpu import CPU
from PyCHIP8.screen import Screen

logging.basicConfig(level=logging.WARNING)


class PyCHIP8:
    def __init__(self):
        self.screen = Screen()
        self.cpu = CPU(self.screen)
        self.cpu.reset()

    def run(self):
        single_instruction_interval = (1000 // Config.CPU_CLOCK_SPEED)

        pygame.time.set_timer(pygame.USEREVENT, Config.TIMER_DELAY)
        pygame.display.set_caption("PyCHIP8 by Piotr Kramek")

        self.cpu.load_rom("ROMS\Breakout.ch8")
        while self.cpu.running:
            pygame.time.wait(single_instruction_interval)

            self.cpu.execute_opcode()
            self.screen.refresh()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cpu.exit()
                if event.type == pygame.USEREVENT:
                    self.cpu.decrement_values_in_timers()


if __name__ == "__main__":
    emulator = PyCHIP8()
    emulator.run()
