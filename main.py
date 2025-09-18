import pygame
import sys
import json
from maze import Maze
from player import Player
from level_manager import LevelManager

# Khởi tạo Pygame
pygame.init()

CELL_SIZE = 40
screen = pygame.display.set_mode((800, 600))  # Màn hình mặc định, sẽ điều chỉnh sau
pygame.display.set_caption("Ice Maze Puzzle - Collect Pellets")
clock = pygame.time.Clock()

# Load assets
TILE_IMAGES = {
    0: pygame.image.load('assets/tiles/floor.png'),
    1: pygame.image.load('assets/tiles/wall.png'),
    3: pygame.image.load('assets/tiles/pellet.png'),
    4: pygame.image.load('assets/tiles/obstacle.png')
}
PLAYER_IMAGES = {
    'behind': pygame.image.load('assets/player/sprite_behind.png'),
    'front': pygame.image.load('assets/player/sprite_front.png'),
    'right': pygame.image.load('assets/player/sprite_right.png'),
    'left': pygame.transform.flip(pygame.image.load('assets/player/sprite_right.png'), True, False)
}
for direction in PLAYER_IMAGES:
    PLAYER_IMAGES[direction] = pygame.transform.scale(PLAYER_IMAGES[direction], (CELL_SIZE, CELL_SIZE))

# Font
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Load progress
try:
    with open('progress.json', 'r') as f:
        progress = json.load(f)
        completed = progress.get('completed', [])
except FileNotFoundError:
    completed = []

# Quản lý level
level_manager = LevelManager('levels/')
NUM_LEVELS = 3
state = 'menu'
current_level_num = 1
maze = None
player = None
win_text = None

class WinText:
    def __init__(self):
        self.original_text = font.render("You Win!", True, (0, 0, 0))
        self.scale = 0.5
        self.start_time = pygame.time.get_ticks()
        self.done = False

    def update(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.scale = 0.5 + elapsed * 1.5
        if elapsed > 1.0:
            self.done = True

    def draw(self, screen):
        scaled_text = pygame.transform.scale(self.original_text, 
                                             (int(self.original_text.get_width() * self.scale), 
                                              int(self.original_text.get_height() * self.scale)))
        screen.blit(scaled_text, (screen.get_width() // 2 - scaled_text.get_width() // 2, 
                                  screen.get_height() // 2 - scaled_text.get_height() // 2))

def draw_menu():
    screen.fill((200, 200, 255))
    title_text = font.render("Select Level", True, (0, 0, 0))
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 50))

    max_unlocked = max(completed + [0]) + 1
    for i in range(1, NUM_LEVELS + 1):
        button_rect = pygame.Rect(100, 100 + (i - 1) * 60, 200, 50)
        color = (0, 255, 0) if i in completed else (255, 0, 0) if i > max_unlocked else (0, 0, 255)
        pygame.draw.rect(screen, color, button_rect)
        level_text = small_font.render(f"Level {i}", True, (255, 255, 255))
        screen.blit(level_text, (button_rect.centerx - level_text.get_width() // 2, 
                                 button_rect.centery - level_text.get_height() // 2))
        if i in completed:
            check_text = small_font.render("✓", True, (0, 255, 0))
            screen.blit(check_text, (button_rect.right - 30, button_rect.centery - check_text.get_height() // 2))

    pygame.display.flip()
    return max_unlocked

running = True
while running:
    if state == 'menu':
        max_unlocked = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i in range(1, NUM_LEVELS + 1):
                    button_rect = pygame.Rect(100, 100 + (i - 1) * 60, 200, 50)
                    if button_rect.collidepoint(mouse_pos) and i <= max_unlocked:
                        current_level_num = i
                        current_level = level_manager.load_level(i)
                        # Điều chỉnh kích thước màn hình dựa trên ma trận
                        WIDTH = len(current_level[0])
                        HEIGHT = len(current_level)
                        SCREEN_WIDTH = WIDTH * CELL_SIZE
                        SCREEN_HEIGHT = HEIGHT * CELL_SIZE
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        maze = Maze(current_level, TILE_IMAGES, CELL_SIZE)
                        player = Player(maze.start_x, maze.start_y, PLAYER_IMAGES, CELL_SIZE)
                        state = 'playing'

    elif state == 'playing':
        screen.fill((200, 200, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1, maze)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1, maze)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0, maze)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0, maze)
                elif event.key == pygame.K_r:
                    state = 'menu'

        player.update(maze)
        maze.draw(screen)
        player.draw(screen)

        if not maze.has_pellets():
            win_text = WinText()
            state = 'win'

        pygame.display.flip()

    elif state == 'win':
        screen.fill((200, 200, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win_text.update()
        maze.draw(screen)
        player.draw(screen)
        win_text.draw(screen)
        pygame.display.flip()

        if win_text.done:
            if current_level_num not in completed:
                completed.append(current_level_num)
                with open('progress.json', 'w') as f:
                    json.dump({'completed': sorted(completed)}, f)
            state = 'menu'

    clock.tick(60)

pygame.quit()
sys.exit()