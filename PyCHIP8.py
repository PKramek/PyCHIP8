import logging

import pygame

from PyCHIP8.conf import Config
from PyCHIP8.cpu import CPU
from PyCHIP8.screen import Screen


class PyCHIP8:
    def __init__(self):
        self.screen = Screen()
        self.cpu = CPU(self.screen)

    def run(self):

        pygame.time.set_timer(pygame.USEREVENT, Config.TIMER_DELAY)
        single_instruction_interval = (1000 // Config.CPU_CLOCK_SPEED)
        logging.debug("Single CPU cycle interval: {}".format(single_instruction_interval))

        self.cpu.load_rom("ROMS\TETRIS")
        while self.cpu.running:

            pygame.time.wait(single_instruction_interval)
            self.cpu.execute_opcode()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cpu.exit()
                if event.type == pygame.USEREVENT:
                    self.cpu.decrement_values_in_timers()


            self.screen.refresh()

if __name__ == "__main__":
    emulator = PyCHIP8()
    emulator.run()
