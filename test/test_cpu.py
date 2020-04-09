from unittest import mock
from unittest.mock import Mock

import pytest

from PyCHIP8.conf import Config, Constants
from PyCHIP8.cpu import CPU


@pytest.fixture
def cpu():
    screen_mock = Mock()
    return CPU(screen_mock)


@pytest.fixture
def fontset_bytearray() -> bytearray:
    return bytearray([
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ])


def test_reset(cpu, fontset_bytearray):
    cpu.reset()
    assert cpu.v == bytearray(Config.NUMBER_OF_REGISTERS)
    assert cpu.pc == Config.PROGRAM_COUNTER
    assert cpu.sp == Config.STACK_POINTER
    assert cpu.timer_dt == 0
    assert cpu.timer_st == 0

    fontset_size = len(fontset_bytearray)
    assert cpu.memory[fontset_size:] == bytearray(Config.MAX_MEMORY - fontset_size)
    assert cpu.memory[:fontset_size] == fontset_bytearray


def test_decrement_values_in_timers_should_decrement_value_if_non_zero(cpu):
    cpu.timer_dt = 1
    cpu.timer_st = 1

    cpu.decrement_values_in_timers()

    assert cpu.timer_dt == 0
    assert cpu.timer_st == 0


def test_decrement_values_in_timers_should_not_decrement_value_if_zero(cpu):
    assert cpu.timer_dt == 0
    assert cpu.timer_st == 0

    cpu.decrement_values_in_timers()

    assert cpu.timer_dt == 0
    assert cpu.timer_st == 0


def test_rom_load(cpu):
    rom_filename = "test/test.ch8"
    index_value = cpu.i

    with open(rom_filename, 'rb') as opened_file:
        rom_data = open(rom_filename, 'rb').read()

        data_size = len(rom_data)

        starting_address = 0
        cpu.load_rom(rom_filename, starting_address)

        assert cpu.memory[index_value + starting_address: index_value + starting_address + data_size] == rom_data


def test_load_fontset(cpu, fontset_bytearray):
    cpu.load_fontset()

    fontset_size = len(fontset_bytearray)
    assert cpu.memory[fontset_size:] == bytearray(Config.MAX_MEMORY - fontset_size)
    assert cpu.memory[:fontset_size] == fontset_bytearray


def test_screen_scroll_up(cpu):
    cpu.screen = Mock()
    cpu.screen.scroll_up = Mock()

    num = 5
    cpu.screen_scroll_up(num)

    cpu.screen.scroll_up.assert_called_with(num)


def test_screen_scroll_down(cpu):
    cpu.screen = Mock()
    cpu.screen.scroll_down = Mock()

    num = 5
    cpu.screen_scroll_down(num)

    cpu.screen.scroll_down.assert_called_with(num)


def test_clear_screen(cpu):
    cpu.screen = Mock()
    cpu.screen.clear = Mock()

    cpu.clear_screen()

    cpu.screen.clear.assert_called_once()


def test_return_from_subroutine(cpu):
    for addr in range(0x200, 0xFFFF + 1):
        cpu.memory[cpu.sp] = addr & 0x00FF
        cpu.memory[cpu.sp + 1] = (addr & 0xFF00) >> 8
        cpu.sp += 2
        cpu.pc = 0
        cpu.return_from_subroutine()
        assert cpu.pc == addr


def test_screen_scroll_right(cpu):
    cpu.screen = Mock()
    cpu.screen.scroll_right = Mock()

    cpu.screen_scroll_right()

    cpu.screen.scroll_right.assert_called_once()


def test_screen_scroll_left(cpu):
    cpu.screen = Mock()
    cpu.screen.scroll_left = Mock()

    cpu.screen_scroll_left()

    cpu.screen.scroll_left.assert_called_once()


def test_exit(cpu):
    assert cpu.running is True
    cpu.exit()
    assert cpu.running is False


def test_disable_extended_screen(cpu):
    cpu.mode = Constants.EXTENDED_MODE
    cpu.screen.disable_extended_screen = Mock()

    cpu.disable_extended_screen()

    assert cpu.mode == Constants.NORMAL_MODE
    cpu.screen.disable_extended_screen.assert_called_once()


def test_enable_extended_screen(cpu):
    cpu.mode = Constants.NORMAL_MODE
    cpu.screen.enable_extended_screen = Mock()

    cpu.enable_extended_screen()

    assert cpu.mode == Constants.EXTENDED_MODE
    cpu.screen.enable_extended_screen.assert_called_once()


def test_jump_to_address(cpu):
    for addr in range(0x200, 0xFFF + 1):
        cpu.opcode = (0x1 << 12) | addr
        cpu.pc = 0
        cpu.jump_to_address()
        assert cpu.pc == addr


