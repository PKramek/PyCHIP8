import pygame


class Config:

    STACK_POINTER = 0x52
    MAX_MEMORY = 4096
    PROGRAM_COUNTER = 0x200
    NUMBER_OF_REGISTERS = 0x10

    SCREEN_WIDTH_NORMAL = 64
    SCREEN_HEIGHT_NORMAL = 32

    SCREEN_WIDTH_EXTENDED = 128
    SCREEN_HEIGHT_EXTENDED = 64

    # Colors in RGBA format
    SCREEN_COLORS = [(0, 0, 0, 255), (65, 255, 0, 255)]

    CPU_CLOCK_SPEED = 500  # in HZ
    TIMER_DELAY = 20  # in ms

    KEY_MAPPING = {
        0x0: pygame.K_1,
        0x1: pygame.K_2,
        0x2: pygame.K_3,
        0x3: pygame.K_4,
        0x4: pygame.K_q,
        0x5: pygame.K_w,
        0x6: pygame.K_e,
        0x7: pygame.K_r,
        0x8: pygame.K_a,
        0x9: pygame.K_s,
        0xA: pygame.K_d,
        0xB: pygame.K_f,
        0xC: pygame.K_z,
        0xD: pygame.K_x,
        0xE: pygame.K_c,
        0xF: pygame.K_v,
    }


class Constants:
    NORMAL_MODE = 'NORMAL'
    EXTENDED_MODE = 'EXTENDED'
