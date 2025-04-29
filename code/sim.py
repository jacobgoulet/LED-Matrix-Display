import time
import pygame
import requests
import random
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Initialize pygame
pygame.init()

# === DISPLAY SETTINGS ===
LED_ROWS = 36
LED_COLS = 480
PIXEL_SIZE = 4
SCREEN_WIDTH = LED_COLS * PIXEL_SIZE
SCREEN_HEIGHT = LED_ROWS * PIXEL_SIZE
FPS = 60

# Set up display and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("LED Matrix Weather Display")
clock = pygame.time.Clock()

# === SCROLL SPEEDS ===
SCROLL_SPEED_MAIN = 0.008
SCROLL_SPEED_ANNOUNCEMENT = 0.015

# === COLORS ===
BACKGROUND_COLOR = (0, 0, 0)
MAIN_COLOR = (0, 200, 255)  # Unified color for time, weather, and temp
ANNOUNCEMENT_COLOR = (252, 3, 3)

# === FONT SETUP ===
try:
    font_main = ImageFont.truetype("arialbd.ttf", 18)
except:
    font_main = ImageFont.load_default()

# === FIREWORK SYSTEM ===
class FireworkParticle:
    def __init__(self, x, y, angle, speed, color, lifetime=30):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.gravity = 0.05
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed

    def update(self):
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Fade out color as particle ages
        fade_factor = 1 - (self.age / self.lifetime)
        self.color = (
            int(self.color[0] * fade_factor),
            int(self.color[1] * fade_factor),
            int(self.color[2] * fade_factor)
        )
        
        # Age particle
        self.age += 1
        
        # Return True if still alive
        return self.age < self.lifetime

    def draw(self, img):
        # Only draw if within bounds
        if 0 <= int(self.x) < LED_COLS and 0 <= int(self.y) < LED_ROWS:
            img.putpixel((int(self.x), int(self.y)), self.color)
        return img

class Firework:
    def __init__(self, matrix_width, matrix_height):
        # Launch position
        self.x = random.randint(20, matrix_width - 20)
        self.y = matrix_height
        
        # Target explosion height
        self.target_y = random.randint(5, matrix_height - 10)
        
        # Movement properties
        self.speed = random.uniform(0.5, 1.5)
        self.particles = []
        self.exploded = False
        
        # Color themes
        color_themes = [
            [(255, 50, 50), (255, 150, 50), (255, 255, 50)],  # Red-orange
            [(50, 50, 255), (50, 150, 255), (50, 255, 255)],  # Blue
            [(50, 255, 50), (150, 255, 50), (255, 255, 50)],  # Green-yellow
            [(255, 50, 255), (255, 150, 255), (255, 200, 255)],  # Purple-pink
            [(255, 255, 255), (200, 200, 255), (150, 150, 255)]   # White-blue
        ]
        
        # Select a random color theme
        self.colors = random.choice(color_themes)
        
        # Trail particles
        self.trail = []

    def update(self):
        # If not exploded, move upward
        if not self.exploded:
            # Create trail particle
            if random.random() < 0.3:  # 30% chance each frame
                trail_particle = FireworkParticle(
                    self.x, self.y, 
                    random.uniform(0, 2*math.pi), 
                    random.uniform(0.2, 0.5),
                    (150, 150, 50),  # Yellow-ish trail
                    lifetime=10
                )
                self.trail.append(trail_particle)
            
            # Move upward
            self.y -= self.speed
            
            # Check if reached target height
            if self.y <= self.target_y:
                self.explode()
        
        # Update trail particles
        for i in range(len(self.trail) - 1, -1, -1):
            if not self.trail[i].update():
                self.trail.pop(i)
        
        # Update explosion particles
        for i in range(len(self.particles) - 1, -1, -1):
            if not self.particles[i].update():
                self.particles.pop(i)
        
        # Return True if still active (has particles)
        return len(self.particles) > 0 or len(self.trail) > 0 or not self.exploded

    def explode(self):
        self.exploded = True
        num_particles = random.randint(20, 40)
        
        # Create explosion pattern
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            color = random.choice(self.colors)
            
            particle = FireworkParticle(
                self.x, self.y, 
                angle, speed, 
                color, 
                lifetime=random.randint(20, 40)
            )
            self.particles.append(particle)

    def draw(self, img):
        # Draw trail particles
        for particle in self.trail:
            img = particle.draw(img)
        
        # Draw launch rocket if not exploded
        if not self.exploded:
            if 0 <= int(self.x) < LED_COLS and 0 <= int(self.y) < LED_ROWS:
                img.putpixel((int(self.x), int(self.y)), (255, 255, 150))
        
        # Draw explosion particles
        for particle in self.particles:
            img = particle.draw(img)
        
        return img

