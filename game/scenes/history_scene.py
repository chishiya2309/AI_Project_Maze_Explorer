import pygame
import time
from core.scene import Scene


class HistoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font_header = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_card = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 16)
        self.font_tiny = pygame.font.SysFont("segoeui", 14)
        self.idx = 0
        self.scroll = 0
        self.recs = self.game.stats.records
        self.hovered_record = -1
        self.dragging_scroll = False  # Track if user is dragging scroll bar
        
        # Scroll settings
        self.records_per_page = 6  # Number of records visible at once
        self.card_height = 80
        self.card_spacing = 10
        self.max_scroll = max(0, len(self.recs) - self.records_per_page)
        
        # Colors
        self.color_bg = (20, 30, 40)  # Dark blue background
        self.color_bg_pattern = (15, 25, 35)  # Darker blue for pattern
        self.color_title = (255, 255, 255)  # White title
        self.color_back_button = (100, 150, 255)  # Blue back button
        self.color_back_button_hover = (120, 170, 255)  # Lighter blue for hover
        self.color_card_bg = (40, 50, 70)  # Dark blue card background
        self.color_card_hover = (60, 80, 100)  # Lighter blue for hover
        self.color_card_selected = (80, 120, 160)  # Even lighter for selected
        self.color_card_text = (255, 255, 255)  # White text on cards
        self.color_card_border = (100, 150, 200)  # Border color
        self.color_success = (100, 255, 100)  # Green for success
        self.color_failure = (255, 100, 100)  # Red for failure
        self.color_stats = (200, 200, 200)  # Gray for stats
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                from .menu_scene import MenuScene
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_UP, pygame.K_w):
                if self.recs: 
                    self.idx = max(0, self.idx - 1)
                    self._update_scroll()
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                if self.recs: 
                    self.idx = min(len(self.recs) - 1, self.idx + 1)
                    self._update_scroll()
            elif e.key == pygame.K_PAGEUP:
                if self.recs:
                    self.idx = max(0, self.idx - self.records_per_page)
                    self._update_scroll()
            elif e.key == pygame.K_PAGEDOWN:
                if self.recs:
                    self.idx = min(len(self.recs) - 1, self.idx + self.records_per_page)
                    self._update_scroll()
            elif e.key == pygame.K_HOME:
                if self.recs:
                    self.idx = 0
                    self.scroll = 0
            elif e.key == pygame.K_END:
                if self.recs:
                    self.idx = len(self.recs) - 1
                    self.scroll = self.max_scroll
        elif e.type == pygame.MOUSEWHEEL:
            # Handle mouse wheel scrolling
            if self.recs and len(self.recs) > self.records_per_page:
                if e.y > 0:  # Scroll up
                    self.scroll = max(0, self.scroll - 1)
                elif e.y < 0:  # Scroll down
                    self.scroll = min(self.max_scroll, self.scroll + 1)
                
                # Update selected index to match scroll position
                self.idx = self.scroll
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
                
                # Check record cards
                self._check_record_click(mouse_x, mouse_y, sw, sh)
                
                # Check scroll bar click/drag start
                self._check_scroll_bar_click(mouse_x, mouse_y, sw, sh)
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:  # Left click release
                self.dragging_scroll = False
        elif e.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            
            # Handle scroll bar dragging
            if self.dragging_scroll and self.recs and len(self.recs) > self.records_per_page:
                scroll_bar_x = sw - 20
                scroll_bar_y = 120
                scroll_bar_height = sh - 200
                
                relative_y = mouse_y - scroll_bar_y
                scroll_ratio = relative_y / scroll_bar_height
                new_scroll = int(scroll_ratio * self.max_scroll)
                
                # Clamp scroll position
                self.scroll = max(0, min(self.max_scroll, new_scroll))
                self.idx = self.scroll
            
            # Check if hovering over back button
            back_rect = pygame.Rect(30, 30, 80, 40)
            self.hovered_back = back_rect.collidepoint(mouse_x, mouse_y)
            
            # Check if hovering over any record
            self.hovered_record = self._check_record_hover(mouse_x, mouse_y, sw, sh)
            
            # Set cursor based on hover state
            if self.hovered_back or self.hovered_record >= 0:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _check_record_click(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse clicked on a record card"""
        if not self.recs:
            return
            
        start_x = 50
        start_y = 120
        card_width = sw - 100
        card_height = self.card_height
        card_spacing = self.card_spacing
        
        # Get visible records based on scroll
        visible_start = self.scroll
        visible_end = min(self.scroll + self.records_per_page, len(self.recs))
        visible_records = self.recs[visible_start:visible_end]
        
        for i, record in enumerate(visible_records):
            card_y = start_y + i * (card_height + card_spacing)
            card_rect = pygame.Rect(start_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_x, mouse_y):
                # Find the actual index in the full records list
                actual_idx = visible_start + i
                self.idx = actual_idx
                break
    
    def _check_record_hover(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse is hovering over any record card"""
        if not self.recs:
            return -1
            
        start_x = 50
        start_y = 120
        card_width = sw - 100
        card_height = self.card_height
        card_spacing = self.card_spacing
        
        # Get visible records based on scroll
        visible_start = self.scroll
        visible_end = min(self.scroll + self.records_per_page, len(self.recs))
        visible_records = self.recs[visible_start:visible_end]
        
        for i, record in enumerate(visible_records):
            card_y = start_y + i * (card_height + card_spacing)
            card_rect = pygame.Rect(start_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_x, mouse_y):
                return i
        return -1
    
    def _check_scroll_bar_click(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse clicked on scroll bar"""
        if not self.recs or len(self.recs) <= self.records_per_page:
            return
        
        scroll_bar_x = sw - 20
        scroll_bar_y = 120
        scroll_bar_height = sh - 200
        scroll_bar_width = 8
        
        # Check if click is on scroll bar area
        scroll_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
        if scroll_rect.collidepoint(mouse_x, mouse_y):
            # Start dragging
            self.dragging_scroll = True
            
            # Calculate new scroll position based on click
            relative_y = mouse_y - scroll_bar_y
            scroll_ratio = relative_y / scroll_bar_height
            new_scroll = int(scroll_ratio * self.max_scroll)
            
            # Clamp scroll position
            self.scroll = max(0, min(self.max_scroll, new_scroll))
            self.idx = self.scroll
    
    def _format_time(self, sec: int) -> str:
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"
    
    def _format_date(self, timestamp: float) -> str:
        return time.strftime("%d/%m/%Y %H:%M", time.localtime(timestamp))
    
    def _update_scroll(self):
        """Update scroll position to keep selected record at the top when possible"""
        if not self.recs:
            return
        
        # Update max scroll
        self.max_scroll = max(0, len(self.recs) - self.records_per_page)
        
        # Set scroll to show selected record at the top
        # But don't go beyond the maximum scroll position
        self.scroll = min(self.idx, self.max_scroll)
        
        # Ensure scroll is not negative
        self.scroll = max(0, self.scroll)
    
    def draw(self, screen):
        # Background with pattern
        screen.fill(self.color_bg)
        sw, sh = screen.get_size()
        
        # Draw subtle pattern
        for y in range(0, sh, 20):
            for x in range(0, sw, 20):
                if (x + y) % 40 == 0:
                    pygame.draw.rect(screen, self.color_bg_pattern, (x, y, 20, 20))
        
        # Back button
        back_rect = pygame.Rect(30, 30, 80, 40)
        back_color = self.color_back_button_hover if hasattr(self, 'hovered_back') and self.hovered_back else self.color_back_button
        pygame.draw.rect(screen, back_color, back_rect, border_radius=8)
        
        # Add subtle border for hover effect
        if hasattr(self, 'hovered_back') and self.hovered_back:
            pygame.draw.rect(screen, (150, 200, 255), back_rect, 2, border_radius=8)
        
        back_text = self.font_header.render("Back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Title
        title_text = self.font_title.render("Game History", True, self.color_title)
        title_rect = title_text.get_rect(center=(sw // 2, 80))
        screen.blit(title_text, title_rect)
        
        if not self.recs:
            # Empty state
            empty_rect = pygame.Rect(50, 120, sw - 100, 200)
            pygame.draw.rect(screen, self.color_card_bg, empty_rect, border_radius=12)
            pygame.draw.rect(screen, self.color_card_border, empty_rect, 2, border_radius=12)
            
            empty_text = self.font_card.render("No game records found", True, self.color_card_text)
            empty_text_rect = empty_text.get_rect(center=empty_rect.center)
            screen.blit(empty_text, empty_text_rect)
            return
        
        # Show records based on scroll position
        start_x = 50
        start_y = 120
        card_width = sw - 100
        card_height = self.card_height
        card_spacing = self.card_spacing
        
        # Get visible records based on scroll
        visible_start = self.scroll
        visible_end = min(self.scroll + self.records_per_page, len(self.recs))
        visible_records = self.recs[visible_start:visible_end]
        
        for i, record in enumerate(visible_records):
            card_y = start_y + i * (card_height + card_spacing)
            card_rect = pygame.Rect(start_x, card_y, card_width, card_height)
            
            # Calculate actual index in the full records list
            actual_idx = visible_start + i
            
            # Determine card color based on state
            if actual_idx == self.idx:
                # Selected card (keyboard selection)
                card_color = self.color_card_selected
                border_color = self.color_card_border
                border_width = 3
            elif i == self.hovered_record:
                # Hovered card (mouse hover)
                card_color = self.color_card_hover
                border_color = self.color_card_border
                border_width = 3
            else:
                # Normal card
                card_color = self.color_card_bg
                border_color = self.color_card_border
                border_width = 2
            
            # Draw card background
            pygame.draw.rect(screen, card_color, card_rect, border_radius=12)
            pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=12)
            
            # Draw record content
            self._draw_record_content(screen, record, card_rect, i)
        
        # Draw scroll indicator
        self._draw_scroll_indicator(screen, sw, sh)
    
    def _draw_record_content(self, screen, record, card_rect, index):
        """Draw the content of a record card"""
        x, y, w, h = card_rect
        
        # Date and time
        date_text = self._format_date(record.ts)
        date_surface = self.font_tiny.render(date_text, True, self.color_stats)
        screen.blit(date_surface, (x + 15, y + 10))
        
        # Level name
        level_text = f"Level: {record.level_name}"
        level_surface = self.font_card.render(level_text, True, self.color_card_text)
        screen.blit(level_surface, (x + 15, y + 30))
        
        # Result with color coding
        result_color = self.color_success if record.result == "WIN" else self.color_failure
        result_surface = self.font_small.render(record.result, True, result_color)
        screen.blit(result_surface, (x + w - 100, y + 15))
        
        # Score
        score_text = f"Score: {record.score}"
        score_surface = self.font_small.render(score_text, True, self.color_card_text)
        screen.blit(score_surface, (x + 15, y + 50))
        
        # Time elapsed
        time_text = f"Time: {self._format_time(record.time_elapsed_sec)}"
        time_surface = self.font_small.render(time_text, True, self.color_card_text)
        screen.blit(time_surface, (x + 200, y + 50))
        
        # Stars
        stars_text = f"Stars: {record.stars_collected}/{record.stars_total}"
        stars_surface = self.font_small.render(stars_text, True, self.color_card_text)
        screen.blit(stars_surface, (x + 350, y + 50))
        
        # Steps
        steps_text = f"Steps: {record.steps}"
        steps_surface = self.font_small.render(steps_text, True, self.color_card_text)
        screen.blit(steps_surface, (x + w - 120, y + 50))

        # Nodes expanded (nếu có và > 0)
        if hasattr(record, 'nodes_expanded') and record.nodes_expanded > 0:
            nodes_text = f"Nodes: {record.nodes_expanded}"
            nodes_surface = self.font_small.render(nodes_text, True, self.color_card_text)
            screen.blit(nodes_surface, (x + 500, y + 50))

        # Solver (nếu có)
        if hasattr(record, 'solver'):
            solver_text = f"Solver: {record.solver}"
            solver_surface = self.font_tiny.render(solver_text, True, self.color_stats)
            screen.blit(solver_surface, (x + w - 220, y + 15))
    
    def _draw_scroll_indicator(self, screen, sw, sh):
        """Draw scroll indicator and position info"""
        if not self.recs or len(self.recs) <= self.records_per_page:
            return
        
        # Draw scroll bar
        scroll_bar_x = sw - 20
        scroll_bar_y = 120
        scroll_bar_height = sh - 200
        scroll_bar_width = 8
        
        # Background of scroll bar
        scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
        pygame.draw.rect(screen, (60, 80, 100), scroll_bg_rect, border_radius=4)
        
        # Calculate scroll thumb position
        scroll_ratio = self.scroll / self.max_scroll if self.max_scroll > 0 else 0
        thumb_height = max(20, int(scroll_bar_height * (self.records_per_page / len(self.recs))))
        thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_height) * scroll_ratio)
        
        # Draw scroll thumb
        thumb_rect = pygame.Rect(scroll_bar_x, thumb_y, scroll_bar_width, thumb_height)
        pygame.draw.rect(screen, (120, 170, 220), thumb_rect, border_radius=4)
        
        # Draw position info
        position_text = f"{self.scroll + 1}-{min(self.scroll + self.records_per_page, len(self.recs))} of {len(self.recs)}"
        position_surface = self.font_tiny.render(position_text, True, self.color_stats)
        screen.blit(position_surface, (sw - 150, sh - 30))
        
        # Draw navigation hints
        if len(self.recs) > self.records_per_page:
            hint_text = "↑/↓ Navigate • PgUp/PgDn Scroll • Home/End Jump • Mouse Wheel"
            hint_surface = self.font_tiny.render(hint_text, True, self.color_stats)
            screen.blit(hint_surface, (50, sh - 30))
