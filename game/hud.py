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
    
    def format_time(self, ms: int) -> str:
        """Format thời gian từ milliseconds thành MM:SS"""
        sec = ms // 1000
        return f"{sec//60:02d}:{sec%60:02d}"
    
    def draw_game_hud(self, screen, level_name: str, time_elapsed: int, score: int, 
                     stars_collected: int, stars_total: int, steps: int):
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
    
    def draw_result(self, screen, result: str):
        """Vẽ kết quả game (WIN/LOSE)"""
        if result:
            text_surface = self.big_font.render(result, True, COLOR_HILIGHT)
            sw, _ = screen.get_size()
            screen.blit(text_surface, text_surface.get_rect(center=(sw//2, 56)))
