from random import randint

import pygame
from pygame import key, KEYDOWN

from PyCHIP8.conf import Config
from PyCHIP8.conf import Constants
from PyCHIP8.screen import Screen


class CPU:
    """"
    This class is used to emulate CHIP-8 CPU.
    """

    class UnknownInstructionException(Exception):
        """
        Inner class that extends Exception and is used to throw exception where emulator tries to execute
        not known instruction
        """

        def __init__(self, opcode):
            Exception.__init__(self, "Unknown instruction {}".format(opcode))

    def __init__(self, screen: Screen):
        """
        This method initializes CPU. Object of class screen is necessary to be able to operate on screen in some
        opcodes

        :param screen: Screen class object on which emulator will draw pixels
        """
        self.screen = screen
        self.opcode = 0
        self.memory = bytearray(Config.MAX_MEMORY)
        self.mode = Constants.NORMAL_MODE

        self.pc = 0
        self.sp = 0
        self.i = 0
        self.v = []

        self.timer_dt = 0
        self.timer_st = 0

        self.running = False

        # Flag used to define if sound should be played
        self.sound_flag = True

        # Python dictionary is used in place of if-else statements when deciding what method to call
        # In most cases opcodes are determined by four oldest bits and in this dict only those bits are used
        self.opcode_lookup = {
            0x0: self.execute_leading_zero_opcodes,
            0x1: self.jump_to_address,
            0x2: self.jump_to_subroutine,
            0x3: self.skip_if_register_equals_value,
            0x4: self.skip_if_register_not_equals_value,
            0x5: self.skip_if_register_equal_other_register,
            0x6: self.move_value_to_register,
            0x7: self.add_value_to_register,
            0x8: self.execute_leading_eight_opcodes,
            0x9: self.skip_if_register_not_equal_other_register,
            0xA: self.move_value_to_index,
            0xB: self.jump_to_address_plus_v_zero,
            0xC: self.generate_random_number,
            0xD: self.draw_sprite,
            0xE: self.execute_leading_e_opcodes,

        }

        self.leading_zero_opcodes_lookup = {
            0xE0: self.clear_screen,
            0xEE: self.return_from_subroutine,
            0xFB: self.screen_scroll_right,
            0xFC: self.screen_scroll_left,
            0xFD: self.exit,
            0xFE: self.disable_extended_screen,
            0xFF: self.enable_extended_screen
        }

        self.leading_eight_opcodes_lookup = {
            0x0: self.move_register_to_register,
            0x1: self.register_logical_or_register,
            0x2: self.register_logical_and_register,
            0x3: self.register_logical_xor_register,
            0x4: self.add_register_to_register,
            0x5: self.subtract_register_from_register,
            0x6: self.shift_register_right,
            0x7: self.negative_subtract_register_from_register,
            0xE: self.shift_register_left
        }

        self.leading_e_opcodes_lookup = {
            0x9E: self.skip_if_key_is_pressed,
            0xA1: self.skip_if_key_is_not_pressed
        }

        self.leading_f_opcodes_lookup = {
            0x07: self.move_delay_to_register,
            0x0A: self.wait_for_keypress,
            0x15: self.move_register_to_delay_timer,
            0x18: self.move_register_to_sound_timer,
            0x1E: self.add_register_to_index,
            0x29: self.move_sprite_address_to_index,
            0x30: self.move_extended_sprite_address_to_index,
            0x33: self.store_bcd_in_memory,
            0x55: self.store_registers_in_memory,
            0x65: self.read_registers_from_memory
        }

    def reset(self):
        """
        Resets the CPU by reseting all registers and timers to its starting values
        """
        self.v = bytearray(Config.NUMBER_OF_REGISTERS)
        self.pc = Config.PROGRAM_COUNTER
        self.sp = Config.STACK_POINTER
        self.i = 0
        self.timer_dt = 0
        self.timer_st = 0

    def decrement_values_in_timers(self):
        """
        Subtracts one from timers if values stored in them are bigger than zero
        """

        if self.timer_st > 0:
            self.timer_st -= 1

        if self.timer_dt > 0:
            self.timer_dt -= 1

    def load_rom(self, rom_filename: str, address: int = Config.PROGRAM_COUNTER):
        """"
        Loads the rom data to emulator memory

        :param rom_filename: path to rom file
        :param address: address at which the rom data will begin to be stored in emulator memory
        """
        rom_data = open(rom_filename, 'rb').read()
        for index, data in enumerate(rom_data):
            self.memory[address + index] = data

    def execute_opcode(self):
        """"
        This method is used to execute next instruction, which opcode is stored in memory at locations PC and PC+1
        Opcodes are two byte wide, but CHIP8 memory consist of 1 byte memory cells and that`s why we need two
        consecutive memory cells. Opcodes can be distinguished by only four oldest bits (in most cases)

        :throws UnknownInstructionException: when there was no opcode defined in opcode lookup dictionaries
        """
        # Get next opcode from memory, opcode is 2 byte so we need two consecutive memory cells
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2

        four_oldest_bits = (self.opcode & 0xF000) >> 12

        try:
            self.opcode_lookup[four_oldest_bits]()
        except KeyError:
            raise self.UnknownInstructionException(self.opcode)

    def execute_leading_zero_opcodes(self):
        """"
        This method is used to execute instructions, which opcodes hex representation start with 0
        """
        # To remove redundant scroll down and up methods we check if there is C or B on second youngest digit in opcode
        operation = self.opcode & 0x00F0
        if operation == 0x00B0:
            number_of_lines = self.opcode & 0x000F
            self.screen_scroll_up(number_of_lines)
        if operation == 0x00C0:
            number_of_lines = self.opcode & 0x000F
            self.screen_scroll_down(number_of_lines)

        operation = self.opcode & 0x00FF
        self.leading_zero_opcodes_lookup[operation]()

    def execute_leading_eight_opcodes(self):
        """"
        This method is used to execute instructions, which opcodes hex representation start with 8,
        Those instructions are distinguished by four youngest bits
        """
        operation = self.opcode & 0x000F
        self.leading_eight_opcodes_lookup[operation]()

    def execute_leading_e_opcodes(self):
        """"
        This method is used to execute instructions, which opcodes hex representation start with E,
        Those instructions are distinguished by eight youngest bits
        """
        operation = self.opcode & 0x00FF
        self.leading_e_opcodes_lookup[operation]()

    def screen_scroll_up(self, number_of_lines: int):
        """"
        Opcode: 0x00BN
        Mnemonic: SCU N

        Scrolls screen up n lines ( n/2 if not in extended mode )

        :param number_of_lines: number of lines to scroll screen up
        """
        self.screen.scroll_up(number_of_lines)

    def screen_scroll_down(self, number_of_lines: int):
        """"
        Opcode: 0x00CN
        Mnemonic: SCD N

        Scrolls screen down n lines ( n/2 if not in extended mode )
        :param number_of_lines: number of lines to scroll screen down
        """
        self.screen.scroll_down(number_of_lines)

    def clear_screen(self):
        """"
        Opcode: 0x00E0
        Mnemonic: CLS

        Clears screen memory
        """
        self.screen.clear()

    def return_from_subroutine(self):
        """"
        Opcode: 0x00EE
        Mnemonic: RET

        Return from subroutine by subtracting 1 from SP and setting PC to value from memory pointed to by SP
        """
        self.sp -= 2
        self.pc = (self.memory[self.sp + 1] << 8) | self.memory[self.sp]

    def screen_scroll_right(self):
        """"
        Opcode: 0x00FB
        Mnemonic: SCR

        Scrolls screen right 4 lines ( 2 if not in extended mode )
        """
        self.screen.scroll_right(self.mode)

    def screen_scroll_left(self):
        """"
        Opcode: 0x00FC
        Mnemonic: SCL

        Scrolls screen left 4 lines ( 2 if not in extended mode )
        """
        self.screen.scroll_left(self.mode)

    def exit(self):
        """"
        Opcode: 0x00FD
        Mnemonic: EXIT

        Exits Emulator
        """
        self.running = False

    def disable_extended_screen(self):
        """"
        Opcode: 0x00FE
        Mnemonic: LOW

        Sets screen to low resolution mode (64 x 32)
        """
        self.mode = Constants.NORMAL_MODE
        self.screen.disable_extended_screen()

    def enable_extended_screen(self):
        """"
        Opcode: 0x00FF
        Mnemonic: HIGH

        Sets screen to high resolution mode (128 x 64)
        """
        self.mode = Constants.EXTENDED_MODE
        self.screen.enable_extended_screen()

    def jump_to_address(self):
        """"
        Opcode: 0x1NNN
        Mnemonic: JP NNN

        Sets PC to value defined in 12 youngest bits of Opcode
        """
        self.pc = self.opcode & 0x0FFF

    def jump_to_subroutine(self):
        """"
        Opcode: 0x2NNN
        Mnemonic: CALL NNN

        Saves current context ( value of PC ) in memory and sets PC to value defined in 12 youngest bits of Opcode
        """
        self.memory[self.sp] = self.pc & 0x00FF
        self.pc += 1
        self.memory[self.sp] = (self.pc & 0xFF00) >> 8
        self.pc += 1

        self.pc = self.opcode & 0x0FFF

    def skip_if_register_equals_value(self):
        """"
        Opcode: 0x3XNN
        Mnemonic: SE VX, NN

        Skips next instruction if value in register Vx is equal to value in 8 youngest bits of opcode
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        if self.v[x] == self.opcode & 0x00FF:
            self.pc += 2

    def skip_if_register_not_equals_value(self):
        """"
        Opcode: 0x4XNN
        Mnemonic: SNE VX, NN

        Skips next instruction if value in register Vx is not equal to value in 8 youngest bits of opcode
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        if self.v[x] != self.opcode & 0x00FF:
            self.pc += 2

    def skip_if_register_equal_other_register(self):
        """"
        Opcode: 0x5XY0
        Mnemonic: SE VX, VY

        Skips next instruction if value in register Vx is equal to value in register Vy
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2

    def move_value_to_register(self):
        """"
        Opcode: 0x6XNN
        Mnemonic: LD VX, NN

        Loads value stored in 8 youngest bits of opcode to register Vx
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.v[x] = (self.opcode & 0x00FF)

    def add_value_to_register(self):
        """"
        Opcode: 0x7XNN
        Mnemonic: ADD VX, NN

        Adds value in 8 youngest bits of opcode to register Vx
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.v[x] += (self.opcode & 0x00FF)

    def move_register_to_register(self):
        """"
        Opcode: 0x8XY0
        Mnemonic: LD VX, VY

        Loads value from register Vy to register Vx
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] = self.v[y]

    def register_logical_or_register(self):
        """"
        Opcode: 0x8XY1
        Mnemonic: OR VX, VY

        Sets value in register Vx to result of performing logical OR on Vx and Vy registers
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] |= self.v[y]

    def register_logical_and_register(self):
        """"
        Opcode: 0x8XY2
        Mnemonic: AND VX, VY

        Sets value in register Vx to result of performing logical AND on Vx and Vy registers
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] &= self.v[y]

    def register_logical_xor_register(self):
        """"
        Opcode: 0x8XY3
        Mnemonic: XOR VX, VY

        Sets value in register Vx to result of performing logical XOR on Vx and Vy registers
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] ^= self.v[y]

    def add_register_to_register(self):
        """"
        Opcode: 0x8XY4
        Mnemonic: ADD VX, VY

        Sets value in register Vx to sum of values in registers Vx and Vy, VF is set to 1 if there is overflow
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        sum = self.v[x] + self.v[y]

        if sum > 255:
            self.v[x] = sum - 256
            self.v[0xF] = 1
        else:
            self.v[x] = sum
            self.v[0xF] = 0

    def subtract_register_from_register(self):
        """"
        Opcode: 0x8XY5
        Mnemonic: SUB VX, VY

        Sets value in register Vx to result of subtraction of values in registers Vx and Vy,
        VF is set to 1 if there is borrow not generated

        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        if self.v[x] > self.v[y]:
            self.v[x] -= self.v[y]
            self.v[0xF] = 1
        else:
            self.v[x] -= self.v[y] - 256
            self.v[0xF] = 0

    def shift_register_right(self):
        """"
        Opcode: 0x8XY6
        Mnemonic: SHR VX

        Stores the least significant bit of Vx in VF and shifts Vx to right once*
        x is stored in bits 8-11 of opcode

        *In original CHIP-8 this instruction would store shifted right value of Vy in Vx, but every emulator and rom
        today uses behavior described above
        """
        x = (self.opcode & 0x0F00) >> 8

        self.v[0xF] = (self.v[x] & 0x1)
        self.v[x] = self.v[x] >> 1

    def negative_subtract_register_from_register(self):
        """"
        Opcode: 0x8XY8
        Mnemonic: SUBN VX, VY

        Sets value in register Vx to result of subtraction of values in registers Vy and Vx,
        VF is set to 1 if there is borrow not generated

        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        if self.v[y] > self.v[x]:
            self.v[x] = self.v[y] - self.v[x]
            self.v[0xF] = 1
        else:
            self.v[x] = self.v[y] + 256 - self.v[x]
            self.v[0xF] = 0

    def shift_register_left(self):
        """"
        Opcode: 0x8XYE
        Mnemonic: SHL VX

        Stores the most significant bit of Vx in VF and shifts Vx to left once*
        x is stored in bits 8-11 of opcode

        *In original CHIP-8 this instruction would store shifted left value of Vy in Vx, but every emulator and rom
        today uses behavior described above
        """
        x = (self.opcode & 0x0F00) >> 8

        self.v[0xF] = (self.v[x] & 0x80) >> 8
        self.v[x] = self.v[x] << 1

    def skip_if_register_not_equal_other_register(self):
        """"
        Opcode: 0x9XY0
        Mnemonic: SNE VX, VY

        Skips next instruction if value in register Vx is equal to value in register Vy
        x is stored in bits 8-11 of opcode
        y is stored in bits 4-7 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2

    def move_value_to_index(self):
        """"
        Opcode: 0xANNN
        Mnemonic: LD I, NNN

        Loads value stored in 12 youngest bits of opcode to index register
        """
        self.i = (self.opcode & 0x0FFF)

    def jump_to_address_plus_v_zero(self):
        """"
        Opcode: 0xBNNN
        Mnemonic: JP V0, NNN

        Sets PC to value defined in 12 youngest bits of Opcode plus value stored in register V0
        """
        self.pc = self.v[0] + (self.opcode & 0x0FFF)

    def generate_random_number(self):
        """"
        Opcode: 0xCXNN
        Mnemonic: RND VX, NN

        Sets value in register Vx as a result of logical AND operation between random number from range (0, 255) and
        value stored in 8 youngest bits of opcode
        """
        x = (self.opcode & 0x0F00) >> 8

        self.v[x] = (self.opcode & 0x00FF) & randint(0, 255)

    def draw_sprite(self):
        """"
        Opcode: 0xDXYN
        Mnemonic: DRW VX, VY, N

        Draws a sprite at coordinate (VX, VY) that has width of 8 pixels (16 pixels in extended mode)
        and height of N pixels. Each horizontal line is read from memory
        location pointed in I register plus number of line
        """
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        n = (self.opcode & 0x000F)

        self.v[0xF] = 0

        num_of_bytes = 1
        if self.mode == Constants.EXTENDED_MODE:
            num_of_bytes = 2

        for horizontal_line_num in range(n):

            for b in range(num_of_bytes):

                # Byte describing pixels is encoded as int but we need binary representation of that number
                pixels = bin(self.memory[self.i + horizontal_line_num + b])[2:].zfill(8)
                # In CHIP-8 when sprite does not fit on screen we draw the rest of it on the opposite side of screen
                y_pos = (y + horizontal_line_num) % self.screen.height

                for vertical_line_num in range(8):

                    x_pos = (x + vertical_line_num + b * 8) % self.screen.width
                    pixel = int(pixels[x_pos])
                    current_pixel = self.screen.get_pixel_value(x_pos, y_pos)

                    if pixel == current_pixel:
                        self.v[0xF] = 1

                    self.screen.draw_pixel(x_pos, y_pos, pixel)

        self.screen.refresh()

    def skip_if_key_is_pressed(self):
        """"
        Opcode: 0xEX9E
        Mnemonic: SKP Vx

        Skips next instruction if key specified in register Vx is pressed
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        key_in_vx = self.v[x]
        pressed_keys = key.get_pressed()
        if pressed_keys[Config.KEY_MAPPING[key_in_vx]]:
            self.pc += 2

    def skip_if_key_is_not_pressed(self):
        """"
        Opcode: 0xEXA1
        Mnemonic: SKNP Vx

        Skips next instruction if key specified in register Vx is pressed
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        key_in_vx = self.v[x]
        pressed_keys = key.get_pressed()
        if not pressed_keys[Config.KEY_MAPPING[key_in_vx]]:
            self.pc += 2

    def move_delay_to_register(self):
        """"
        Opcode: 0xFX07
        Mnemonic: LD Vx, DT

        Sets value in register Vx to value from delay timer
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.v[x] = self.timer_dt

    def wait_for_keypress(self):
        """"
        Opcode: 0xFX0A
        Mnemonic: LD Vx, K

        All execution stops until key is pressed, then the value of that key is stored in Vx
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8

        key_pressed = False
        while not key_pressed:
            event = pygame.event.wait()
            if event.type == KEYDOWN:
                pressed_keys = key.get_pressed()

                for key_address, key_value in Config.KEY_MAPPING.items():
                    if pressed_keys[key_value]:
                        self.v[x] = key_address
                        key_pressed = True
                        break

    def move_register_to_delay_timer(self):
        """"
        Opcode: 0xFX15
        Mnemonic: LD DT, Vx

        Sets value in delay timer to value from register Vx
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.timer_dt = self.v[x]

    def move_register_to_sound_timer(self):
        """"
        Opcode: 0xFX18
        Mnemonic: LD ST, Vx

        Sets value in sound timer to value from register Vx
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.timer_st = self.v[x]

    def add_register_to_index(self):
        """"
        Opcode: 0xFX1E
        Mnemonic: ADD I, Vx

        Sets value in index register I to sum of values in registers Vx and I
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.i += self.v[x]

    def move_sprite_address_to_index(self):
        """"
        Opcode: 0xFX29
        Mnemonic: LD F, Vx

        Sets value in index register I to address of the sprite for hex character specified in Vx.
        Each character 0-F is represented as 5 bytes so to get specific character address we need to multiply
        value stored in Vx by 5
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.i = self.v[x] * 5

    def move_extended_sprite_address_to_index(self):
        """"
        Opcode: 0xFX30
        Mnemonic: LDH F, Vx

        Sets value in index register I to address of the sprite for decimal character specified in Vx.
        Each character is represented as 10 bytes so to get specific character address we need to multiply
        value stored in Vx by 10
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        self.i = self.v[x] * 10

    def store_bcd_in_memory(self):
        """"
        Opcode: 0xFX33
        Mnemonic: LD B, Vx

        Stores BCD representation of value in register Vx in memory. Hundreds are stored at addres pointed to in I,
        tens are stored at I + 1 and ones are stored at addres I+2
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8
        value = str(self.v[x]).zfill(3)

        self.memory[self.i] = int(value[0])
        self.memory[self.i + 1] = int(value[1])
        self.memory[self.i + 2] = int(value[2])

    def store_registers_in_memory(self):
        """"
        Opcode: 0xFX55
        Mnemonic: LD [I], Vx

        Stores registers V0 - VX in memory starting at position pointed to in index register i, every consecutive
        register is stored in next memory cell
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8

        for i in range(x + 1):
            self.memory[self.i + i] = self.v[i]

    def read_registers_from_memory(self):
        """"
        Opcode: 0xFX65
        Mnemonic: LD Vx, [I]

        Sets values in registers V0 - VX with values stored in memory starting at position pointed to in index register,
        every consecutive value is stored in next memory cell
        x is stored in bits 8-11 of opcode
        """
        x = (self.opcode & 0x0F00) >> 8

        for i in range(x + 1):
            self.v[i] = self.memory[self.i + i]
