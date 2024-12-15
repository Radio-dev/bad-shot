import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Fullscreen dimensions
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Create the screen object for the display surface
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Clock for frame rate
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# High score file
HIGH_SCORE_FILE = "high_score.txt"

# High score encryption mapping
ENCODE_MAP = {"1": "a", "2": "z", "3": "b", "4": "x", "5": "c", "6": "y", "7": "d", "8": "w", "9": "e", "0": "u"}
DECODE_MAP = {v: k for k, v in ENCODE_MAP.items()}

def encode_score(score):
    """Encodes the score using the custom encryption."""
    return "".join(ENCODE_MAP.get(digit, digit) for digit in str(score))

def decode_score(encoded_score):
    """Decodes the encrypted score back to an integer."""
    return int("".join(DECODE_MAP.get(char, char) for char in encoded_score))

def load_high_score():
    """Loads and decodes the high score from a file or initializes it."""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            try:
                return decode_score(file.read().strip())
            except ValueError:
                return 0
    return 0

def save_high_score(high_score):
    """Encodes and saves the high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(encode_score(high_score))

# Load initial high score
high_score = load_high_score()

# Game states
TITLE_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
game_state = TITLE_SCREEN

# Player settings
player_size = 40
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5

# Enemy settings
enemy_size = 40
enemies = []
enemy_speed = 3
first_enemy_delay = 4000  # Delay for the first enemy (4 seconds)
enemy_spawn_delay = 1000  # Delay for subsequent enemies (1 second)
last_enemy_spawn_time = 0
first_enemy_spawned = False

# Bullet settings
bullets = []
bullet_speed = 10
bullet_size = 10

# Score
score = 0

# Load background image for title screen and game
background_image_path_title = r"C:\Program Files (x86)\bad shot\tbackg.png"
background_image_path_game = r"C:\Program Files (x86)\bad shot\ok.png"

# Check if background images exist and load them
if os.path.exists(background_image_path_title):
    title_screen_bg = pygame.image.load(background_image_path_title)
    title_screen_bg = pygame.transform.scale(title_screen_bg, (WIDTH, HEIGHT))
else:
    title_screen_bg = None

if os.path.exists(background_image_path_game):
    game_bg = pygame.image.load(background_image_path_game)
    game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))
else:
    game_bg = None

def draw_text(text, font, color, surface, x, y):
    """Utility function to draw centered text."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

        # Title screen controls
        if game_state == TITLE_SCREEN:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = GAME_RUNNING
                last_enemy_spawn_time = current_time

        # Game over controls
        if game_state == GAME_OVER:
            if score > high_score:  # Check if current score is higher than high score
                high_score = score  # Update high score
                save_high_score(high_score)  # Save the new high score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game_state = GAME_RUNNING
                player_pos = [WIDTH // 2, HEIGHT // 2]
                enemies = []
                bullets = []
                last_enemy_spawn_time = current_time
                first_enemy_spawned = False
                score = 0

        # Shooting mechanic during gameplay
        if game_state == GAME_RUNNING and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            bullet_direction = [mouse_x - player_pos[0], mouse_y - player_pos[1]]
            magnitude = (bullet_direction[0]**2 + bullet_direction[1]**2)**0.5
            bullet_direction[0] /= magnitude
            bullet_direction[1] /= magnitude
            bullets.append({
                "pos": [player_pos[0] + player_size // 2, player_pos[1] + player_size // 2],
                "dir": bullet_direction
            })

    if game_state == TITLE_SCREEN:
        screen.fill(WHITE)
        if title_screen_bg:
            screen.blit(title_screen_bg, (0, 0))  # Blit background image for title screen

    elif game_state == GAME_RUNNING:
        # Set the background for the game screen
        if game_bg:
            screen.blit(game_bg, (0, 0))  # Blit background image for the game
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos[1] -= player_speed
        if keys[pygame.K_s]:
            player_pos[1] += player_speed
        if keys[pygame.K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_d]:
            player_pos[0] += player_speed

        if not first_enemy_spawned:
            if current_time - last_enemy_spawn_time > first_enemy_delay:
                enemy_pos = [random.randint(0, WIDTH - enemy_size), random.randint(0, HEIGHT - enemy_size)]
                enemies.append(enemy_pos)
                last_enemy_spawn_time = current_time
                first_enemy_spawned = True
        else:
            if current_time - last_enemy_spawn_time > enemy_spawn_delay:
                enemy_pos = [random.randint(0, WIDTH - enemy_size), random.randint(0, HEIGHT - enemy_size)]
                enemies.append(enemy_pos)
                last_enemy_spawn_time = current_time

        for enemy_pos in enemies:
            if enemy_pos[0] < player_pos[0]:
                enemy_pos[0] += enemy_speed
            else:
                enemy_pos[0] -= enemy_speed

            if enemy_pos[1] < player_pos[1]:
                enemy_pos[1] += enemy_speed
            else:
                enemy_pos[1] -= enemy_speed

        for bullet in bullets[:]:
            bullet["pos"][0] += bullet["dir"][0] * bullet_speed
            bullet["pos"][1] += bullet["dir"][1] * bullet_speed
            if (bullet["pos"][0] < 0 or bullet["pos"][0] > WIDTH or
                    bullet["pos"][1] < 0 or bullet["pos"][1] > HEIGHT):
                bullets.remove(bullet)

        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet["pos"][0], bullet["pos"][1], bullet_size, bullet_size)
            for enemy_pos in enemies[:]:
                enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy_pos)
                    bullets.remove(bullet)
                    score += 1
                    break

        player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
        for enemy_pos in enemies:
            enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_state = GAME_OVER

        pygame.draw.rect(screen, BLUE, (player_pos[0], player_pos[1], player_size, player_size))
        for enemy_pos in enemies:
            pygame.draw.rect(screen, RED, (enemy_pos[0], enemy_pos[1], enemy_size, enemy_size))
        for bullet in bullets:
            pygame.draw.circle(screen, BLACK, (int(bullet["pos"][0]), int(bullet["pos"][1])), bullet_size)

        score_text = small_font.render(f"Score: {score}", True, BLACK)
        high_score_text = small_font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

    elif game_state == GAME_OVER:
        screen.fill(WHITE)
        draw_text("Game Over", font, RED, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Final Score: {score}", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text(f"High Score: {high_score}", small_font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Press R to Restart", small_font, GRAY, screen, WIDTH // 2, HEIGHT // 2 + 100)

    pygame.display.flip()
    clock.tick(FPS)
