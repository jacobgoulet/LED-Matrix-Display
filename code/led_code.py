import time
from datetime import datetime
import requests
from rpi_ws281x import PixelStrip, Color
from PIL import Image, ImageDraw, ImageFont

#=== LED MATRIX CONFIG ===
LED_ROWS = 32
LED_COLS = 384
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = 18  # GPIO18
BRIGHTNESS = 40

#=== Initialize LED Strip ===
strip = PixelStrip(LED_COUNT, LED_PIN, 800000, 10, False, BRIGHTNESS)
strip.begin()

#=== FONT SETUP ===
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_main = ImageFont.truetype(FONT_PATH, 16)
TEXT_COLOR = (0, 0, 255)
ANNOUNCEMENT_COLOR = (255, 255, 0)

#=== WEATHER API CONFIG ===
API_KEY = "6592c6ba769a4b934b6d309f912c7a8d"
CITY = "State College"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"

def get_weather():
    try:
        response = requests.get(URL)
        data = response.json()
        temp = round(data["main"]["temp"])
        condition = data["weather"][0]["main"]
        return f"{temp}°F {condition}", condition
    except:
        return "Weather Error", "Error"

#=== PANEL MAPPING (Z pattern starting top-left) ===
def get_led_index(x, y):
    panel_h = 16
    panel_w = 16
    panel_column = x // panel_h
    panel_row = y // panel_w
    panel_x = x % panel_h
    panel_y = y % panel_w
    if panel_column % 2 == 0:
        led_index = (panel_row * panel_h + panel_x) * panel_w + panel_y
    else:
        led_index = (panel_row * panel_h + (panel_w - 1 - panel_x)) * panel_w + panel_y

    return led_index + (panel_column * panel_h * panel_w) + (panel_row * panel_w * panel_h)

#=== WEATHER ICON DRAWING ===
def draw_weather_icon(condition):
    icon = Image.new("RGB", (32, 32), (0, 0, 0))
    draw = ImageDraw.Draw(icon)
    if condition == "Clear":
        draw.ellipse((8, 8, 24, 24), fill=(255, 255, 0))  #sun
    elif condition == "Clouds":
        draw.ellipse((10, 12, 22, 24), fill=(150, 150, 150))
        draw.ellipse((14, 8, 26, 20), fill=(150, 150, 150))
    elif condition == "Rain":
        draw.ellipse((10, 12, 22, 24), fill=(150, 150, 150))
        draw.ellipse((14, 8, 26, 20), fill=(150, 150, 150))
        draw.rectangle((12, 26, 14, 30), fill=(0, 100, 255))
        draw.rectangle((18, 26, 20, 30), fill=(0, 100, 255))
    elif condition == "Snow":
        draw.ellipse((10, 12, 22, 24), fill=(150, 150, 150))
        draw.ellipse((14, 8, 26, 20), fill=(150, 150, 150))
        draw.text((13, 26), "*", font=font_main, fill=(255, 255, 255))
    return icon

#=== DRAWING FUNCTIONS ===
def draw_text_image(text, color, icon=None):
    bbox = font_main.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    img_width = width + LED_COLS + 100 + (icon.width if icon else 0)
    img = Image.new("RGB", (img_width, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = (LED_ROWS - height) // 2
    draw.text((LED_COLS + (icon.width if icon else 0), y), text, font=font_main, fill=color)
    if icon:
        img.paste(icon, (LED_COLS, 0))
    return img

def scroll_image(img, speed=0.03):
    width = img.width
    for offset in range(width - LED_COLS):
        frame = img.crop((offset, 0, offset + LED_COLS, LED_ROWS))
        for y in range(LED_ROWS):
            for x in range(LED_COLS):
                r, g, b = frame.getpixel((x, y))
                strip.setPixelColor(get_led_index(x, y), Color(r, g, b))
        strip.show()
        time.sleep(speed)

def show_static_text(text, color, duration=30):
    bbox = font_main.getbbox(text)
    text_width = bbox[2] - bbox[0]
    spacing = (LED_COLS - 3 * text_width) // 4
    img = Image.new("RGB", (LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = (LED_ROWS - (bbox[3] - bbox[1])) // 2
    for i in range(3):
        x = spacing + i * (text_width + spacing)
        draw.text((x, y), text, font=font_main, fill=color)
    for y in range(LED_ROWS):
        for x in range(LED_COLS):
            r, g, b = img.getpixel((x, y))
            strip.setPixelColor(get_led_index(x, y), Color(r, g, b))
    strip.show()
    time.sleep(duration)

#=== ANNOUNCEMENTS ===
ANNOUNCEMENTS = [
    "Jacob",
    "Ben",
    "Sami",
    "Mason",
    "Stevie"
]

#=== MAIN LOOP ===
while True:
    weather_str, condition = get_weather()
    combined = f"{datetime.now().strftime('%I:%M %p')}    {weather_str}"
    icon = draw_weather_icon(condition)

    #1. Static display
    show_static_text(combined, TEXT_COLOR, duration=30)

    #2. Scroll time + weather
    scroll_image(draw_text_image(combined, TEXT_COLOR, icon), speed=0.02)

    #3. Scroll all announcements
    for msg in ANNOUNCEMENTS:
        scroll_image(draw_text_image(msg, ANNOUNCEMENT_COLOR), speed=0.05)