def test_jump_to_subroutine(cpu):
    for addr in range(0x200, 0xFFF + 1):
        starting_pc_addr = 0x200
        cpu.opcode = (0x2 << 12) | addr
        cpu.sp = 0
        cpu.pc = starting_pc_addr
        cpu.jump_to_subroutine()
        assert cpu.pc == addr
        assert cpu.memory[cpu.sp - 2] == starting_pc_addr & 0x00FF
        assert cpu.memory[cpu.sp - 1] == (starting_pc_addr & 0xFF00) >> 8


def test_skip_if_register_equals_value_should_skip_if_value_equals_register(cpu):
    for addr in range(0xFF + 1):
        cpu.v[0] = addr
        cpu.opcode = ((0x3 << 12) | (0 << 8) | addr)
        cpu.pc = 0

        cpu.skip_if_register_equals_value()

        assert cpu.pc == 2


def test_skip_if_register_equals_value_should_not_skip_if_value_not_equals_register(cpu):
    for addr in range(1, 0xFF + 1):
        cpu.v[0] = addr - 1
        cpu.opcode = ((0x3 << 12) | (0 << 8) | addr)
        cpu.pc = 0

        cpu.skip_if_register_equals_value()

        assert cpu.pc == 0


def test_skip_if_register_not_equals_value_should_skip_if_value_not_equals_register(cpu):
    for addr in range(1, 0xFF + 1):
        cpu.v[0] = addr - 1
        cpu.opcode = ((0x3 << 12) | (0 << 8) | addr)
        cpu.pc = 0

        cpu.skip_if_register_not_equals_value()

        assert cpu.pc == 2


def test_skip_if_register_not_equals_value_should_not_skip_if_value_equals_register(cpu):
    for addr in range(1, 0xFF + 1):
        cpu.v[0] = addr
        cpu.opcode = ((0x3 << 12) | (0 << 8) | addr)
        cpu.pc = 0

        cpu.skip_if_register_not_equals_value()

        assert cpu.pc == 0


def test_skip_if_register_equal_other_register_should_skip_if_registers_are_equal(cpu):
    for i in range(0, 16, 2):
        cpu.opcode = ((0x5 << 12) | (i << 8) | ((i + 1) << 4))
        cpu.v[i] = 200
        cpu.v[i + 1] = 200

        cpu.pc = 0

        cpu.skip_if_register_equal_other_register()
        assert cpu.pc == 2


def test_skip_if_register_equal_other_register_should_not_skip_if_values_not_equal(cpu):
    for i in range(0, 16, 2):
        cpu.opcode = ((0x5 << 12) | (i << 8) | ((i + 1) << 4))
        cpu.v[i] = 200
        cpu.v[i + 1] = 100

        cpu.pc = 0

        cpu.skip_if_register_equal_other_register()

        assert cpu.pc == 0


def test_move_value_to_register(cpu):
    for i in range(16):
        for value in range(1, 0xFF):
            cpu.opcode = (6 << 12) | (i << 8) | value

            cpu.v[i] = 0
            cpu.move_value_to_register()
            assert cpu.v[i] == value


def test_add_value_to_register(cpu):
    for i in range(16):
        for value in range(1, 0xFF):
            cpu.opcode = (7 << 12) | (i << 8) | value

            before_addition = cpu.v[i]
            cpu.add_value_to_register()
            assert cpu.v[i] == (before_addition + value) % 256


def test_move_register_to_register(cpu):
    for i in range(0, 16, 2):
        cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
        cpu.v[i] = 200
        cpu.v[i + 1] = 0

        cpu.move_register_to_register()

        assert cpu.v[i] == cpu.v[i + 1]


def test_register_logical_or_register(cpu):
    for i in range(0, 16, 2):
        for value in range(1, 0xFF):
            cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
            cpu.v[i] = value
            cpu.v[i + 1] = 0xFF - value

            cpu.register_logical_or_register()

            assert cpu.v[i] == (value | 0xFF - value)


def test_register_logical_and_register(cpu):
    for i in range(0, 16, 2):
        for value in range(1, 0xFF):
            cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
            cpu.v[i] = value
            cpu.v[i + 1] = 0xFF - value

            cpu.register_logical_and_register()

            assert cpu.v[i] == (value & 0xFF - value)


def test_register_logical_xor_register(cpu):
    for i in range(0, 16, 2):
        for value in range(1, 0xFF):
            cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
            cpu.v[i] = value
            cpu.v[i + 1] = 0xFF - value

            cpu.register_logical_xor_register()

            assert cpu.v[i] == (value ^ 0xFF - value)


def test_add_register_to_register(cpu):
    for i in range(0, 16, 2):
        for value in range(1, 0xFF - 1):
            cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
            cpu.v[i] = value
            cpu.v[i + 1] = value + 1
            sum = cpu.v[i] + cpu.v[i + 1]
            cpu.add_register_to_register()

            assert cpu.v[i] == sum % 256
            if sum >= 256:
                assert cpu.v[0xF] == 1
            else:
                assert cpu.v[0xF] == 0


