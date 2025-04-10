import time
from datetime import datetime
import board
import neopixel
import requests
from PIL import Image, ImageDraw, ImageFont

#=== LED MATRIX CONFIG ===
LED_ROWS = 32
LED_COLS = 384
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = board.D18  #GPIO18
BRIGHTNESS = 0.2

#initialize NeoPixel strip
pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)

# === WEATHER API CONFIG ===
API_KEY = "6592c6ba769a4b934b6d309f912c7a8d"
CITY = "State College"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"

#=== FONT SETTINGS ===
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_main = ImageFont.truetype(FONT_PATH, 16)
TEXT_COLOR = (0, 0, 255)
ANNOUNCEMENT_COLOR = (255, 255, 0)

def get_weather():
    try:
        response = requests.get(URL)
        data = response.json()
        temp = round(data["main"]["temp"])
        condition = data["weather"][0]["main"]
        return f"{temp}°F {condition}"
    except:
        return "Weather Error"

#zigzag layout function
def get_led_index(x, y):
    y = LED_ROWS - 1 - y
    return y * LED_COLS + (x if y % 2 == 0 else (LED_COLS - 1 - x))

def draw_text_image(text, color):
    bbox = font_main.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    img_width = width + LED_COLS + 100
    img = Image.new("RGB", (img_width, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = (LED_ROWS - height) // 2
    draw.text((LED_COLS, y), text, font=font_main, fill=color)
    return img

def scroll_image(img, speed=0.03):
    width = img.width
    for offset in range(width):
        frame = img.crop((offset, 0, offset + LED_COLS, LED_ROWS))
        for y in range(LED_ROWS):
            for x in range(LED_COLS):
                r, g, b = frame.getpixel((x, y))
                pixels[get_led_index(x, y)] = (r, g, b)
        pixels.show()
        time.sleep(speed)

#=== MAIN LOOP ===
ANNOUNCEMENT_TEXT = "Capstone LED Matrix Live Demo Week!"
STATIC_DURATION = 30

while True:
    #1.show static time + weather for 30 seconds
    combined = f"{datetime.now().strftime('%I:%M %p')}    {get_weather()}"
    bbox = font_main.getbbox(combined)
    text_width = bbox[2] - bbox[0]
    spacing = (LED_COLS - 3 * text_width) // 4
    img = Image.new("RGB", (LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = (LED_ROWS - (bbox[3] - bbox[1])) // 2
    for i in range(3):
        x = spacing + i * (text_width + spacing)
        draw.text((x, y), combined, font=font_main, fill=TEXT_COLOR)
    for y in range(LED_ROWS):
        for x in range(LED_COLS):
            r, g, b = img.getpixel((x, y))
            pixels[get_led_index(x, y)] = (r, g, b)
    pixels.show()
    time.sleep(STATIC_DURATION)

    #2. scroll time + weather
    scroll_image(draw_text_image(combined, TEXT_COLOR))

    #3. scroll announcement
    scroll_image(draw_text_image(ANNOUNCEMENT_TEXT, ANNOUNCEMENT_COLOR), speed=0.05)