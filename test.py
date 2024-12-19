import pygame
import math

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rotating Rectangle")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Create a rectangle surface
rect_width, rect_height = 100, 50
rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)  # Alpha for transparency
rect_surface.fill(BLUE)

# Center position
center_x, center_y = 400, 300

# Rotation angle
angle = 0

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)

    # Rotate the rectangle
    rotated_surface = pygame.transform.rotate(rect_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))

    # Draw the rotated rectangle
    screen.blit(rotated_surface, rotated_rect.topleft)

    # Update the angle
    angle += 1
    angle %= 360  # Keep angle in range [0, 360]

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()
