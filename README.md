# PyCHIP8
This is a project where I implemented CHIP-8 emulator using Python 3. 
## Table of content
<!-- TOC -->
- [PyCHIP8](#pychip8)
- [Table of content](#table-of-content)
- [Installation](#installation)
- [Running](#running)
- [Changing key mapping](#changing-key-mapping)
<!-- /TOC -->

## Installation
To install this emulator you will need Python 3.7 with pip package. Using virtual environment in recommended but not necessary
1. Download this repository (using download button or use git clone command)
1. (Optional) Create virtual environment by running ``` virtualenv venv ```
1. (Optional) Activate virtual environment by running ```venv\Scripts\activate``` (Windows)  or ```source venv/bin/activate```(Linux)
1. Run ```pip install -r requirements.txt ```

## Running

To run this emulator you have to have valid CHIP-8 ROM file. There are many sources you can get them from and one example is [this github repository](https://github.com/dmatlack/chip8/tree/master/roms)

Running PyCHIP8 emulator is done by running ```python PyCHIP8.py --rom <path_to_file>``` command
## Changing key mapping
To change key mapping in this emulator you have to change PyCHIP8/conf.py file. In this file there is python dictionary named KEY_MAPPING, change values in it to customize key mapping to your preferences.

CHIP-8 uses 4x4 keyboard and each key has its address in memory. To help you visualize this I`ve created table below. Each cell represents key, and value in the cell is address specified in KEY_MAPPING key. 

|  |  |  |  |
| --- | --- | --- | --- |
| 0x0 | 0x1 | 0x2 | 0x3 |
| 0x4 | 0x5 | 0x6 | 0x7 |
| 0x8 | 0x9 | 0xA | 0xB |
| 0xC | 0xD | 0xE | 0xF |
|  |  |  |  |

This is the current key mapping

|  |  |  |  |
| --- | --- | --- | --- |
| 1 | 2 | 3 | 4 |
| q | w | e | r |
| a | s | d | f |
| z | x | c | v |
|  |  |  |  |

Because this emulator uses pygame for keyboard support, you will have to use pygame constants to define keys, to find specific keys visit [this site](https://www.pygame.org/docs/ref/key.html)


