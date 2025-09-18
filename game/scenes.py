# maze_explorer/game/scenes.py
import pygame
import time
from typing import List
from core.engine import COLOR_BG, COLOR_TEXT, COLOR_DIM, COLOR_HILIGHT, WIDTH, HEIGHT
from core.scene import Scene
from core.assets import scan_levels

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font = pygame.font.SysFont("segoeui", 24)
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.game.scenes.switch(LevelSelectScene(self.game))
            elif e.key == pygame.K_h:
                self.game.scenes.switch(HistoryScene(self.game))
    
    def draw(self, screen):
        screen.fill(COLOR_BG)
        title = self.font_big.render("Maze Explorer", True, COLOR_TEXT)
        tip1 = self.font.render("ENTER: Level Select", True, COLOR_TEXT)
        tip2 = self.font.render("H: History", True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2-40)))
        screen.blit(tip1, tip1.get_rect(center=(WIDTH//2, HEIGHT//2+20)))
        screen.blit(tip2, tip2.get_rect(center=(WIDTH//2, HEIGHT//2+50)))

class HistoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.SysFont("segoeui", 40, bold=True)
        self.font = pygame.font.SysFont("segoeui", 20)
        self.small = pygame.font.SysFont("segoeui", 18)
        self.idx = 0
        self.scroll = 0
        self.msg = "↑/↓ chọn · ESC về Menu"
        self.recs = self.game.stats.records
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_UP, pygame.K_w):
                if self.recs: 
                    self.idx = (self.idx - 1) % len(self.recs)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                if self.recs: 
                    self.idx = (self.idx + 1) % len(self.recs)
    
    def _format_time(self, sec: int) -> str:
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"
    
    def draw(self, screen):
        screen.fill(COLOR_BG)
        title = self.font_big.render("History", True, COLOR_TEXT)
        screen.blit(title, (48, 32))
        hint = self.small.render(self.msg, True, COLOR_DIM)
        screen.blit(hint, (48, 76))
        
        if not self.recs:
            empty = self.font.render("Chưa có bản ghi.", True, COLOR_DIM)
            screen.blit(empty, (64, 140))
            return
        
        y = 120
        line_h = 28
        # Hiển thị 14 dòng cuối
        for i, r in enumerate(self.recs[-14:]):
            tstr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.ts))
            elapsed = self._format_time(r.time_elapsed_sec)
            txt = f"{tstr} | {r.level_name:12s} | {r.result:4s} | Score {r.score:4d} | Elapsed {elapsed} | Stars {r.stars_collected}/{r.stars_total} | Steps {r.steps}"
            color = COLOR_HILIGHT if i == self.idx else COLOR_TEXT
            screen.blit(self.font.render(txt, True, color), (48, y + i * line_h))

class LevelSelectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_big = pygame.font.SysFont("segoeui", 40, bold=True)
        self.font = pygame.font.SysFont("segoeui", 24)
        self.levels = scan_levels("data/levels")
        self.idx = 0
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.idx = (self.idx - 1) % len(self.levels)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.idx = (self.idx + 1) % len(self.levels)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.levels:
                    name, rows = self.levels[self.idx]
                    from game.level import LevelScene
                    self.game.scenes.switch(LevelScene(self.game, name, rows))
    
    def draw(self, screen):
        screen.fill(COLOR_BG)
        title = self.font_big.render("Level Select", True, COLOR_TEXT)
        screen.blit(title, (48, 32))
        
        for i, (n, _) in enumerate(self.levels):
            c = COLOR_HILIGHT if i == self.idx else COLOR_TEXT
            screen.blit(self.font.render(f"{i+1:02d}. {n}", True, c), (64, 120 + i * 34))
