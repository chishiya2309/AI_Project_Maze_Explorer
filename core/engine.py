# maze_explorer/core/engine.py
import pygame
import time
from typing import List
from dataclasses import dataclass, asdict
import json
import os

# ================== CONFIG ==================
WIDTH, HEIGHT = 920, 600
FPS = 60
TILE = 32
GRID_OFFSET_X, GRID_OFFSET_Y = 240, 96

# Colors
COLOR_BG = (20, 24, 32)
COLOR_TEXT = (220, 230, 240)
COLOR_DIM = (140, 155, 170)
COLOR_WALL = (70, 90, 120)
COLOR_PATH = (36, 46, 64)
COLOR_PLAYER = (60, 200, 120)
COLOR_GOAL_UNLOCK = (0, 170, 220)
COLOR_GOAL_LOCK = (90, 100, 120)
COLOR_STAR = (255, 200, 40)
COLOR_HILIGHT = (80, 200, 255)

LEVELS_DIR = "data/levels"
STATS_FILE = "stats.json"
MAX_KEEP = 500

# ================== DATA STRUCTURES ==================
@dataclass
class PlayRecord:
    ts: float
    level_name: str
    result: str
    score: int
    time_elapsed_sec: int
    stars_collected: int
    stars_total: int
    steps: int
    solver: str = "HUMAN"  # HUMAN | BFS | ...

class StatsStore:
    def __init__(self, path: str):
        self.path = path
        self.records: List[PlayRecord] = []
        self.load()

    def load(self):
        if not os.path.isfile(self.path): 
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.records = [PlayRecord(**r) for r in raw.get("records", [])]
        except: 
            self.records = []

    def save(self):
        data = {"records": [asdict(r) for r in self.records[-MAX_KEEP:]]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, rec: PlayRecord):
        self.records.append(rec)
        self.save()

# ================== GAME ENGINE ==================
class GameApp:
    def __init__(self):
        pygame.init()
        # Luôn mở fullscreen, không cho phép resize
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Maze Explorer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.stats = StatsStore(STATS_FILE)
        # Scene manager will be injected from main
        self.scenes = None

    def set_scene_manager(self, scene_manager):
        self.scenes = scene_manager

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scenes.handle_event(e)
            self.scenes.update(dt)
            self.scenes.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
