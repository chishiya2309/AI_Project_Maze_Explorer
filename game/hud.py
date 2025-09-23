# maze_explorer/game/hud.py
import pygame
from core.engine import COLOR_TEXT, COLOR_HILIGHT, WIDTH

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("segoeui", 22)
        self.big_font = pygame.font.SysFont("segoeui", 36, bold=True)
    
    def format_time(self, ms: int) -> str:
        """Format thời gian từ milliseconds thành MM:SS"""
        sec = ms // 1000
        return f"{sec//60:02d}:{sec%60:02d}"
    
    def draw_game_hud(self, screen, level_name: str, time_elapsed: int, score: int, 
                     stars_collected: int, stars_total: int, steps: int):
        """Vẽ HUD trong game"""
        hud_text = f"{level_name} | Time {self.format_time(time_elapsed)} | Score {score} | Stars {stars_collected}/{stars_total} | Steps {steps}"
        hud_surface = self.font.render(hud_text, True, COLOR_TEXT)
        screen.blit(hud_surface, (24, 18))
    
    def draw_result(self, screen, result: str):
        """Vẽ kết quả game (WIN/LOSE)"""
        if result:
            text_surface = self.big_font.render(result, True, COLOR_HILIGHT)
            sw, _ = screen.get_size()
            screen.blit(text_surface, text_surface.get_rect(center=(sw//2, 56)))
