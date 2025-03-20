import board
import neopixel
from adafruit_pixel_framebuf import PixelFramebuffer

# Matrix configuration for 16x32
pixel_pin = board.D18
pixel_width = 16
pixel_height = 32
num_pixels = pixel_width * pixel_height

# Initialize NeoPixels
pixels = neopixel.NeoPixel(
    pixel_pin,
    num_pixels,
    brightness=0.2,
    auto_write=False,
)

# Create the framebuffer for drawing
pixel_framebuf = PixelFramebuffer(
    pixels,
    pixel_width,
    pixel_height,
    reverse_x=True,
    orientation=1,
    rotation=1
)

# Fill background with black
pixel_framebuf.fill(0x000000)

# Display the text "hello" in purple (hex color 0xb400ff)
pixel_framebuf.text("hello", 1, 12, 0xb400ff)  # (x=1, y=12) adjust if needed

# Show the frame on the matrix
pixel_framebuf.display()

# Keep displaying (the matrix holds the image until power off or code update)
while True:
    pass  # Infinite loop to keep the program running
