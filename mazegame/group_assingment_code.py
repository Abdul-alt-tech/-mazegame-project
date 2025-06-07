#Music by <a href="https://pixabay.com/users/sapan4-1742806/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=335408">sapan patel</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=335408">Pixabay</a>
#Music by <a href="https://pixabay.com/users/fassounds-3433550/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=259703">FASSounds</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=259703">Pixabay</a>
import os
import pygame
import random
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque

pygame.init()
pygame.mixer.init()

# Global volume settings
music_volume = 0.5
effects_volume = 0.5
pygame.mixer.music.set_volume(music_volume)

# Load player move sound globally.
try:
    move_sound = pygame.mixer.Sound(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\sound\mixkit-martial-arts-fast-punch-2047.wav")
    move_sound.set_volume(effects_volume)
except Exception as e:
    print("Error loading move sound:", e)
    move_sound = None

# Set Game Icon
try:
    icon_path = r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\gameicon\falling-blob.png"
    icon_img = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_img)
    print("Game icon set successfully.")
except pygame.error as e:
    print(f"Error loading icon image: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Initialize Pygame mixer and play background music
try:
    pygame.mixer.music.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\backgroundmusic\edm-gaming-music-335408.MP3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except Exception as e:
    print("Error loading background music:", e)

# Load level selection sound
try:
    level_select_sound = pygame.mixer.Sound(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\backgroundmusic\play-time-fun-upbeat-gaming-birthday-music-259703.MP3")
    level_select_sound.set_volume(effects_volume)
except Exception as e:
    print("Error loading level select sound:", e)
    level_select_sound = None

# ── Added: Load threat‐hit warning sound ──
try:
    threat_hit_sound = pygame.mixer.Sound(
        r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\threat\mixkit-sci-fi-positive-notification-266.wav"
    )
    threat_hit_sound.set_volume(effects_volume)
except Exception as e:
    print("Error loading threat hit sound:", e)
    threat_hit_sound = None

pygame.key.set_repeat(200, 50)  # Enables continuous movement when keys are held

# ---------------------------
# Leaderboard Functions
# ---------------------------
def load_leaderboard_file():
    leaderboard = []
    try:
        filpath =  r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\leaderboard.txt"
        with open(filpath, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 2:
                        name = parts[0]
                        try:
                            score = int(parts[1])
                        except:
                            score = 0
                        leaderboard.append((name, score))
    except Exception as e:
        print("Error loading leaderboard:", e)
    return leaderboard

def save_leaderboard_file(leaderboard):
    try:
        filpath = r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\leaderboard.txt"
        with open(filpath, "r") as f:
        
            for name, score in leaderboard:
                f.write(f"{name},{score}\n")
    except Exception as e:
        print("Error saving leaderboard:", e)

def update_leaderboard(name, score):
    leaderboard = load_leaderboard_file()
    leaderboard.append((name, score))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    leaderboard = leaderboard[:10]  # Keep top 10 scores
    save_leaderboard_file(leaderboard)

def display_leaderboard():
    leaderboard = load_leaderboard_file()
    if not leaderboard:
        return "No scores yet."
    lines = [f"{i+1}. {name}: {score}" for i, (name, score) in enumerate(leaderboard)]
    return "\n".join(lines)


# Utility Functions for High Score

def load_high_score():
    try:
        filpath = r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\highscore.txt"
        with open(filpath, "r") as f:
        
            return int(f.read().strip())
    except Exception as e:
        print("Error loading high score:", e)
        return 0

def save_high_score(score):
    try:
        filpath = r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\highscore.txt"
        with open(filpath, "r") as f:
        
            f.write(str(score))
    except Exception as e:
        print("Error saving high score:", e)


# Helper Function: Get Random Goal in Top-Right Quadrant

def get_random_goal(cols, rows):
    valid_x = [x for x in range(cols // 2, cols - 1) if x % 2 == 1]
    valid_y = [y for y in range(1, rows // 2 + 1) if y % 2 == 1]
    goal = [random.choice(valid_x), random.choice(valid_y)]
    print(f"Random goal chosen at: {goal}")
    return goal


# Color Constants

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GREEN   = (0, 255, 0)
RED     = (255, 0, 0)
BLUE    = (0, 0, 255)
YELLOW  = (255, 255, 0)
PURPLE  = (128, 0, 128)
ORANGE  = (255, 165, 0)
CYAN    = (0, 255, 255)
MAGENTA = (255, 0, 255)


# Maze Class – With Path Background Image and Wall Image for Walls

class Maze:
    def __init__(self, cols, rows, tile_size, goal_pos):
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.goal_pos = goal_pos
        self.grid = [[1] * cols for _ in range(rows)]
        self.generate()
        # Load the path background image for walkable cells.
        self.path_tile = self.generate_path_tile(tile_size)
        self.wall_tile = self.load_wall_tile(tile_size)

    def generate(self):
        m = [[1] * self.cols for _ in range(self.rows)]
        stack = [(1, 1)]
        m[1][1] = 0
        while stack:
            x, y = stack[-1]
            dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx * 2, y + dy * 2
                if 1 <= nx < self.cols - 1 and 1 <= ny < self.rows - 1 and m[ny][nx] == 1:
                    m[ny][nx] = 0
                    m[y + dy][x + dx] = 0
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()
        gx, gy = self.goal_pos
        m[gy][gx] = 0
        self.grid = m
        self.add_extra_paths(probability=0.1)

    def add_extra_paths(self, probability=0.1):
        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):
                if self.grid[y][x] == 1:
                    if ((self.grid[y][x-1] == 0 and self.grid[y][x+1] == 0) or 
                        (self.grid[y-1][x] == 0 and self.grid[y+1][x] == 0)):
                        if random.random() < probability:
                            self.grid[y][x] = 0

    def generate_path_tile(self, tile_size):
        try:
            path_image = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\gamepath\37e76650-136e-47a6-bd21-ddb63e4f4c77.JPG")
            path_image = pygame.transform.scale(path_image, (tile_size, tile_size))
            return path_image
        except Exception as e:
            print("Error loading path background image:", e)
            tile = pygame.Surface((tile_size, tile_size))
            tile.fill((50, 200, 50))
            return tile

    def load_wall_tile(self, tile_size):
        try:
            wall_image = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\wall image\4747369.JPG")
            wall_image = pygame.transform.scale(wall_image, (tile_size, tile_size))
            return wall_image
        except Exception as e:
            print("Error loading wall image:", e)
            return None

    def draw(self, screen):
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == 1:
                    if self.wall_tile:
                        screen.blit(self.wall_tile, (x * self.tile_size, y * self.tile_size))
                    else:
                        pygame.draw.rect(screen, WHITE, (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
                else:
                    screen.blit(self.path_tile, (x * self.tile_size, y * self.tile_size))


# Updated Player Class – Using an Image as the Player Sprite and Running Animation

class Player:
    def __init__(self, start_pos, image_path, scale):
        self.pos = list(start_pos)
        try:
            self.image = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\playericon\steering-wheel_8033924.png")
            self.image = pygame.transform.scale(self.image, (scale, scale))
        except Exception as e:
            print("Error loading player image:", e)
            self.image =None
        self.moves_count = 0

        # ── Added: Load running monkey frames for animation ──
        self.run_images = []
        try:
            for i in range(1, 5):
                frame = pygame.image.load(
                    rf"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\playericon\round-struck{i}.png"
                )
                frame = pygame.transform.scale(frame, (scale, scale))
                self.run_images.append(frame)
        except Exception as e:
            print("Error loading running frames:", e)
        self.current_run_frame = 0

    def can_move(self, dx, dy, maze):
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy
        if new_x < 0 or new_x >= maze.cols or new_y < 0 or new_y >= maze.rows:
            return False
        if maze.grid[new_y][new_x] != 0:
            return False
        return True

    def move(self, dx, dy, maze):
        if self.can_move(dx, dy, maze):
            self.pos[0] += dx
            self.pos[1] += dy
            self.moves_count += 1
            if move_sound:
                move_sound.play()
            # ── Added: Cycle running frames on movement ──
            if self.run_images:
                self.current_run_frame = (self.current_run_frame + 1) % len(self.run_images)
                self.image = self.run_images[self.current_run_frame]

    def draw(self, screen, tile_size):
        if self.image:
            rect = self.image.get_rect()
            rect.center = (self.pos[0] * tile_size + tile_size // 2,
                           self.pos[1] * tile_size + tile_size // 2)
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, GREEN,
                               (self.pos[0] * tile_size + tile_size // 2,
                                self.pos[1] * tile_size + tile_size // 2),
                               tile_size // 2)

# ---------------------------
# Updated AIOpponent Class – Using an Image as the Opponent Sprite
# ---------------------------
class AIOpponent:
    def __init__(self, start_pos, goal_pos, difficulty, level, image_path, scale):
        self.pos = list(start_pos)
        self.goal = goal_pos
        self.speed = self.set_speed(difficulty, level)
        self.move_counter = 0
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (scale, scale))
        except Exception as e:
            print("Error loading opponent image:", e)
            self.image = None

    def set_speed(self, difficulty, level):
        if difficulty == "easy":
            base_speed = 15
            decrement = level - 1
            return max(base_speed - decrement, 5)
        elif difficulty == "medium":
            base_speed = 11
            decrement = level - 1
            return max(base_speed - decrement, 3)
        elif difficulty == "hard":
            base_speed = 7
            decrement = level - 1
            return max(base_speed - decrement, 2)
        else:
            return 10

    def move(self, maze):
        self.move_counter += 1
        if self.move_counter >= self.speed:
            self.move_counter = 0
            self.make_move(maze)

    def make_move(self, maze):
        path = compute_path(maze, self.pos, self.goal)
        if path and len(path) > 1:
            self.pos = list(path[1])
        else:
            valid_moves = []
            x, y = self.pos
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze.cols and 0 <= ny < maze.rows and maze.grid[ny][nx] == 0:
                    valid_moves.append((nx, ny))
            if valid_moves:
                self.pos = list(random.choice(valid_moves))

    def draw(self, screen, tile_size):
        if self.image:
            rect = self.image.get_rect()
            rect.center = (self.pos[0] * tile_size + tile_size // 2,
                           self.pos[1] * tile_size + tile_size // 2)
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, BLUE,
                               (self.pos[0] * tile_size + tile_size // 2,
                                self.pos[1] * tile_size + tile_size // 2),
                               15)

# ---------------------------
# Updated Threat Class – Using an Image as the Threat Sprite
# ---------------------------
class Threat:
    def __init__(self, pos, behavior, move_speed):
        self.pos = list(pos)
        self.behavior = behavior
        self.move_speed = move_speed
        self.move_counter = 0
        try:
            self.image = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\threat\fire.png")
        except Exception as e:
            print("Error loading threat image:", e)
            self.image = None

    def move(self, maze, player_pos=None):
        self.move_counter += 1
        if self.move_counter < self.move_speed:
            return
        self.move_counter = 0
        x, y = self.pos
        moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.cols and 0 <= ny < maze.rows and maze.grid[ny][nx] == 0:
                moves.append((nx, ny))
        if not moves:
            return
        if self.behavior == 'chase' and player_pos is not None:
            best_move = min(moves, key=lambda m: abs(m[0] - player_pos[0]) + abs(m[1] - player_pos[1]))
            self.pos = list(best_move)
        else:
            self.pos = list(random.choice(moves))

    def draw(self, screen, tile_size):
        if self.image:
            threat_image = pygame.transform.scale(self.image, (tile_size, tile_size))
            screen.blit(threat_image, (self.pos[0] * tile_size, self.pos[1] * tile_size))
        else:
            pygame.draw.rect(screen, RED,
                             (self.pos[0] * tile_size, self.pos[1] * tile_size,
                              tile_size, tile_size))

# ---------------------------
# PowerUp Class
# ---------------------------
class PowerUp:
    def __init__(self, pos, type):
        self.pos = list(pos)
        self.type = type

    def draw(self, screen, tile_size):
        if self.type == "extra_moves":
            color = ORANGE
        elif self.type == "hint":
            color = CYAN
        elif self.type == "teleportation":
            color = MAGENTA
        pygame.draw.circle(screen, color,
                           (self.pos[0] * tile_size + tile_size // 2,
                            self.pos[1] * tile_size + tile_size // 2),
                           tile_size // 3)

# ---------------------------
# GameStatistics Class (HUD and Session Stats)
# ---------------------------  
class GameStatistics:
    def __init__(self, moves_left, timer, trials, high_score=0):
        self.moves_left = moves_left
        self.timer = timer
        self.trials = trials
        self.high_score = high_score
        self.games_played = 0
        self.games_won = 0
        self.fastest_escape = None
        self.initial_moves = moves_left

    def update(self, delta_time):
        self.timer -= delta_time

    def draw(self, screen, screen_width, level, player):
        font = pygame.font.Font(None, 28)
        stats_width = 220
        stats_height = 250
        stats_surface = pygame.Surface((stats_width, stats_height))
        stats_surface.set_alpha(220)
        stats_surface.fill((50, 50, 50))
        pygame.draw.rect(stats_surface, WHITE, stats_surface.get_rect(), 2)
        
        timer_text = font.render(f"Timer: {int(self.timer)} s", True, WHITE)
        moves_text = font.render(f"Moves Left: {self.moves_left}", True, WHITE)
        score = player.moves_count // 2
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        games_text = font.render(f"Games Played: {self.games_played}", True, WHITE)
        wins_text = font.render(f"Wins: {self.games_won}", True, WHITE)
        win_percent = (self.games_won / self.games_played * 100) if self.games_played > 0 else 0
        win_percent_text = font.render(f"Win %: {win_percent:.2f}%", True, WHITE)
        fastest_text = font.render(f"Fastest Escape: {self.fastest_escape if self.fastest_escape is not None else 'N/A'} moves", True, WHITE)
        
        stats_surface.blit(timer_text, (10, 10))
        stats_surface.blit(moves_text, (10, 35))
        stats_surface.blit(score_text, (10, 60))
        stats_surface.blit(high_score_text, (10, 85))
        stats_surface.blit(level_text, (10, 110))
        stats_surface.blit(games_text, (10, 135))
        stats_surface.blit(wins_text, (10, 160))
        stats_surface.blit(win_percent_text, (10, 185))
        stats_surface.blit(fastest_text, (10, 210))
        
        screen.blit(stats_surface, (screen_width - stats_width - 10, 10))

# ---------------------------
# UserInterface Class
# ---------------------------  
class UserInterface:
    def __init__(self, screen, maze, player, ai_opponent, threats, powerups, tile_size):
        self.screen = screen
        self.maze = maze
        self.player = player
        self.ai_opponent = ai_opponent
        self.threats = threats
        self.powerups = powerups
        self.tile_size = tile_size
        self.panel_margin = 10
        self.MINIMAP_SCALE = 0.2
        self.MINI_TILE = int(tile_size * self.MINIMAP_SCALE)
        self.MINIMAP_WIDTH = self.maze.cols * self.MINI_TILE
        self.MINIMAP_HEIGHT = self.maze.rows * self.MINI_TILE
        self.LEGEND_WIDTH, self.LEGEND_HEIGHT = 150, 60
        self.panel_width = max(self.MINIMAP_WIDTH, self.LEGEND_WIDTH)
        self.panel_height = self.MINIMAP_HEIGHT + 10 + self.LEGEND_HEIGHT
        self.panel_x = self.screen.get_width() - self.panel_width - self.panel_margin
        self.panel_y = self.screen.get_height() - self.panel_height - self.panel_margin
        self.minimap_pos = (self.panel_x, self.panel_y)
        self.legend_pos = (self.panel_x, self.panel_y + self.MINIMAP_HEIGHT + 10)

    def draw_minimap(self):
        mini_surface = pygame.Surface((self.MINIMAP_WIDTH, self.MINI_TILE * self.maze.rows))
        for y in range(self.maze.rows):
            for x in range(self.maze.cols):
                rect = pygame.Rect(x * self.MINI_TILE, y * self.MINI_TILE, self.MINI_TILE, self.MINI_TILE)
                color = WHITE if self.maze.grid[y][x] == 1 else BLACK
                pygame.draw.rect(mini_surface, color, rect)
        def mini_center(pos):
            return (pos[0] * self.MINI_TILE + self.MINI_TILE // 2,
                    pos[1] * self.MINI_TILE + self.MINI_TILE // 2)
        pygame.draw.circle(mini_surface, GREEN, mini_center(self.player.pos), self.MINI_TILE // 2)
        pygame.draw.circle(mini_surface, YELLOW, mini_center(self.maze.goal_pos), self.MINI_TILE // 2)
        pygame.draw.circle(mini_surface, BLUE, mini_center(self.ai_opponent.pos), self.MINI_TILE // 2)
        for threat in self.threats:
            threat.draw(mini_surface, self.MINI_TILE)
        for powerup in self.powerups:
            if powerup.type == "extra_moves":
                p_color = ORANGE
            elif powerup.type == "hint":
                p_color = CYAN
            elif powerup.type == "teleportation":
                p_color = MAGENTA
            pygame.draw.circle(mini_surface, p_color, mini_center(powerup.pos), self.MINI_TILE // 2)
        path = compute_path(self.maze, self.ai_opponent.pos, self.maze.goal_pos)
        if path and len(path) > 1:
            points = [(x * self.MINI_TILE + self.MINI_TILE // 2,
                       y * self.MINI_TILE + self.MINI_TILE // 2) for (x, y) in path]
            pygame.draw.lines(mini_surface, BLUE, False, points, 2)
        self.screen.blit(mini_surface, self.minimap_pos)

    def draw_legend(self):
        legend_surface = pygame.Surface((self.LEGEND_WIDTH, self.LEGEND_HEIGHT))
        legend_surface.fill(WHITE)
        font = pygame.font.Font(None, 24)
        threat_rect = pygame.Rect(10, 10, 20, 20)
        pygame.draw.rect(legend_surface, RED, threat_rect)
        threat_text = font.render("Threat", True, BLACK)
        legend_surface.blit(threat_text, (threat_rect.right + 10, threat_rect.y))
        pygame.draw.line(legend_surface, BLUE, (10, 40), (30, 40), 3)
        opp_text = font.render("Opponent Path", True, BLACK)
        legend_surface.blit(opp_text, (40, 35))
        pm_rect = pygame.Rect(10, 50, 20, 20)
        pygame.draw.circle(legend_surface, ORANGE, (pm_rect.centerx, pm_rect.centery), 10)
        pm_text = font.render("Extra Moves", True, BLACK)
        legend_surface.blit(pm_text, (pm_rect.right + 10, pm_rect.y))
        self.screen.blit(legend_surface, self.legend_pos)

    def draw_difficulty_buttons(self, buttons):
        for rect, label, color in buttons:
            pygame.draw.rect(self.screen, color, rect)
            font = pygame.font.Font(None, 50)
            text = font.render(label, True, WHITE)
            self.screen.blit(text, (rect.x + 10, rect.y + 10))

    def draw(self):
        self.draw_minimap()
        self.draw_legend()

# ---------------------------
# BFS Path Helper Function
# ---------------------------
def compute_path(maze, start, goal):
    queue = deque()
    queue.append(start)
    came_from = {tuple(start): None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        x, y = current
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze.cols and 0 <= ny < maze.rows and maze.grid[ny][nx] == 0 and (nx, ny) not in came_from:
                queue.append([nx, ny])
                came_from[(nx, ny)] = current
    path = []
    current = goal
    if tuple(current) not in came_from:
        return []
    while current is not None:
        path.append(tuple(current))
        current = came_from.get(tuple(current))
    path.reverse()
    return path

# ---------------------------
# Game Class with Pause/Continue Added
# ---------------------------
class Game:
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((1280, 800))
            pygame.display.set_caption("THE MAZE GAME")
        except Exception as e:
            print("Error initializing display:", e)
            sys.exit()
        self.clock = pygame.time.Clock()
        self.tile_size = 40
        self.cols, self.rows = 25, 19

        try:
            bg_img = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\backgroundimg\image.JPG")
            self.background_img = pygame.transform.scale(bg_img, (1280, 800))
        except Exception as e:
            print("Error loading background image:", e)
            self.background_img = None

        player_start = [1, self.rows - 2]
        self.goal_pos = get_random_goal(self.cols, self.rows)

        self.maze = Maze(self.cols, self.rows, self.tile_size, self.goal_pos)
        self.player = Player(player_start, r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\playericon\steering-wheel_8033924.png", self.tile_size)
        self.ai_opponent = AIOpponent(player_start, self.goal_pos, "medium", 1,
                                      r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\gameicon\billiard_7100422.png", self.tile_size)
        self.threats = []
        self.powerups = []
        self.stats = GameStatistics(80, 45, 3, load_high_score())
        self.ui = UserInterface(self.screen, self.maze, self.player, self.ai_opponent, self.threats, self.powerups, self.tile_size)

        # Difficulty selection buttons for the menu
        self.difficulty_buttons = [
            (pygame.Rect(300, 200, 200, 60), "Easy", GREEN),
            (pygame.Rect(300, 300, 200, 60), "Medium", BLUE),
            (pygame.Rect(300, 400, 200, 60), "Hard", RED),
            (pygame.Rect(300, 500, 200, 60), "Quit", PURPLE)
        ]
        self.game_active = False
        self.running = True
        self.threat_blink_rate = 30
        self.blink_counter = 0
        self.collision_cooldown = 0
        self.level = 1
        self.current_difficulty = "medium"

        # UI buttons
        self.reset_hs_button = pygame.Rect(self.screen.get_width() - 220, 10 + 250 + 10, 210, 40)
        self.exit_button = pygame.Rect(self.screen.get_width() - 220, self.reset_hs_button.bottom + 130, 210, 40)
        self.volume_up_button = pygame.Rect(self.screen.get_width() - 220, self.exit_button.bottom + 10, 100, 40)
        self.volume_down_button = pygame.Rect(self.screen.get_width() - 110, self.exit_button.bottom + 10, 100, 40)
        self.back_button = pygame.Rect(20, 20, 100, 40)

        # PAUSE: Pause / Continue buttons & state
        self.pause_button = pygame.Rect(10, 10, 100, 40)
        self.continue_button = pygame.Rect(10, 10, 100, 40)
        self.paused = False

        self.menu_state = "difficulty"
        self.level_buttons = []

    def setup_level_buttons(self):
        self.level_buttons = []
        button_width = 100
        button_height = 50
        margin = 20
        start_x = (self.screen.get_width() - (button_width * 5 + margin * 4)) // 2
        start_y = (self.screen.get_height() - (button_height * 4 + margin * 3)) // 2
        level_num = 1
        for row in range(4):
            for col in range(5):
                x = start_x + col * (button_width + margin)
                y = start_y + row * (button_height + margin)
                rect = pygame.Rect(x, y, button_width, button_height)
                self.level_buttons.append((rect, str(level_num)))
                level_num += 1

    def reset_level(self, difficulty, reset_trials=True):
        try:
            self.goal_pos = get_random_goal(self.cols, self.rows)
            self.maze.goal_pos = self.goal_pos
            self.maze.generate()
            self.player.pos = [1, self.rows - 2]
            if reset_trials:
                self.stats.trials = 3
            if difficulty == "easy":
                base_moves = 100
                base_timer = 60
                moves_left = max(base_moves - (self.level - 1) * 2, 40)
            elif difficulty == "medium":
                base_moves = 80
                base_timer = 45
                moves_left = max(base_moves - (self.level - 1) * 3, 40)
            elif difficulty == "hard":
                base_moves = 70
                base_timer = 30
                moves_left = max(base_moves - (self.level - 1) * 4, 30)
            self.stats.moves_left = moves_left
            self.stats.timer = base_timer
            self.stats.initial_moves = moves_left
            if difficulty == "easy":
                num_threats = 3
                num_powerups = 2
            elif difficulty == "medium":
                num_threats = 5
                num_powerups = 3
            elif difficulty == "hard":
                num_threats = 8
                num_powerups = 4
            self.generate_threats(num_threats, difficulty)
            self.generate_powerups(num_powerups, difficulty)
            self.ai_opponent = AIOpponent([1, self.rows - 2], self.goal_pos, self.current_difficulty, self.level,
                                          r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\gameicon\billiard_7100422.png", self.tile_size)
            self.ui.ai_opponent = self.ai_opponent
        except Exception as e:
            print("Error resetting level:", e)

    def generate_threats(self, count, level):
        try:
            if level == "easy":
                move_speed = 30
            elif level == "medium":
                move_speed = 20
            elif level == "hard":
                move_speed = 10
            self.threats = []
            while len(self.threats) < count:
                x = random.randint(1, self.cols - 2)
                y = random.randint(1, self.rows - 2)
                if self.maze.grid[y][x] == 0 and [x, y] != self.player.pos and [x, y] != self.goal_pos:
                    behavior = 'random'
                    if level == "hard" and random.random() < 0.5:
                        behavior = 'chase'
                    self.threats.append(Threat((x, y), behavior, move_speed))
            self.ui.threats = self.threats
        except Exception as e:
            print("Error generating threats:", e)

    def generate_powerups(self, count, level):
        try:
            self.powerups = []
            while len(self.powerups) < count:
                x = random.randint(1, self.cols - 2)
                y = random.randint(1, self.rows - 2)
                if self.maze.grid[y][x] == 0 and [x, y] != self.player.pos and [x, y] != self.goal_pos:
                    p_type = random.choice(["extra_moves", "hint", "teleportation"])
                    self.powerups.append(PowerUp((x, y), p_type))
            self.ui.powerups = self.powerups
        except Exception as e:
            print("Error generating power-ups:", e)

    def _out_of_trials_dialog(self):
        root = tk.Tk()
        root.withdraw()
        retry = messagebox.askyesno(
            "Game Over",
            "You have run out of trials!\n\n"
            "Yes → Retry this level\n"
            "No  → Go back to difficulty selection"
        )
        root.destroy()
        if retry:
            self.reset_level(self.current_difficulty, reset_trials=True)
        else:
            self.game_active = False
            self.menu_state = "difficulty"

    def handle_game_events(self):
        global music_volume, effects_volume

        # 1) Process inputs (including Pause/Continue) every tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # PAUSE: mouse clicks on Pause/Continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if not self.paused and self.pause_button.collidepoint(mx, my):
                    self.paused = True
                    return
                if self.paused and self.continue_button.collidepoint(mx, my):
                    self.paused = False
                    return

            # PAUSE: toggle via P key
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
                return

            # All other input only if not paused
            if not self.paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if self.player.can_move(0, -1, self.maze):
                            self.player.move(0, -1, self.maze)
                            self.stats.moves_left -= 1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if self.player.can_move(0, 1, self.maze):
                            self.player.move(0, 1, self.maze)
                            self.stats.moves_left -= 1
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if self.player.can_move(-1, 0, self.maze):
                            self.player.move(-1, 0, self.maze)
                            self.stats.moves_left -= 1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.player.can_move(1, 0, self.maze):
                            self.player.move(1, 0, self.maze)
                            self.stats.moves_left -= 1

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.reset_hs_button.collidepoint(mouse_pos):
                        self.stats.high_score = 0
                        save_high_score(0)
                        messagebox.showinfo("High Score Reset", "High score has been reset!")
                    elif self.exit_button.collidepoint(mouse_pos):
                        # Changed Exit button to go back to level selection
                        self.game_active = False
                        self.menu_state = "level_selection"
                        self.setup_level_buttons()
                    elif self.volume_up_button.collidepoint(mouse_pos):
                        music_volume = min(music_volume + 0.1, 1.0)
                        effects_volume = min(effects_volume + 0.1, 1.0)
                        pygame.mixer.music.set_volume(music_volume)
                        if move_sound: move_sound.set_volume(effects_volume)
                        if level_select_sound: level_select_sound.set_volume(effects_volume)
                        if threat_hit_sound: threat_hit_sound.set_volume(effects_volume)
                    elif self.volume_down_button.collidepoint(mouse_pos):
                        music_volume = max(music_volume - 0.1, 0.0)
                        effects_volume = max(effects_volume - 0.1, 0.0)
                        pygame.mixer.music.set_volume(music_volume)
                        if move_sound: move_sound.set_volume(effects_volume)
                        if level_select_sound: level_select_sound.set_volume(effects_volume)
                        if threat_hit_sound: threat_hit_sound.set_volume(effects_volume)

        # 2) If paused, skip all game-logic updates
        if self.paused:
            return

        # 3) Game-logic (runs only when not paused)
        self.ai_opponent.move(self.maze)
        for threat in self.threats:
            threat.move(self.maze, self.player.pos)

        for powerup in self.powerups[:]:
            if self.player.pos == powerup.pos:
                if powerup.type == "extra_moves":
                    self.stats.moves_left += 20
                    root = tk.Tk(); root.withdraw()
                    messagebox.showinfo("Power-Up", "Extra Moves! +20 moves.")
                    root.destroy()
                elif powerup.type == "hint":
                    path = compute_path(self.maze, self.player.pos, self.maze.goal_pos)
                    steps = len(path) - 1 if path else 0
                    root = tk.Tk(); root.withdraw()
                    messagebox.showinfo("Hint", f"The exit is approximately {steps} steps away.")
                    root.destroy()
                elif powerup.type == "teleportation":
                    open_positions = []
                    for y in range(self.maze.rows):
                        for x in range(self.cols):
                            if self.maze.grid[y][x] == 0 and [x, y] != self.player.pos:
                                open_positions.append([x, y])
                    if open_positions:
                        self.player.pos = random.choice(open_positions)
                        root = tk.Tk(); root.withdraw()
                        messagebox.showinfo("Teleportation", "You have been teleported!")
                        root.destroy()
                self.powerups.remove(powerup)
                break

        # Threat collisions, out of moves, timeouts, wins/losses...
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
        else:
            if self.blink_counter // self.threat_blink_rate % 2 == 0:
                for threat in self.threats:
                    if tuple(self.player.pos) == tuple(threat.pos):
                        # ── Added: Play warning sound on threat hit ──
                        if threat_hit_sound:
                            threat_hit_sound.play()

                        self.stats.moves_left -= 10
                        self.stats.trials -= 1
                        self.stats.games_played += 1
                        root = tk.Tk(); root.withdraw()
                        if self.stats.trials <= 0:
                            root.destroy(); self._out_of_trials_dialog()
                        else:
                            messagebox.showinfo(
                                "Threat Hit",
                                f"You hit a threat!\nMoves left: {self.stats.moves_left}\nTrials left: {self.stats.trials}"
                            )
                            root.destroy()
                            self.player.pos = [1, self.rows - 2]
                        self.collision_cooldown = 30
                        break

        if self.stats.moves_left <= 0:
            self.stats.games_played += 1
            root = tk.Tk(); root.withdraw()
            if self.stats.trials <= 0:
                root.destroy(); self._out_of_trials_dialog()
            else:
                messagebox.showinfo("Out of Moves", "Out of moves! Restarting level with time reset!")
                root.destroy()
                self.reset_level(self.current_difficulty, reset_trials=False)

        if self.stats.timer <= 0:
            self.stats.games_played += 1
            root = tk.Tk(); root.withdraw()
            if self.stats.trials <= 0:
                root.destroy(); self._out_of_trials_dialog()
            else:
                messagebox.showinfo("Time Out", "Time Out! Start over!")
                root.destroy()
                self.reset_level(self.current_difficulty, reset_trials=False)

        if self.ai_opponent.pos == self.maze.goal_pos:
            root = tk.Tk(); root.withdraw(); root.destroy()
            self.stats.trials -= 1
            self.stats.games_played += 1
            if self.stats.trials <= 0:
                self._out_of_trials_dialog()
            else:
                messagebox.showinfo("Opponent Wins", "The opponent reached the exit before you. You lose a trial!")
                self.reset_level(self.current_difficulty, reset_trials=False)
            return

        if self.player.pos == self.maze.goal_pos:
            score = self.player.moves_count // 2
            if score > self.stats.high_score:
                self.stats.high_score = score
                save_high_score(score)
            self.stats.games_played += 1
            self.stats.games_won += 1
            if self.stats.fastest_escape is None or self.player.moves_count < self.stats.fastest_escape:
                self.stats.fastest_escape = self.player.moves_count
            root = tk.Tk(); root.withdraw()
            name = simpledialog.askstring("Leaderboard", "Enter your name for the leaderboard:")
            if name:
                update_leaderboard(name, score)
            root.destroy()
            root = tk.Tk(); root.withdraw()
            messagebox.showinfo(
                "Level Complete",
                f"Congratulations! You've reached the exit in {self.player.moves_count} moves.\nProceeding to next level."
            )
            root.destroy()
            self.level += 1
            self.reset_level(self.current_difficulty, reset_trials=False)

        self.stats.update(1 / 30)
        self.blink_counter += 1

    def handle_menu_events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        leaderboard_str = display_leaderboard()
                        messagebox.showinfo("Leaderboard", leaderboard_str)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.menu_state == "difficulty":
                        for rect, label, color in self.difficulty_buttons:
                            if rect.collidepoint(mouse_pos):
                                if label == "Quit":
                                    self.running = False
                                else:
                                    self.current_difficulty = label.lower()
                                    self.menu_state = "level_selection"
                                    self.setup_level_buttons()
                    elif self.menu_state == "level_selection":
                        if self.back_button.collidepoint(mouse_pos):
                            self.menu_state = "difficulty"
                            return
                        for rect, level_str in self.level_buttons:
                            if rect.collidepoint(mouse_pos):
                                if level_select_sound:
                                    level_select_sound.play()
                                self.level = int(level_str)
                                self.reset_level(self.current_difficulty)
                                self.game_active = True
                                pygame.mixer.music.stop()
                                self.menu_state = ""
        except Exception as e:
            print("Error in handle_menu_events:", e)
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Menu Error", f"An error occurred in the menu: {e}")
            root.destroy()

    def draw_level_selection(self):
        self.screen.fill(BLACK)
        header_font = pygame.font.Font(None, 60)
        header_text = header_font.render("Select Level", True, WHITE)
        header_rect = header_text.get_rect(center=(self.screen.get_width()//2, 100))
        self.screen.blit(header_text, header_rect)
        pygame.draw.rect(self.screen, RED, self.back_button, border_radius=10)
        font = pygame.font.Font(None, 30)
        self.screen.blit(font.render("Back", True, WHITE), (self.back_button.x + 20, self.back_button.y + 10))
        button_font = pygame.font.Font(None, 40)
        for rect, level_str in self.level_buttons:
            pygame.draw.rect(self.screen, BLUE, rect, border_radius=10)
            text = button_font.render(level_str, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_menu(self):
        try:
            if self.menu_state == "difficulty":
                if self.background_img:
                    self.screen.blit(self.background_img, (0, 0))
                else:
                    self.screen.fill(BLACK)
                self.ui.draw_difficulty_buttons(self.difficulty_buttons)
            elif self.menu_state == "level_selection":
                self.draw_level_selection()
        except Exception as e:
            print("Error in draw_menu:", e)
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Menu Draw Error", f"An error occurred while drawing the menu: {e}")
            root.destroy()

    def draw_game(self):
        try:
            self.screen.fill(BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen, self.tile_size)
            self.ai_opponent.draw(self.screen, self.tile_size)
            for powerup in self.powerups:
                powerup.draw(self.screen, self.tile_size)
            if self.blink_counter // self.threat_blink_rate % 2 == 0:
                for threat in self.threats:
                    threat.draw(self.screen, self.tile_size)
            self.stats.draw(self.screen, self.screen.get_width(), self.level, self.player)
            self.ui.draw()
            pygame.draw.rect(self.screen, PURPLE, self.reset_hs_button, border_radius=10)
            font = pygame.font.Font(None, 30)
            text = font.render("Reset High Score", True, WHITE)
            self.screen.blit(text, (self.reset_hs_button.x + 10, self.reset_hs_button.y + 10))
            lb_window_rect = pygame.Rect(self.reset_hs_button.x, self.reset_hs_button.bottom + 10, self.reset_hs_button.width, 100)
            pygame.draw.rect(self.screen, GREEN, lb_window_rect, border_radius=10)
            leaderboard = load_leaderboard_file()
            top_entries = leaderboard[:3]
            font_small = pygame.font.Font(None, 24)
            y_offset = lb_window_rect.y + 5
            for i, (name, score) in enumerate(top_entries):
                entry_text = font_small.render(f"{i+1}. {name}: {score}", True, BLACK)
                self.screen.blit(entry_text, (lb_window_rect.x + 5, y_offset))
                y_offset += 25
            pygame.draw.rect(self.screen, RED, self.exit_button, border_radius=10)
            exit_text = font.render("Back", True, WHITE)
            self.screen.blit(exit_text, (self.exit_button.x + 10, self.exit_button.y + 10))

            # Volume buttons with new icons
            try:
                volume_up_img = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\Volume\volume.PNG")
                volume_up_img = pygame.transform.scale(volume_up_img, (40, 40))
                self.screen.blit(volume_up_img, self.volume_up_button.topleft)
            except Exception as e:
                print("Error loading volume up icon:", e)
                pygame.draw.rect(self.screen, GREEN, self.volume_up_button, border_radius=10)
                vol_font = pygame.font.Font(None, 30)
                self.screen.blit(vol_font.render("+", True, WHITE), (self.volume_up_button.x + 35, self.volume_up_button.y + 5))

            try:
                volume_down_img = pygame.image.load(r"C:\Users\HP ELITEBOOK 1030 G4\OneDrive\Documents\mazegame\Volume\volume2.PNG")
                volume_down_img = pygame.transform.scale(volume_down_img, (40, 40))
                self.screen.blit(volume_down_img, self.volume_down_button.topleft)
            except Exception as e:
                print("Error loading volume down icon:", e)
                pygame.draw.rect(self.screen, RED, self.volume_down_button, border_radius=10)
                vol_font = pygame.font.Font(None, 30)
                self.screen.blit(vol_font.render("-", True, WHITE), (self.volume_down_button.x + 40, self.volume_down_button.y + 5))

            btn_font = pygame.font.Font(None, 30)
            if not self.paused:
                pygame.draw.rect(self.screen, YELLOW, self.pause_button, border_radius=5)
                self.screen.blit(btn_font.render("Pause", True, BLACK),
                                 (self.pause_button.x + 10, self.pause_button.y + 5))
            else:
                pygame.draw.rect(self.screen, GREEN, self.continue_button, border_radius=5)
                self.screen.blit(btn_font.render("Continue", True, BLACK),
                                 (self.continue_button.x + 5, self.continue_button.y + 5))
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                big_font = pygame.font.Font(None, 100)
                txt = big_font.render("PAUSED", True, WHITE)
                rect = txt.get_rect(center=self.screen.get_rect().center)
                overlay.blit(txt, rect)
                self.screen.blit(overlay, (0, 0))
        except Exception as e:
            print("Error in draw_game:", e)
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Draw Error", f"An error occurred while drawing the game: {e}")
            root.destroy()

    def run(self):
        try:
            while self.running:
                if self.game_active:
                    self.handle_game_events()
                    self.draw_game()
                else:
                    self.handle_menu_events()
                    self.draw_menu()
                pygame.display.flip()
                self.clock.tick(30)
            pygame.quit()
            sys.exit()
        except Exception as e:
            print("Fatal error:", e)
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"A fatal error occurred: {e}")
            root.destroy()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print("Error in main execution:", e)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fatal Error", f"A fatal error occurred during startup: {e}")
        root.destroy()
        pygame.quit()
        sys.exit()
