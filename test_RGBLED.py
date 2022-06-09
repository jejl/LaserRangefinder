import board
import neopixel
import time
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(board.D10, 1, brightness=0.1, pixel_order=ORDER)
pixels[0] = (0, 255, 0)
time.sleep(0.5)
pixels[0] = (255, 0, 0)
time.sleep(0.5)
pixels[0] = (0, 0, 255)
