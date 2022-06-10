import spidev as SPI
import ST7789
import time

from PIL import Image,ImageDraw,ImageFont

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 24
bus = 0
device = 0

class ScreenAndButtons:

    def __init__(self):
        """Open display and initialise. self.disp is the display object"""
        # 240x240 display with hardware SPI:
        self.disp = ST7789.ST7789(SPI.SpiDev(bus, device), RST, DC, BL)

        # Initialize library.
        self.disp.Init()

        # Clear display.
        self.disp.clear()

