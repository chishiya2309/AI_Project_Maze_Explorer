# maze_explorer/game/level.py
import pygame
import time
from typing import List
from core.engine import (
    COLOR_BG, COLOR_WALL, COLOR_PATH, COLOR_PLAYER, COLOR_GOAL_UNLOCK, 
    COLOR_GOAL_LOCK, COLOR_STAR, GRID_OFFSET_X, GRID_OFFSET_Y, TILE,
    PlayRecord
)
from core.scene import Scene
from game.player import Player
from game.grid import Grid
from game.collectibles import StarCollector
from game.hud import HUD

class LevelScene(Scene):
    def __init__(self, game, name: str, rows: List[str]):
        super().__init__(game)
        self.name = name
        self.grid = Grid(rows)
        
        # Khởi tạo player và goal
        start_pos, self.goal = self.grid.find_start_goal()
        self.player = Player(*start_pos)
        
        # Khởi tạo star collector
        stars = self.grid.find_stars()
        self.star_collector = StarCollector(stars)
        
        # Game state
        self.score = 0
        self.steps = 0
        self.time_elapsed = 0
        self.cool = 0  # Cooldown cho movement
        self.result = None
        self.timer = 0  # Timer cho hiển thị kết quả
        
        # HUD
        self.hud = HUD()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            from game.scenes import LevelSelectScene
            self.game.scenes.switch(LevelSelectScene(self.game))

    def update(self, dt):
        if self.result:
            self.timer -= dt
            if self.timer <= 0:
                from game.scenes import LevelSelectScene
                self.game.scenes.switch(LevelSelectScene(self.game))
            return
        
        self.time_elapsed += dt
        keys = pygame.key.get_pressed()
        self.cool -= dt
        
        if self.cool <= 0:
            dx = dy = 0
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            elif keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1
            
            if dx or dy:
                nx, ny = self.player.gx + dx, self.player.gy + dy
                if not self.grid.is_blocked(nx, ny):
                    self.player.gx, self.player.gy = nx, ny
                    self.steps += 1
                    self._on_step()
                self.cool = 110

    def _on_step(self):
        """Xử lý khi player di chuyển"""
        # Thu thập ngôi sao
        if self.star_collector.collect_star_at(self.player.gx, self.player.gy):
            self.score += 10
        
        # Kiểm tra điều kiện thắng
        player_pos = (self.player.gx, self.player.gy)
        if player_pos == self.goal and self.star_collector.is_complete():
            self._finish()

    def _finish(self):
        """Kết thúc level"""
        self.result = "WIN"
        self.timer = 1200
        
        # Ghi lại record
        rec = PlayRecord(
            ts=time.time(),
            level_name=self.name,
            result="WIN",
            score=self.score,
            time_elapsed_sec=int(self.time_elapsed // 1000),
            stars_collected=self.star_collector.stars_collected,
            stars_total=self.star_collector.stars_total,
            steps=self.steps
        )
        self.game.stats.add(rec)

    def _draw_thin_walls(self, screen):
        """Vẽ tường kiểu mỏng theo đường viền"""
        wall_thickness = 3
        
        for y in range(self.grid.H):
            for x in range(self.grid.W):
                if self.grid.get_cell(x, y) == "1":  # Nếu là tường
                    cell_x = GRID_OFFSET_X + x * TILE
                    cell_y = GRID_OFFSET_Y + y * TILE
                    
                    # Kiểm tra các ô xung quanh
                    top_wall = self.grid.get_cell(x, y-1) == "1"
                    bottom_wall = self.grid.get_cell(x, y+1) == "1"
                    left_wall = self.grid.get_cell(x-1, y) == "1"
                    right_wall = self.grid.get_cell(x+1, y) == "1"
                    
                    # Vẽ viền trên
                    if not top_wall:
                        pygame.draw.rect(screen, COLOR_WALL, (
                            cell_x, cell_y, TILE, wall_thickness
                        ))
                    
                    # Vẽ viền dưới
                    if not bottom_wall:
                        pygame.draw.rect(screen, COLOR_WALL, (
                            cell_x, cell_y + TILE - wall_thickness, TILE, wall_thickness
                        ))
                    
                    # Vẽ viền trái
                    if not left_wall:
                        pygame.draw.rect(screen, COLOR_WALL, (
                            cell_x, cell_y, wall_thickness, TILE
                        ))
                    
                    # Vẽ viền phải
                    if not right_wall:
                        pygame.draw.rect(screen, COLOR_WALL, (
                            cell_x + TILE - wall_thickness, cell_y, wall_thickness, TILE
                        ))

    def draw(self, screen):
        screen.fill(COLOR_BG)
        
        # Vẽ nền cho tất cả các ô (đường đi)
        for y in range(self.grid.H):
            for x in range(self.grid.W):
                if self.grid.get_cell(x, y) != "1":  # Chỉ vẽ nền cho ô không phải tường
                    pygame.draw.rect(screen, COLOR_PATH, (
                        GRID_OFFSET_X + x * TILE,
                        GRID_OFFSET_Y + y * TILE,
                        TILE, TILE
                    ))
        
        # Vẽ tường kiểu mỏng
        self._draw_thin_walls(screen)
        
        # Vẽ ngôi sao
        for (x, y) in self.star_collector.get_remaining_stars():
            cx = GRID_OFFSET_X + x * TILE + TILE // 2
            cy = GRID_OFFSET_Y + y * TILE + TILE // 2
            pygame.draw.circle(screen, COLOR_STAR, (cx, cy), TILE // 4)
        
        # Vẽ goal
        gx, gy = self.goal
        door_color = COLOR_GOAL_UNLOCK if self.star_collector.is_complete() else COLOR_GOAL_LOCK
        pygame.draw.rect(screen, door_color, (
            GRID_OFFSET_X + gx * TILE + 6,
            GRID_OFFSET_Y + gy * TILE + 6,
            TILE - 12, TILE - 12
        ), border_radius=6)
        
        # Vẽ player
        px = GRID_OFFSET_X + self.player.gx * TILE + TILE // 2
        py = GRID_OFFSET_Y + self.player.gy * TILE + TILE // 2
        pygame.draw.circle(screen, COLOR_PLAYER, (px, py), TILE // 3)
        
        # Vẽ HUD
        self.hud.draw_game_hud(
            screen, self.name, self.time_elapsed, self.score,
            self.star_collector.stars_collected, self.star_collector.stars_total,
            self.steps
        )
        
        # Vẽ kết quả
        self.hud.draw_result(screen, self.result)
