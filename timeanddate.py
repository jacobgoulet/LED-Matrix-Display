import board
import neopixel
import time
from adafruit_pixel_framebuf import PixelFramebuffer
from datetime import datetime

pixel_pin = board.D18
pixel_width = 16
pixel_height = 32
num_pixels = pixel_width * pixel_height

pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    brightness=0.2,
    auto_write=False,
)

pixel_framebuf = PixelFramebuffer(
    pixels,
    pixel_width,
    pixel_height,
    reverse_x=True,
    orientation=1,
    rotation=1
)

CHAR_WIDTH = 6  # 5px character width + 1px spacing

while True:
    # Get current time and date
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p").lstrip('0')  # Remove leading zero
    date_str = now.strftime("%A %m/%d/%Y")

    # Calculate X positions to center
    time_x = max((pixel_width - (len(time_str) * CHAR_WIDTH)) // 2, 0)
    date_x = max((pixel_width - (len(date_str) * CHAR_WIDTH)) // 2, 0)

    pixel_framebuf.fill(0x000000)

    # Draw time (top), centered
    pixel_framebuf.text(time_str, time_x, 0, 0x00FF00)

    # Draw date/day (bottom), centered
    pixel_framebuf.text(date_str, date_x, 12, 0xFFFFFF)

    pixel_framebuf.display()
    time.sleep(1)
