from PyCHIP8.conf import Config
from PyCHIP8.conf import Constants
from PyCHIP8.screen import Screen


class CPU:
    """"
    This class is used to emulate CHIP-8 CPU.

    CHIP-8 CPU has
        - 16 8-bit general purpose registers - Vx
        - 1 16-bit stack pointer - SP
        - 1 16-bit program counter - PC
        - 1 16-bit index register - I
        - 1 8-bit delay timer - DT
        - 1 8-bit sound timer - ST
    """

    def __init__(self, screen: Screen):
        """
        This method initializes CPU. Object of class screen is necessary to be able to operate on screen in some
        opcodes
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

    def execute_opcode(self) -> None:
        # Get next opcode from memory, opcode is 2 byte so we need two consecutive memory cells
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2

        four_oldest_bits = (self.opcode & 0xF000) >> 12

        self.opcode_lookup[four_oldest_bits]()

    def execute_leading_zero_opcodes(self):
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
        operation = self.opcode & 0x000F
        self.leading_eight_opcodes_lookup[operation]()

    def screen_scroll_up(self, number_of_lines: int):
        """"
        Opcode: 0x00BN
        Mnemonic: SCU N

        Scrolls screen up n lines ( n/2 if not in extended mode )
        """
        self.screen.scroll_up(number_of_lines)

    def screen_scroll_down(self, number_of_lines: int):
        """"
        Opcode: 0x00CN
        Mnemonic: SCD N

        Scrolls screen down n lines ( n/2 if not in extended mode )
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
        NN is stored in bits 0-11 of opcode
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

        Loads value in 8 youngest bits of opcode to register Vx
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