def test_subtract_register_from_register(cpu):
    for i in range(0, 0xF, 2):
        for value_x in range(0, 0xFF):
            for value_y in range(0, 0xFF):
                cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
                cpu.v[i] = value_x
                cpu.v[i + 1] = value_y
                cpu.subtract_register_from_register()

                if value_x >= value_y:
                    assert cpu.v[i] == value_x - value_y
                    assert cpu.v[0xF] == 1
                else:
                    assert cpu.v[i] == value_x + 256 - value_y
                    assert cpu.v[0xF] == 0


def test_shift_register_right(cpu):
    for value in range(0xFF):
        for i in range(0xF):
            cpu.opcode = ((8 << 12) | (i << 8) | 0x6)
            lsb = value & 0x1
            cpu.v[i] = value

            cpu.shift_register_right()
            assert cpu.v[i] == value >> 1
            assert cpu.v[0xF] == lsb


def test_negative_subtract_register_from_register(cpu):
    for i in range(0, 0xF, 2):
        for value_x in range(0, 0xFF):
            for value_y in range(0, 0xFF):
                cpu.opcode = ((0x8 << 12) | (i << 8) | ((i + 1) << 4))
                cpu.v[i] = value_x
                cpu.v[i + 1] = value_y
                cpu.negative_subtract_register_from_register()

                if value_y >= value_x:
                    assert cpu.v[i] == value_y - value_x
                    assert cpu.v[0xF] == 1
                else:
                    assert cpu.v[i] == value_y + 256 - value_x
                    assert cpu.v[0xF] == 0


def test_shift_register_left(cpu):
    for value in range(0xFF):
        for i in range(0xF):
            cpu.opcode = ((8 << 12) | (i << 8) | 0x6)
            msb = (value & 0x80) >> 8
            cpu.v[i] = value

            cpu.shift_register_left()

            assert cpu.v[i] == (value << 1) & 0xFF
            assert cpu.v[0xF] == msb


def test_skip_if_register_not_equal_other_register_should_skip_if_registers_are_not_equal_should_skip_if_not_equal(cpu):
    for value in range(1, 0xFF):
        for x in range(0xF):
            for y in range(0xF):
                if x != y:
                    cpu.pc = 0
                    cpu.opcode = cpu.opcode = ((0x9 << 12) | (x << 8) | (y << 4))

                    cpu.v[x] = 0
                    cpu.v[y] = value

                    cpu.skip_if_register_not_equal_other_register()

                    assert cpu.pc == 2


def test_skip_if_register_not_equal_other_register_should_not_skip_if_equal(cpu):
    x = 1
    y = 2
    for value in range(1, 0xFF):
        cpu.pc = 0
        cpu.opcode = cpu.opcode = ((0x9 << 12) | (x << 8) | (y << 4))

        cpu.v[x] = value
        cpu.v[y] = value

        cpu.skip_if_register_not_equal_other_register()

        assert cpu.pc == 0


def test_move_value_to_index(cpu):
    for value in range(0xFFF):
        cpu.opcode = (0xA << 12) | value
        cpu.i = 0

        cpu.move_value_to_index()
        assert cpu.i == value


def test_jump_to_address_plus_v_zero(cpu):
    for v_0 in range(0xFF):
        for value in range(0xFFF):
            cpu.pc = 0
            cpu.opcode = (0xB << 12) | value
            cpu.v[0] = v_0
            cpu.jump_to_address_plus_v_zero()
            assert cpu.pc == v_0 + value


def test_generate_random_number(cpu):
    def random_int(*args):
        return 255

    with mock.patch('PyCHIP8.cpu.randint', random_int):

        for x in range(0xF):
            for value in range(0xFF):
                cpu.opcode = 0xC << 12 | x << 8 | value

                cpu.generate_random_number()

                assert cpu.v[x] == value & random_int()


# TODO test draw sprite


def test_skip_if_key_is_pressed_should_skip_if_key_is_pressed(cpu):
    possible_keys = Config.KEY_MAPPING.values()
    # pygame stores key pressed in array containing boolean values, there are 323 possible keys
    pressed_keys = [False] * 323
    for key in possible_keys:
        pressed_keys[key] = True

    def get_pressed():
        return pressed_keys

    possible_keys = Config.KEY_MAPPING.keys()
    for x in range(0xF):
        for key in possible_keys:
            with mock.patch('PyCHIP8.cpu.key.get_pressed', get_pressed):
                cpu.opcode = 0xE << 12 | (x << 8) | 0x9E
                cpu.v[x] = key
                cpu.pc = 0

                cpu.skip_if_key_is_pressed()

                assert cpu.pc == 2


