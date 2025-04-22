import time
from rpi_ws281x import PixelStrip, Color

# === SINGLE PANEL CONFIG ===
LED_ROWS = 16
LED_COLS = 16
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = 18  # GPIO18
BRIGHTNESS = 40

# === Initialize Strip ===
strip = PixelStrip(LED_COUNT, LED_PIN, 800000, 10, False, BRIGHTNESS)
strip.begin()

# === Simple Zigzag Mapping Function (panel only) ===
def get_led_index(x, y):
    if y % 2 == 0:
        return y * LED_COLS + x  # even rows left to right
    else:
        return y * LED_COLS + (LED_COLS - 1 - x)  # odd rows right to left

# === Ball Setup ===
x = 0
y = 0
dx = 1
dy = 1
BALL_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)

# === Draw Pixel Helper ===
def draw_pixel(x, y, color):
    if 0 <= x < LED_COLS and 0 <= y < LED_ROWS:
        strip.setPixelColor(get_led_index(x, y), Color(*color))

# === Main Loop ===
while True:
    # Clear screen
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(*BG_COLOR))

    # Draw ball
    draw_pixel(x, y, BALL_COLOR)
    strip.show()
    time.sleep(0.05)

    # Move ball
    x += dx
    y += dy

    # Bounce off walls
    if x <= 0 or x >= LED_COLS - 1:
        dx *= -1
    if y <= 0 or y >= LED_ROWS - 1:
        dy *= -1
