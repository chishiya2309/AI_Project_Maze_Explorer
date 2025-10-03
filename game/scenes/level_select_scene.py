import pygame
from core.scene import Scene
from core.assets import scan_levels, load_image


class LevelSelectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font_button = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_level = pygame.font.SysFont("segoeui", 20, bold=True)
        self.levels = scan_levels("data/levels")
        self.selected_level = 0
        self.hovered_level = -1  # Track which level is being hovered
        self.hovered_back = False  # Track if back button is hovered
        
        # Background image for level select screen
        self.bg_image = load_image("level_background.png")

        # Colors
        self.color_bg = (20, 40, 30)  # Dark green background
        self.color_bg_pattern = (15, 35, 25)  # Darker green for pattern
        self.color_title = (255, 255, 255)  # White title
        
        # Back button colors
        self.color_back_button = (100, 200, 100)  # Green back button
        self.color_back_button_hover = (120, 220, 120)  # Lighter green for hover
        self.color_back_button_text = (255, 255, 255)  # White text
        
        # Card colors
        self.color_card_bg = (40, 80, 60)  # Dark teal card background
        self.color_card_hover = (60, 120, 80)  # Lighter teal for hover
        self.color_card_selected = (80, 160, 100)  # Even lighter for selected
        self.color_card_text = (255, 255, 255)  # White text on cards
        self.color_card_border = (80, 160, 100)  # Border color
        self.color_card_border_hover = (120, 200, 140)  # Brighter border for hover
        
        # Card layout
        self.cards_per_row = 4
        self.card_width = 150
        self.card_height = 100
        self.card_spacing = 20
        self.card_margin = 50
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                from .menu_scene import MenuScene
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                if self.selected_level > 0:
                    self.selected_level -= 1
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                if self.selected_level < len(self.levels) - 1:
                    self.selected_level += 1
            elif e.key in (pygame.K_UP, pygame.K_w):
                if self.selected_level >= self.cards_per_row:
                    self.selected_level -= self.cards_per_row
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected_level + self.cards_per_row < len(self.levels):
                    self.selected_level += self.cards_per_row
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.levels:
                    name, rows = self.levels[self.selected_level]
                    from game.level import LevelScene
                    # Sử dụng tên đẹp thay vì tên file
                    level_display_name = f"Level {self.selected_level + 1}"
                    self.game.scenes.switch(LevelScene(self.game, level_display_name, rows))
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                mouse_x, mouse_y = e.pos
                sw, sh = self.game.screen.get_size()
                
                # Check back button
                back_rect = pygame.Rect(30, 30, 80, 40)
                if back_rect.collidepoint(mouse_x, mouse_y):
                    from .menu_scene import MenuScene
                    self.game.scenes.switch(MenuScene(self.game))
                    return
                
                # Check level cards
                self._check_card_click(mouse_x, mouse_y, sw, sh)
        elif e.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            
            # Check if hovering over back button
            back_rect = pygame.Rect(30, 30, 80, 40)
            self.hovered_back = back_rect.collidepoint(mouse_x, mouse_y)
            
            # Check if hovering over any card
            self.hovered_level = self._check_card_hover(mouse_x, mouse_y, sw, sh)
            
            # Set cursor based on hover state
            if self.hovered_back or self.hovered_level >= 0:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _check_card_click(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse clicked on a level card"""
        start_x = (sw - (self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing)) // 2
        start_y = sh // 2 - 50
        
        for i, (name, _) in enumerate(self.levels):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            card_x = start_x + col * (self.card_width + self.card_spacing)
            card_y = start_y + row * (self.card_height + self.card_spacing)
            
            card_rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
            if card_rect.collidepoint(mouse_x, mouse_y):
                self.selected_level = i
                # Start the level
                from game.level import LevelScene
                # Sử dụng tên đẹp thay vì tên file
                level_display_name = f"Level {i + 1}"
                self.game.scenes.switch(LevelScene(self.game, level_display_name, self.levels[i][1]))
                break
    
    def _check_card_hover(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse is hovering over any card and return card index"""
        start_x = (sw - (self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing)) // 2
        start_y = sh // 2 - 50
        
        for i in range(len(self.levels)):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            card_x = start_x + col * (self.card_width + self.card_spacing)
            card_y = start_y + row * (self.card_height + self.card_spacing)
            
            card_rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
            if card_rect.collidepoint(mouse_x, mouse_y):
                return i
        return -1
    
    def draw(self, screen):
        # Background image first
        sw, sh = screen.get_size()
        if self.bg_image:
            bg_scaled = pygame.transform.smoothscale(self.bg_image, (sw, sh))
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill(self.color_bg)
        
        # Back button
        back_rect = pygame.Rect(30, 30, 80, 40)
        back_color = self.color_back_button_hover if self.hovered_back else self.color_back_button
        pygame.draw.rect(screen, back_color, back_rect, border_radius=8)
        
        # Add subtle border for hover effect
        if self.hovered_back:
            pygame.draw.rect(screen, (150, 250, 150), back_rect, 2, border_radius=8)
        
        back_text = self.font_button.render("Back", True, self.color_back_button_text)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Title
        title_text = self.font_title.render("Select level", True, self.color_title)
        title_rect = title_text.get_rect(center=(sw // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Level cards
        if not self.levels:
            return
            
        # Calculate card positions
        start_x = (sw - (self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing)) // 2
        start_y = sh // 2 - 50
        
        for i, (name, _) in enumerate(self.levels):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            card_x = start_x + col * (self.card_width + self.card_spacing)
            card_y = start_y + row * (self.card_height + self.card_spacing)
            
            # Card background
            card_rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
            
            # Determine card color based on state
            if i == self.selected_level:
                # Selected card (keyboard selection)
                card_color = self.color_card_selected
                border_color = self.color_card_border
                border_width = 3
            elif i == self.hovered_level:
                # Hovered card (mouse hover)
                card_color = self.color_card_hover
                border_color = self.color_card_border_hover
                border_width = 3
            else:
                # Normal card
                card_color = self.color_card_bg
                border_color = self.color_card_border
                border_width = 2
            
            # Draw card background
            pygame.draw.rect(screen, card_color, card_rect, border_radius=12)
            pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=12)
            
            # Level text
            level_text = f"Level {i + 1}"
            level_surface = self.font_level.render(level_text, True, self.color_card_text)
            level_rect = level_surface.get_rect(center=(card_x + self.card_width // 2, card_y + self.card_height // 2))
            screen.blit(level_surface, level_rect)
