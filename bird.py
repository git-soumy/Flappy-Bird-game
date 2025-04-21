import pygame
import random
import sys
import time
import os  # Added for file handling

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Cute Bird with Emotions")

# Colors
DAY_COLOR = (135, 206, 250)
NIGHT_COLOR = (25, 25, 112)
WHITE = (255, 255, 255)
GREEN = (0, 250, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)

# High score file
HIGH_SCORE_FILE = "flappy_bird_highscore.txt"

# Function to load high score
def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                return int(file.read())
    except:
        pass  # If any error occurs, just return 0
    return 0

# Function to save high score
def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(str(score))
    except:
        pass  # Silently fail if we can't save

# Load high score at startup
high_score = load_high_score()

# Load bird images
bird_happy = pygame.image.load("bird.png").convert_alpha()
bird_sad = pygame.image.load("8cbfc1b30d5da2a0c29be43aff948261.png").convert_alpha()
bird_image = bird_happy

# Resize bird image
bird_img_size = (60, 60)
bird_happy = pygame.transform.scale(bird_happy, bird_img_size)
bird_sad = pygame.transform.scale(bird_sad, bird_img_size)

# Bird setup
gravity = 0.5
bird_movement = 0
score = 0
game_active = True
bird = pygame.Rect(100, 300, *bird_img_size)

# Pipe setup
pipe_width = 70
pipe_gap = 150
pipe_list = []

font = pygame.font.SysFont("Arial", 28)
clock = pygame.time.Clock()

# Powerup variables
active_powerup = None
powerup_end_time = 0
shield_active = False
double_points = False
slow_motion = False

# Theme switching
day_theme = True
last_theme_switch = time.time()

# Cheat mode
no_collision = False

# Timers
SPAWNPIPE = pygame.USEREVENT
SPAWNPOWER = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, 1500)
pygame.time.set_timer(SPAWNPOWER, 7000)

def create_pipe():
    height = random.randint(100, 400)
    top = pygame.Rect(WIDTH, 0, pipe_width, height)
    bottom = pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT)
    return {"top": top, "bottom": bottom, "scored": False}

def spawn_powerup():
    kind = random.choice(["shield", "double", "slow"])
    rect = pygame.Rect(WIDTH, random.randint(100, 500), 30, 30)
    return {"rect": rect, "type": kind}

powerups = []

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score(high_score)  # Save high score before quitting
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -8
            elif event.key == pygame.K_SPACE and not game_active:
                bird.center = (100, 300)
                pipe_list.clear()
                powerups.clear()
                bird_movement = 0
                score = 0
                active_powerup = None
                game_active = True
                shield_active = False
                double_points = False
                slow_motion = False
                no_collision = False
                bird_image = bird_happy  # Reset to happy bird when restarting game

            elif event.key == pygame.K_p:
                no_collision = not no_collision
                print("No Collision Mode:", no_collision)

        if event.type == SPAWNPIPE and game_active:
            pipe_list.append(create_pipe())

        if event.type == SPAWNPOWER and game_active:
            powerups.append(spawn_powerup())

    if time.time() - last_theme_switch >= 20:
        day_theme = not day_theme
        last_theme_switch = time.time()

    SCREEN.fill(DAY_COLOR if day_theme else NIGHT_COLOR)

    if game_active:
        bird_movement += gravity
        bird.y += bird_movement
        SCREEN.blit(bird_image, bird.topleft)

        # Pipe handling
        new_pipe_list = []
        for pipe in pipe_list:
            speed = 2 if slow_motion else 4
            pipe["top"].x -= speed
            pipe["bottom"].x -= speed

            pygame.draw.rect(SCREEN, GREEN, pipe["top"])
            pygame.draw.rect(SCREEN, GREEN, pipe["bottom"])

            if pipe["top"].right > 0:
                new_pipe_list.append(pipe)

            if not no_collision and (bird.colliderect(pipe["top"]) or bird.colliderect(pipe["bottom"])):
                if shield_active:
                    shield_active = False
                else:
                    bird_image = bird_sad  # Show sad bird when collision occurs
                    game_active = False
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)  # Save new high score immediately

            if pipe["bottom"].right < bird.left and not pipe["scored"]:
                score += 2 if double_points else 1
                pipe["scored"] = True

        pipe_list = new_pipe_list

        # Powerup handling
        for p in powerups[:]:
            p["rect"].x -= 3
            color = YELLOW if p["type"] == "shield" else PURPLE if p["type"] == "double" else WHITE
            pygame.draw.rect(SCREEN, color, p["rect"])

            if bird.colliderect(p["rect"]):
                active_powerup = p["type"]
                powerup_end_time = pygame.time.get_ticks() + 5000
                powerups.remove(p)

        if active_powerup:
            now = pygame.time.get_ticks()
            if now < powerup_end_time:
                shield_active = active_powerup == "shield"
                double_points = active_powerup == "double"
                slow_motion = active_powerup == "slow"
            else:
                active_powerup = None
                shield_active = False
                double_points = False
                slow_motion = False

        # Wall collision
        if bird.top <= 0 or bird.bottom >= HEIGHT:
            if not no_collision:
                if shield_active:
                    shield_active = False
                else:
                    bird_image = bird_sad
                    game_active = False
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)  # Save new high score immediately

        # Score and info display
        SCREEN.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        SCREEN.blit(font.render(f"High Score: {high_score}", True, WHITE), (10, 40))
        if active_powerup:
            SCREEN.blit(font.render(f"{active_powerup.upper()} ACTIVE", True, WHITE), (10, 70))
        if no_collision:
            SCREEN.blit(font.render("CHEAT MODE ON", True, RED), (10, 100))

    else:
        # When game is over, just show the score and message without the bird image
        SCREEN.blit(font.render("Game Over! Press SPACE to restart", True, WHITE), (20, HEIGHT // 2 - 30))
        SCREEN.blit(font.render(f"Score: {score}  High Score: {high_score}", True, WHITE), (60, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
