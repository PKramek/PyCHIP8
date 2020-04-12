import argparse
import logging

import pygame

from PyCHIP8.conf import Config
from PyCHIP8.cpu import CPU
from PyCHIP8.screen import Screen

logging.basicConfig(level=logging.WARNING)
from pathlib import Path


class PyCHIP8:
    """
    Main class of the emulator
    """

    def __init__(self, path: str):
        """
        PyCHIP8 class constructor, its only purpose is to initialize CPU and Screen objects

        :param path: Path to file containing CHIP8 game or program
        """
        self.screen = Screen()
        self.cpu = CPU(self.screen)
        self.cpu.reset()

        self.rom_path = Path(path)

    def run(self):
        """
        Main method of CHIP-8 emulator
        """
        single_instruction_interval = (1000 // Config.CPU_CLOCK_SPEED)

        pygame.time.set_timer(pygame.USEREVENT, Config.TIMER_DELAY)
        pygame.display.set_caption("PyCHIP8 by Piotr Kramek")

        try:
            self.cpu.load_rom(self.rom_path)
        except FileNotFoundError:
            print("\nFile does not exist\n")
        else:
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
    parser = argparse.ArgumentParser(description='CHIP-8 emulator')
    parser.add_argument('--rom', help='Path to ROM file containing CHIP-8 game or program')
    args = parser.parse_args()

    emulator = PyCHIP8(args.rom)
    emulator.run()
