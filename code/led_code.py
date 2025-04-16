import time
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import board
import neopixel

#=== LED MATRIX CONFIGURATION ===
LED_ROWS = 32
LED_COLS = 384
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = board.D18
BRIGHTNESS = 0.2

#Initialize the NeoPixel matrix
pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)

#=== WEATHER API CONFIG ===
API_KEY = "6592c6ba769a4b934b6d309f912c7a8d"
CITY = "State College"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"

#=== FONTS AND COLORS ===
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_main = ImageFont.truetype(FONT_PATH, 16)
TEXT_COLOR = (0, 0, 255)
ANNOUNCEMENT_COLOR = (255, 255, 0)

#=== DISPLAY FUNCTIONS ===
def get_weather_data():
    try:
        response = requests.get(URL)
        data = response.json()
        temp = round(data["main"]["temp"])
        condition = data["weather"][0]["main"].lower()
        return temp, condition
    except:
        return None, "weather error"

def draw_weather_icon(draw, x, y, condition):
    if "clear" in condition:
        draw.ellipse((x, y, x+12, y+12), fill=(255, 255, 0))
    elif "cloud" in condition:
        draw.ellipse((x, y+2, x+10, y+10), fill=(200, 200, 200))
        draw.ellipse((x+6, y, x+16, y+10), fill=(200, 200, 200))
    elif "rain" in condition:
        draw.ellipse((x, y+2, x+10, y+10), fill=(150, 150, 150))
        draw.line((x+3, y+11, x+3, y+15), fill=(0, 0, 255))
        draw.line((x+7, y+11, x+7, y+15), fill=(0, 0, 255))
    elif "snow" in condition:
        draw.text((x, y), "*", font=font_main, fill=(255, 255, 255))
    elif "thunder" in condition:
        draw.ellipse((x, y+2, x+10, y+10), fill=(100, 100, 100))
        draw.line((x+6, y+10, x+4, y+14), fill=(255, 255, 0), width=2)
    elif "fog" in condition or "mist" in condition:
        draw.line((x, y+4, x+14, y+4), fill=(180, 180, 180))
        draw.line((x, y+8, x+14, y+8), fill=(180, 180, 180))

def get_led_index(x, y):
    y = LED_ROWS - 1 - y
    return y * LED_COLS + (x if y % 2 == 0 else (LED_COLS - 1 - x))

def render_image_to_pixels(image):
    for y in range(LED_ROWS):
        for x in range(LED_COLS):
            r, g, b = image.getpixel((x, y))
            pixels[get_led_index(x, y)] = (r, g, b)
    pixels.show()

def scroll_image(image, speed=0.03):
    width = image.width
    for offset in range(width):
        frame = image.crop((offset, 0, offset + LED_COLS, LED_ROWS))
        render_image_to_pixels(frame)
        time.sleep(speed)

#=== MAIN LOOP ===
ANNOUNCEMENT_TEXT = "Capstone LED Matrix Live Demo!"
STATIC_DURATION = 30

while True:
    #Static display of time and weather
    temp, condition = get_weather_data()
    time_str = datetime.now().strftime("%I:%M %p")
    label = f"{time_str}    {temp}°F {condition.capitalize()}"
    bbox = font_main.getbbox(label)
    text_width = bbox[2] - bbox[0]
    spacing = (LED_COLS - 3 * text_width) // 4

    img = Image.new("RGB", (LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_weather_icon(draw, 5, 10, condition)
    y = (LED_ROWS - (bbox[3] - bbox[1])) // 2
    for i in range(3):
        x = spacing + i * (text_width + spacing)
        draw.text((x, y), label, font=font_main, fill=TEXT_COLOR)
    render_image_to_pixels(img)
    time.sleep(STATIC_DURATION)

    #Scroll time + weather
    scroll_image(draw_text_image(label, TEXT_COLOR))

    #Scroll announcements
    scroll_image(draw_text_image(ANNOUNCEMENT_TEXT, ANNOUNCEMENT_COLOR), speed=0.05)
