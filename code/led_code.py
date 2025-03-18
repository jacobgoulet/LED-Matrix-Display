import time
from datetime import datetime
from rpi_ws281x import PixelStrip, Color
from PIL import Image, ImageDraw, ImageFont

#the configuration of the LED
LED_ROWS = 16
LED_COLS = 32
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = 18
BRIGHTNESS = 40

#initialize LED Matrix
strip = PixelStrip(LED_COUNT, LED_PIN, 800000, 10, False, BRIGHTNESS, 0)
strip.begin()

#random font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
TEXT_COLOR = (0, 0, 255)  #blue test

#this is going to map the LED based on the chain sequence of the matrix
#in this system we go from right to left on the bottom, then connect to top, then go left to right on top
def get_led_index(x, y):
    return y * LED_COLS + (x if y % 2 == 0 else (LED_COLS - 1 - x))

#this is the function to generate the image of the time
def generate_time_image():
    current_time = datetime.now().strftime("%I:%M %p")  
    text_size = font.getsize(current_time)
    img = Image.new("RGB", (text_size[0] + LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((LED_COLS, (LED_ROWS - text_size[1]) // 2), current_time, font=font, fill=TEXT_COLOR)
    return img

#scroll across the screen
def scroll_text(image):
    for offset in range(image.width - LED_COLS):
        frame = image.crop((offset, 0, offset + LED_COLS, LED_ROWS))
        for y in range(LED_ROWS):
            for x in range(LED_COLS):
                r, g, b = frame.getpixel((x, y))
                strip.setPixelColor(get_led_index(x, y), Color(r, g, b) if (r or g or b) else 0)
        strip.show()
        time.sleep(5.0 / (image.width + LED_COLS))  #this is a 5 second scroll for testing across all panels

#update the time
while True:
    time_image = generate_time_image()
    scroll_text(time_image)