# Firework manager
class FireworkSystem:
    def __init__(self, matrix_width, matrix_height):
        self.width = matrix_width
        self.height = matrix_height
        self.fireworks = []
        self.last_launch_time = time.time()
        self.launch_interval = random.uniform(1.0, 3.0)  # Time between launches
    
    def update(self):
        # Check if it's time to launch a new firework
        current_time = time.time()
        if current_time - self.last_launch_time > self.launch_interval:
            # Launch new firework
            self.fireworks.append(Firework(self.width, self.height))
            self.last_launch_time = current_time
            self.launch_interval = random.uniform(1.0, 3.0)  # Randomize next interval
        
        # Update existing fireworks
        for i in range(len(self.fireworks) - 1, -1, -1):
            if not self.fireworks[i].update():
                self.fireworks.pop(i)
    
    def draw(self, img):
        # Draw all fireworks
        for firework in self.fireworks:
            img = firework.draw(img)
        return img

# Initialize firework system
firework_system = FireworkSystem(LED_COLS, LED_ROWS)

def draw_weather_icon(draw, x, y, condition, size=24):
    """Draw custom weather icons with improved visuals"""
    if condition == "clear":
        # Sun with rays
        draw.ellipse((x, y, x+size, y+size), fill=(255, 255, 0))
        for i in range(8):
            angle = i * math.pi/4
            end_x = x+size/2 + math.cos(angle)*size*0.7
            end_y = y+size/2 + math.sin(angle)*size*0.7
            draw.line((x+size/2, y+size/2, end_x, end_y), fill=(255, 255, 0), width=2)
    elif condition == "clouds":
        # Fluffy cloud
        draw.ellipse((x, y+size/3, x+size*0.6, y+size*0.8), fill=(220, 220, 220))
        draw.ellipse((x+size*0.3, y, x+size*0.9, y+size*0.7), fill=(230, 230, 230))
        draw.ellipse((x+size*0.1, y+size*0.2, x+size*0.7, y+size*0.9), fill=(240, 240, 240))
    elif condition == "rain":
        # Cloud with rain
        draw.ellipse((x, y+size/3, x+size*0.6, y+size*0.8), fill=(150, 150, 150))
        draw.ellipse((x+size*0.3, y, x+size*0.9, y+size*0.7), fill=(180, 180, 180))
        for i in range(5):
            ry = random.randint(int(y+size*0.7), int(y+size*1.1))
            draw.line((x+size*0.2+i*size*0.15, ry, x+size*0.2+i*size*0.15, ry+size*0.3), 
                     fill=(100, 100, 255), width=1)
    elif condition == "thunderstorm":
        # Storm cloud with lightning
        draw.ellipse((x, y+size/3, x+size*0.7, y+size*0.9), fill=(80, 80, 80))
        draw.ellipse((x+size*0.3, y, x+size, y+size*0.7), fill=(100, 100, 100))
        # Lightning bolt
        draw.polygon([
            (x+size*0.5, y+size*0.3),
            (x+size*0.4, y+size*0.5),
            (x+size*0.55, y+size*0.5),
            (x+size*0.45, y+size*0.8),
            (x+size*0.6, y+size*0.5),
            (x+size*0.5, y+size*0.6)
        ], fill=(255, 255, 0))
    elif condition == "snow":
        # Snow cloud with flakes
        draw.ellipse((x, y+size/3, x+size*0.7, y+size*0.9), fill=(230, 230, 230))
        draw.ellipse((x+size*0.3, y, x+size, y+size*0.7), fill=(240, 240, 230))
        for _ in range(8):
            sx = x + random.randint(0, size)
            sy = y + random.randint(int(size*0.7), size)
            for i in range(6):
                angle = i * math.pi/3
                draw.line((sx, sy, sx+math.cos(angle)*3, sy+math.sin(angle)*3),
                          fill=(255, 255, 255), width=1)
    else:  # Default (thermometer)
        # Thermometer with bulb
        draw.rectangle((x+size*0.3, y, x+size*0.7, y+size*0.8), fill=(255, 50, 50))
        draw.ellipse((x+size*0.2, y+size*0.6, x+size*0.8, y+size*1.2), fill=(255, 50, 50))

