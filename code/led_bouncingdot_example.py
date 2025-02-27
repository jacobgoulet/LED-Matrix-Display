import pygame # type: ignore
import time
import random

# Simulation Setup
PANEL_WIDTH = 16
PANEL_HEIGHT = 16
PIXEL_SIZE = 16  # Scale factor for visibility

# Colors
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0,255,0)
# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((PANEL_WIDTH * PIXEL_SIZE, PANEL_HEIGHT * PIXEL_SIZE))
pygame.display.set_caption("16x16 LED Panel Simulation")

# Bouncing Dot Setup
x_pos = random.randint(0, PANEL_WIDTH - 1)
y_pos = random.randint(0, PANEL_HEIGHT - 1)
x_dir = 1  # Moving right
y_dir = 1  # Moving down

running = True
while running:
    screen.fill(BLACK)  # Clear screen
    
    # Draw the red dot
    pygame.draw.rect(screen, RED, 
                     (x_pos * PIXEL_SIZE, y_pos * PIXEL_SIZE, 
                      PIXEL_SIZE, PIXEL_SIZE))
    pygame.draw.rect(screen, GREEN, 
                     (100, 100, 
                      PIXEL_SIZE, PIXEL_SIZE))
    # Update display
    pygame.display.flip()
    time.sleep(0.1)  # Adjust speed
    
    # Move the dot
    x_pos += x_dir
    y_pos += y_dir
    
    # Bounce off walls
    if x_pos <= 0 or x_pos >= PANEL_WIDTH - 1:
        x_dir *= -1  # Reverse X direction
    if y_pos <= 0 or y_pos >= PANEL_HEIGHT - 1:
        y_dir *= -1  # Reverse Y direction

    # Quit if window is closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()





#code conversion to real raspberry pi matrix
'''
import board
import neopixel
import time
import random

# LED Matrix Setup
LED_PIN = board.D18  # GPIO pin connected to the matrix's DIN
PANEL_WIDTH = 16
PANEL_HEIGHT = 16
NUM_LEDS = PANEL_WIDTH * PANEL_HEIGHT

# Initialize LED Matrix
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=0.5, auto_write=False)

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Bouncing Dot Setup
x_pos = random.randint(0, PANEL_WIDTH - 1)
y_pos = random.randint(0, PANEL_HEIGHT - 1)
x_dir = 1  # Moving right
y_dir = 1  # Moving down

# Convert (x, y) to LED index for zigzag layout
def get_led_index(x, y):
    if y % 2 == 0:  # Even rows left to right
        return y * PANEL_WIDTH + x
    else:           # Odd rows right to left (zigzag)
        return y * PANEL_WIDTH + (PANEL_WIDTH - 1 - x)

# Animation Loop
while True:
    pixels.fill(BLACK)  # Clear screen

    # Draw the bouncing red dot
    pixels[get_led_index(x_pos, y_pos)] = RED

    # Draw the fixed green dot at (100, 100) in Pygame units
    # Mapping (100, 100) to LED matrix coordinates
    green_x = 100 // PANEL_WIDTH
    green_y = 100 // PANEL_HEIGHT
    pixels[get_led_index(green_x, green_y)] = GREEN
    
    # Update LED matrix
    pixels.show()
    time.sleep(0.1)  # Adjust speed

    # Move the red dot
    x_pos += x_dir
    y_pos += y_dir
    
    # Bounce off walls
    if x_pos <= 0 or x_pos >= PANEL_WIDTH - 1:
        x_dir *= -1  # Reverse X direction
    if y_pos <= 0 or y_pos >= PANEL_HEIGHT - 1:
        y_dir *= -1  # Reverse Y direction
'''