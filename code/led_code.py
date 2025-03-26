import time
from datetime import datetime
import requests
from rpi_ws281x import PixelStrip, Color
from PIL import Image, ImageDraw, ImageFont

#confuguration for the led
LED_ROWS = 32
LED_COLS = 384  #24 panels wide * 16px
LED_COUNT = LED_ROWS * LED_COLS
LED_PIN = 18
BRIGHTNESS = 40

strip = PixelStrip(LED_COUNT, LED_PIN, 800000, 10, False, BRIGHTNESS, 0)
strip.begin() #basically initializes communication with the LED matrices

#text, adjustable
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_main = ImageFont.truetype(font_path, 16)
TEXT_COLOR = (0, 0, 255)
ANNOUNCEMENT_COLOR = (255, 255, 0)

#weather API import
API_KEY = "6592c6ba769a4b934b6d309f912c7a8d"
CITY = "State College"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"

def get_weather():
    try:
        response = requests.get(URL)
        data = response.json()
        temp = round(data["main"]["temp"]) #retrieves the current temperature
        condition = data["weather"][0]["main"]
        return f"{temp}°F {condition}" #format for display purposes
    except:
        return "Weather Error"

#LED MAPPING FUNCTION (Zigzag layout)
def get_led_index(x, y):
    y = LED_ROWS - 1 - y  #flip vertical if the bottom row is 0
    return y * LED_COLS + (x if y % 2 == 0 else (LED_COLS - 1 - x)) #even rows go left to right, odd rows go right to left


def generate_time_weather_image():
    time_str = datetime.now().strftime("%I:%M %p")
    weather_str = get_weather()
    combined = f"{time_str}    {weather_str}" #combine both of the strings
    text_width, text_height = font_main.getsize(combined)

    img_width = text_width + LED_COLS #measure the width of the string then
    #we create a wide image to scroll across
    img = Image.new("RGB", (img_width + LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = (LED_ROWS - text_height) // 2 #center the text
    draw.text((LED_COLS, y), combined, font=font_main, fill=TEXT_COLOR)
    draw.text((LED_COLS + text_width + 50, y), combined, font=font_main, fill=TEXT_COLOR)
    return img


announcement_text = "capstone"

def generate_announcement_image(text):
    #same idea as weather and time
    font_announcement = ImageFont.truetype(font_path, 14)
    text_width, text_height = font_announcement.getsize(text)

    img_width = text_width + LED_COLS
    img = Image.new("RGB", (img_width + LED_COLS, LED_ROWS), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = (LED_ROWS - text_height) // 2
    draw.text((LED_COLS, y), text, font=font_announcement, fill=ANNOUNCEMENT_COLOR)
    draw.text((LED_COLS + text_width + 50, y), text, font=font_announcement, fill=ANNOUNCEMENT_COLOR)
    return img


def scroll_text(image, speed=0.03):
    offset = 0 #starting at leftmost part of the image
    width = image.width
    while offset < width: #scroll until a full loop is complete
        frame = Image.new("RGB", (LED_COLS, LED_ROWS), (0, 0, 0))
        for x in range(LED_COLS): #fill the frame from the image by copying pixels with wrapping
            for y in range(LED_ROWS):
                src_x = (offset + x) % width #wrap around
                r, g, b = image.getpixel((src_x, y))
                frame.putpixel((x, y), (r, g, b))
        #convert image to LED colors
        for y in range(LED_ROWS):
            for x in range(LED_COLS):
                r, g, b = frame.getpixel((x, y))
                strip.setPixelColor(get_led_index(x, y), Color(r, g, b))
        strip.show() #this basically pushes updates to led
        offset = (offset + 1) % width #move the scroll position
        time.sleep(speed)


while True:
    #time and weather scroll
    time_image = generate_time_weather_image()
    scroll_text(time_image)

    #announcement scroll
    announcement_image = generate_announcement_image(announcement_text)
    scroll_text(announcement_image)
