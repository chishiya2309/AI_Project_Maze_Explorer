import pygame
import time
from typing import List
from core.engine import COLOR_BG, COLOR_TEXT, COLOR_DIM, COLOR_HILIGHT, WIDTH, HEIGHT
from core.scene import Scene
from core.assets import scan_levels

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("segoeui", 64, bold=True)
        self.font_button = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 20)
        self.font_tiny = pygame.font.SysFont("segoeui", 16)
        self.selected_button = 0  # 0=Start, 1=History, 2=Quit
        
        self.color_bg = (20, 30, 40)  # Nền màu tối
        self.color_title_white = (255, 255, 255)
        self.color_title_blue = (100, 150, 255)
        self.color_button_bg = (60, 70, 80)  # Màu xám đen cho nút đã chọn
        self.color_button_text = (100, 255, 100)  # Màu xanh lá cây sáng
        self.color_text = (200, 200, 200)
        self.color_group = (150, 150, 150)
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                self.selected_button = (self.selected_button - 1) % 3
            elif e.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % 3
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_button()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                self._activate_button()
        elif e.type == pygame.MOUSEMOTION:
            # Cập nhật nút đã chọn dựa trên vị trí con trỏ chuột
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            button_y = sh // 2
            button_spacing = 60
            button_height = 50
            
            # Kiểm tra xem con trỏ chuột có nằm trên bất kỳ nút nào không
            mouse_over_button = False
            for i in range(3):
                button_rect = pygame.Rect((sw - 200) // 2, button_y + i * button_spacing, 200, button_height)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_button = i
                    mouse_over_button = True
                    break
            
            # Đặt con trỏ chuột dựa trên trạng thái hover
            if mouse_over_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _activate_button(self):
        """Kích hoạt nút đã chọn"""
        if self.selected_button == 0:  # Start
            self.game.scenes.switch(LevelSelectScene(self.game))
        elif self.selected_button == 1:  # History
            self.game.scenes.switch(HistoryScene(self.game))
        elif self.selected_button == 2:  # Quit
            self.game.running = False
    
    def draw(self, screen):
        screen.fill(self.color_bg)
        sw, sh = screen.get_size()
        
        # Vẽ tiêu đề "MazeExplorer" với các màu khác nhau
        title1 = self.font_title.render("Maze", True, self.color_title_white)
        title2 = self.font_title.render("Explorer", True, self.color_title_blue)
        
        # Căn giữa tiêu đề theo chiều ngang
        title1_rect = title1.get_rect()
        title2_rect = title2.get_rect()
        total_title_width = title1_rect.width + title2_rect.width + 10
        title_x = (sw - total_title_width) // 2
        title_y = sh // 4
        
        screen.blit(title1, (title_x, title_y))
        screen.blit(title2, (title_x + title1_rect.width + 10, title_y))
        
        # Vẽ các nút
        button_y = sh // 2
        button_spacing = 60
        button_width = 200
        button_height = 50
        
        buttons = ["Start", "History", "Quit"]
        for i, button_text in enumerate(buttons):
            # Nền nút
            if i == self.selected_button:
                button_rect = pygame.Rect((sw - button_width) // 2, button_y + i * button_spacing, button_width, button_height)
                pygame.draw.rect(screen, self.color_button_bg, button_rect, border_radius=8)
            
            # Văn bản nút
            text_surface = self.font_button.render(button_text, True, self.color_button_text)
            text_rect = text_surface.get_rect(center=((sw - button_width) // 2 + button_width // 2, button_y + i * button_spacing + button_height // 2))
            screen.blit(text_surface, text_rect)
        
        # Vẽ thông tin nhóm ở dưới cùng bên trái
        group_text = "251ARIN330585_03CLC_AI_Project_Nhóm 09"
        group_surface = self.font_tiny.render(group_text, True, self.color_group)
        screen.blit(group_surface, (20, sh - 30))

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
        
        # Layout list responsively: center vertically if short list
        sw, sh = screen.get_size()
        start_y = 120
        total_h = len(self.levels) * 34
        if start_y + total_h < sh - 40:
            start_y = (sh - total_h) // 2
        for i, (n, _) in enumerate(self.levels):
            c = COLOR_HILIGHT if i == self.idx else COLOR_TEXT
            screen.blit(self.font.render(f"{i+1:02d}. {n}", True, c), (64, start_y + i * 34))
