# maze_explorer/game/hud.py
import pygame
from core.engine import COLOR_TEXT, COLOR_HILIGHT, WIDTH

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("segoeui", 22)
        self.big_font = pygame.font.SysFont("segoeui", 36, bold=True)
        self.title_font = pygame.font.SysFont("segoeui", 32, bold=True)
        self.timer_font = pygame.font.SysFont("segoeui", 24, bold=True)
        self.instruction_font = pygame.font.SysFont("segoeui", 18)
        self.small_font = pygame.font.SysFont("segoeui", 16)
        # Colors for team panel
        self.color_panel_bg = (0, 0, 0, 140)
        self.color_panel_border = (100, 150, 255)
        self.color_panel_title = (255, 255, 255)
        self.color_panel_text = (210, 220, 230)
    
    def format_time(self, ms: int) -> str:
        """Format thời gian từ milliseconds thành MM:SS"""
        sec = ms // 1000
        return f"{sec//60:02d}:{sec%60:02d}"
    
    def draw_game_hud(self, screen, level_name: str, time_elapsed: int, score: int, 
                     stars_collected: int, stars_total: int, steps: int, nodes_expanded):
        """Vẽ HUD trong game với layout mới"""
        sw, sh = screen.get_size()
        
        # Header background
        header_height = 80
        header_rect = pygame.Rect(0, 0, sw, header_height)
        pygame.draw.rect(screen, (30, 40, 50), header_rect)
        pygame.draw.line(screen, (60, 70, 80), (0, header_height), (sw, header_height), 2)
        
        # Back button (top left)
        back_rect = pygame.Rect(20, 20, 80, 40)
        pygame.draw.rect(screen, (100, 200, 100), back_rect, border_radius=8)
        back_text = self.font.render("Back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Level title (center)
        level_text = self.title_font.render(level_name, True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(sw // 2, header_height // 2))
        screen.blit(level_text, level_rect)
        
        # Timer and stars (top right)
        timer_text = self.timer_font.render(self.format_time(time_elapsed), True, (255, 255, 255))
        timer_rect = timer_text.get_rect(topright=(sw - 20, 15))
        screen.blit(timer_text, timer_rect)
        
        # Star count
        star_text = f"x {stars_collected}"
        star_surface = self.font.render(star_text, True, (255, 255, 0))
        star_rect = star_surface.get_rect(topright=(sw - 20, 45))
        screen.blit(star_surface, star_rect)
        # Steps (under star count)
        steps_text = self.small_font.render(f"Steps: {steps}", True, (220, 230, 240))
        steps_rect = steps_text.get_rect(topright=(sw - 20, 200))
        screen.blit(steps_text, steps_rect)
        # Nodes expanded (under steps) - chỉ hiển thị sau khi hoàn tất (khi không phải None)
        if nodes_expanded is not None:
            expanded_text = self.small_font.render(f"Expanded: {nodes_expanded}", True, (255, 200, 120))
            expanded_rect = expanded_text.get_rect(topright=(sw - 20, 220))
            screen.blit(expanded_text, expanded_rect)
        
        # Algorithm selection panel (left side)
        self._draw_algorithm_panel(screen, sw, sh)
        
        # Team panel (bottom-right), avoid overlapping header/top-right metrics
        self._draw_team_panel(screen, sw, sh)
    
    def draw_result(self, screen, result: str):
        """Vẽ kết quả game (WIN/LOSE)"""
        if result:
            text_surface = self.big_font.render(result, True, COLOR_HILIGHT)
            sw, _ = screen.get_size()
            screen.blit(text_surface, text_surface.get_rect(center=(sw//2, 56)))

    def _draw_algorithm_panel(self, screen, sw: int, sh: int):
        """Vẽ panel chọn thuật toán ở phía bên trái màn hình."""
        # Panel content
        title = "Chọn thuật toán"
        algorithms = [
            "1 - BFS",
            "2 - DFS", 
            "3 - UCS",
            "4 - Greedy",
            "5 - A*"
        ]
        
        pad_x, pad_y = 12, 8
        title_surf = self.instruction_font.render(title, True, (255, 255, 255))
        algo_surfs = [self.small_font.render(algo, True, (200, 220, 240)) for algo in algorithms]
        
        # Calculate panel dimensions
        content_width = max([title_surf.get_width(), *[s.get_width() for s in algo_surfs]])
        content_height = title_surf.get_height() + 8 + sum(s.get_height() for s in algo_surfs) + (len(algo_surfs) - 1) * 4
        panel_width = content_width + pad_x * 2
        panel_height = content_height + pad_y * 2
        
        # Position panel on left side, below header
        panel_x = 20
        panel_y = 100  # Below header (80px) + margin
        
        # Semi-transparent background and border
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 120))  # Dark semi-transparent background
        pygame.draw.rect(panel_surface, (100, 150, 255), panel_surface.get_rect(), width=2, border_radius=6)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw content
        screen.blit(title_surf, (panel_x + pad_x, panel_y + pad_y))
        y = panel_y + pad_y + title_surf.get_height() + 8
        for surf in algo_surfs:
            screen.blit(surf, (panel_x + pad_x, y))
            y += surf.get_height() + 4

    def _draw_team_panel(self, screen, sw: int, sh: int):
        """Vẽ panel hiển thị thông tin nhóm ở góc phải dưới, không che nội dung chính."""
        group_title = "Team 09"
        group_lines = [
            "251ARIN330585_03CLC_AI_Project",
            "23110110 - Lê Quang Hưng",
            "23110078 - Nguyễn Thái Bảo",
            "23110111 - Lương Nguyễn Thành Hưng",
        ]
        
        pad_x, pad_y = 14, 10
        title_surf = self.small_font.render(group_title, True, self.color_panel_title)
        line_surfs = [self.small_font.render(t, True, self.color_panel_text) for t in group_lines]
        content_width = max([title_surf.get_width(), *[s.get_width() for s in line_surfs]])
        content_height = title_surf.get_height() + 6 + sum(s.get_height() for s in line_surfs) + (len(line_surfs) - 1) * 2
        panel_width = content_width + pad_x * 2
        panel_height = content_height + pad_y * 2
        panel_x = sw - panel_width - 20
        panel_y = sh - panel_height - 20
        
        # Semi-transparent background and border
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.color_panel_bg)
        pygame.draw.rect(panel_surface, self.color_panel_border, panel_surface.get_rect(), width=2, border_radius=8)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Content
        screen.blit(title_surf, (panel_x + pad_x, panel_y + pad_y))
        y = panel_y + pad_y + title_surf.get_height() + 6
        for s in line_surfs:
            screen.blit(s, (panel_x + pad_x, y))
            y += s.get_height() + 2