def get_weather():
    try:
        API_KEY = "6592c6ba769a4b934b6d309f912c7a8d"
        CITY = "State College"
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial",
            timeout=3
        )
        data = response.json()
        temp = round(data["main"]["temp"])
        condition = data["weather"][0]["main"].lower()
        description = data["weather"][0]["description"].title()
        return temp, condition, description
    except Exception as e:
        print(f"Weather error: {e}")
        return None, "default", "Weather Unavailable"

def render_time_weather():
    """Render time, weather, and temp in one color with spacing before icon"""
    current_time = datetime.now().strftime("%I:%M %p")
    temp, condition, description = get_weather()
    
    # Create text with space before icon
    weather_text = f"{description} {temp}°F   " if temp else f"{description} N/A°F   "
    full_text = f"{current_time}  {weather_text}"
    
    # Calculate widths
    text_width = font_main.getbbox(full_text)[2]
    icon_space = 30
    
    # Create image
    total_width = text_width + icon_space
    img = Image.new("RGB", (total_width, LED_ROWS), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw all text in unified color
    draw.text((0, (LED_ROWS-18)//2), full_text, font=font_main, fill=MAIN_COLOR)
    
    # Draw weather icon with spacing
    draw_weather_icon(draw, text_width, (LED_ROWS-24)//2, condition)
    
    return img

def render_announcement(text, color=ANNOUNCEMENT_COLOR):
    """Render announcement text"""
    img = Image.new("RGB", (font_main.getbbox(text)[2], LED_ROWS), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    draw.text((0, (LED_ROWS-18)//2), text, font=font_main, fill=color)
    return img

def check_quit():
    """Check for quit events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return True
    return False

def create_continuous_banner(images, spacing=20):
    """Create a continuous banner with multiple images separated by spacing"""
    # Calculate total width needed
    total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
    
    # Create a new image to hold all content
    banner = Image.new("RGB", (total_width, LED_ROWS), BACKGROUND_COLOR)
    
    # Paste all images with spacing
    x_offset = 0
    for img in images:
        banner.paste(img, (x_offset, 0))
        x_offset += img.width + spacing
    
    return banner

def scroll_content(image, speed, loops=2):
    """Scroll the content across the screen with continuous flow
    
    The image will be displayed for the specified number of loops,
    with each loop being one complete pass of the content.
    """
    width = image.width
    
    # For each loop, we need to scroll the entire width of the image
    total_scroll_distance = width * loops
    
    # Start position (image is just off-screen to the right)
    offset = 0
    
    while offset < total_scroll_distance:
        if check_quit():
            return False
        
        # Create frame for current view
        frame = Image.new("RGB", (LED_COLS, LED_ROWS), BACKGROUND_COLOR)
        
        # Update and draw fireworks first (as background)
        firework_system.update()
        frame = firework_system.draw(frame)
        
        # Copy pixels from the image to the frame
        for x in range(LED_COLS):
            # Calculate the source x position in the scrolling image
            src_x = (offset + x) % width
            
            # Copy pixel column
            for y in range(LED_ROWS):
                r, g, b = image.getpixel((src_x, y))
                if r or g or b:  # Only copy non-black pixels
                    frame.putpixel((x, y), (r, g, b))
        
        # Display frame
        pygame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
        scaled = pygame.transform.scale(pygame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        screen.fill(BACKGROUND_COLOR)
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        
        # Move to next position
        offset += 2  # Controls scroll speed
        time.sleep(speed)
        clock.tick(FPS)
    
    return True

def main_loop():
    announcements = [
        "CAPSTONE DEMO IN PROGRESS!",
        "PENN STATE ENGINEERING",
        "Built by Jacob, Stevie, Ben W, Ben R, Mason, Muhannad, Sophia, Maddalena, Nick, Sami",
    ]
    
    running = True
    
    while running:
        # Get fresh time/weather data
        time_weather_img = render_time_weather()
        
        # Create all announcement images
        announcement_images = [render_announcement(text) for text in announcements]
        
        # Create a continuous banner with time/weather followed by all announcements
        # This ensures seamless flow between content items
        all_content = [time_weather_img] + announcement_images
        
        # Duplicate the first content (time/weather) to add at the end for a smooth loop
        all_content.append(time_weather_img)
        
        # Create the continuous banner with spacing between items
        continuous_banner = create_continuous_banner(all_content, spacing=60)
        
        # Scroll the entire banner continuously
        if not scroll_content(continuous_banner, SCROLL_SPEED_MAIN, loops=1):
            running = False
            break

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        pygame.quit()