def test_skip_if_key_is_pressed_should_not_skip_if_key_is_not_pressed(cpu):
    # pygame stores key pressed in array containing boolean values, there are 323 possible keys
    pressed_keys = [False] * 323

    def get_pressed():
        return pressed_keys

    possible_keys = Config.KEY_MAPPING.keys()
    for x in range(0xF):
        for key in possible_keys:
            with mock.patch('PyCHIP8.cpu.key.get_pressed', get_pressed):
                cpu.opcode = 0xE << 12 | (x << 8) | 0x9E
                cpu.v[x] = key
                cpu.pc = 0

                cpu.skip_if_key_is_pressed()

                assert cpu.pc == 0


def test_skip_if_key_is_not_pressed_should_skip_if_key_is_not_pressed(cpu):
    # pygame stores key pressed in array containing boolean values, there are 323 possible keys
    pressed_keys = [False] * 323

    def get_pressed():
        return pressed_keys

    possible_keys = Config.KEY_MAPPING.keys()
    for x in range(0xF):
        for key in possible_keys:
            with mock.patch('PyCHIP8.cpu.key.get_pressed', get_pressed):
                cpu.opcode = 0xE << 12 | (x << 8) | 0x9E
                cpu.v[x] = key
                cpu.pc = 0

                cpu.skip_if_key_is_not_pressed()

                assert cpu.pc == 2


def test_skip_if_key_is_not_pressed_should_not_skip_if_key_is_pressed(cpu):
    possible_keys = Config.KEY_MAPPING.values()
    # pygame stores key pressed in array containing boolean values, there are 323 possible keys
    pressed_keys = [False] * 323
    for key in possible_keys:
        pressed_keys[key] = True

    def get_pressed():
        return pressed_keys

    possible_keys = Config.KEY_MAPPING.keys()
    for x in range(0xF):
        for key in possible_keys:
            with mock.patch('PyCHIP8.cpu.key.get_pressed', get_pressed):
                cpu.opcode = 0xE << 12 | (x << 8) | 0x9E
                cpu.v[x] = key
                cpu.pc = 0

                cpu.skip_if_key_is_not_pressed()

                assert cpu.pc == 0


def test_move_delay_to_register(cpu):
    for x in range(1, 0xF):
        for value in [0, 0xFA, 0xFF]:
            cpu.opcode = (0xF << 12) | (x << 8)
            cpu.timer_dt = value

            cpu.v[x] = 0

            cpu.move_delay_to_register()
            assert cpu.v[x] == value


def test_move_register_to_delay_timer(cpu):
    for x in range(0xF):
        for value in [1, 0xFA, 0xFF]:
            cpu.timer_dt = 0

            cpu.opcode = (0xF << 12) | (x << 8) | 0x12
            cpu.v[x] = value

            cpu.move_register_to_delay_timer()

            assert cpu.timer_dt == value


def test_move_register_to_sound_timer(cpu):
    for x in range(0xF):
        for value in [1, 0xFA, 0xFF]:
            cpu.timer_st = 0

            cpu.opcode = (0xF << 12) | (x << 8) | 0x12
            cpu.v[x] = value

            cpu.move_register_to_sound_timer()

            assert cpu.timer_st == value


def test_move_sprite_address_to_index(cpu):
    for x in range(0xF):
        for value in [1, 0xF, 0xFA, 0xFF]:
            cpu.v[x] = value
            cpu.i = 0
            cpu.opcode = (0xF << 12) | (x << 8) | 0x30

            cpu.move_sprite_address_to_index()
            assert cpu.i == value * 5


def test_move_extended_sprite_address_to_index(cpu):
    for x in range(0xF):
        for value in [1, 0xF, 0xFA, 0xFF]:
            cpu.v[x] = value
            cpu.i = 0
            cpu.opcode = (0xF << 12) | (x << 8) | 0x30

            cpu.move_extended_sprite_address_to_index()
            assert cpu.i == value * 10


def test_store_bcd_in_memory(cpu):
    for value in range(0xFF):
        for x in range(0xF):
            cpu.i = 0
            cpu.opcode = (0xF << 12) | (x << 8) | 0x33
            cpu.v[x] = value

            value_str = str(value).zfill(3)

            cpu.store_bcd_in_memory()
            assert cpu.memory[0] == int(value_str[0])
            assert cpu.memory[1] == int(value_str[1])
            assert cpu.memory[2] == int(value_str[2])


def test_store_registers_in_memory(cpu):
    for x in range(0xF):
        for i in range(x):
            cpu.v[i] = 0xF * i

        cpu.i = Config.MAX_MEMORY - x - 1
        cpu.opcode = (0xF << 12) | (x << 8) | 0x55

        cpu.store_registers_in_memory()

        for j in range(x):
            assert cpu.memory[cpu.i + j] == cpu.v[j]
