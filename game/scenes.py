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
        self.selected_button = 0  # 0=Start, 1=History, 2=Edit Map, 3=Quit
        
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
                self.selected_button = (self.selected_button - 1) % 4
            elif e.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % 4
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
            for i in range(4):
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
        elif self.selected_button == 2:  # Edit Map
            self.game.scenes.switch(EditMapScene(self.game))
        elif self.selected_button == 3:  # Quit
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
        
        buttons = ["Start", "History", "Edit Map", "Quit"]
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
                    self.game.scenes.switch(LevelScene(self.game, name, rows))
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                mouse_x, mouse_y = e.pos
                sw, sh = self.game.screen.get_size()
                
                # Check back button
                back_rect = pygame.Rect(30, 30, 80, 40)
                if back_rect.collidepoint(mouse_x, mouse_y):
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
                self.game.scenes.switch(LevelScene(self.game, name, self.levels[i][1]))
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

class EditMapScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font_button = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 18)
        self.font_tiny = pygame.font.SysFont("segoeui", 14)
        
        # Colors
        self.color_bg = (20, 30, 40)  # Dark background
        self.color_title = (255, 255, 255)  # White title
        self.color_back_button = (100, 150, 255)  # Blue back button
        self.color_back_button_hover = (120, 170, 255)  # Lighter blue for hover
        self.color_back_button_text = (255, 255, 255)  # White text
        
        # Grid colors
        self.color_grid_bg = (40, 50, 70)  # Dark blue grid background
        self.color_grid_border = (80, 100, 120)  # Grid border
        self.color_wall = (60, 60, 60)  # Wall color
        self.color_floor = (100, 100, 100)  # Floor color
        self.color_start = (100, 255, 100)  # Start position (green)
        self.color_goal = (255, 100, 100)  # Goal position (red)
        self.color_star = (255, 255, 100)  # Star color (yellow)
        self.color_selected = (255, 200, 100)  # Selected cell (orange)
        
        # Grid settings
        self.grid_size = 20
        self.grid_width = 15
        self.grid_height = 15
        self.cell_size = 25
        self.grid_x = 50
        self.grid_y = 100
        
        # Editor state
        self.selected_tool = 0  # 0=Wall, 1=Floor, 2=Start, 3=Goal, 4=Star
        self.tools = ["Wall", "Floor", "Start", "Goal", "Star"]
        self.tool_colors = [self.color_wall, self.color_floor, self.color_start, self.color_goal, self.color_star]
        
        # Grid data (0=floor, 1=wall, S=start, G=goal, *=star)
        self.grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Set borders as walls
        for i in range(self.grid_width):
            self.grid[0][i] = '1'
            self.grid[self.grid_height-1][i] = '1'
        for i in range(self.grid_height):
            self.grid[i][0] = '1'
            self.grid[i][self.grid_width-1] = '1'
        
        # Set default start and goal
        self.grid[1][1] = 'S'
        self.grid[self.grid_height-2][self.grid_width-2] = 'G'
        
        self.hovered_back = False
        self.hovered_cell = None
        self.dragging = False
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                self.selected_tool = e.key - pygame.K_1
            elif e.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self._save_level()
            elif e.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self._load_level()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                mouse_x, mouse_y = e.pos
                sw, sh = self.game.screen.get_size()
                
                # Check back button
                back_rect = pygame.Rect(30, 30, 80, 40)
                if back_rect.collidepoint(mouse_x, mouse_y):
                    self.game.scenes.switch(MenuScene(self.game))
                    return
                
                # Check grid click
                self._handle_grid_click(mouse_x, mouse_y)
                self.dragging = True
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:  # Left click release
                self.dragging = False
        elif e.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            
            # Check if hovering over back button
            back_rect = pygame.Rect(30, 30, 80, 40)
            self.hovered_back = back_rect.collidepoint(mouse_x, mouse_y)
            
            # Check grid hover
            self._handle_grid_hover(mouse_x, mouse_y)
            
            # Handle dragging
            if self.dragging:
                self._handle_grid_click(mouse_x, mouse_y)
            
            # Set cursor
            if self.hovered_back or self._is_grid_hover(mouse_x, mouse_y):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _handle_grid_click(self, mouse_x, mouse_y):
        """Handle clicking on the grid"""
        if not self._is_grid_hover(mouse_x, mouse_y):
            return
        
        # Calculate grid position
        grid_x = (mouse_x - self.grid_x) // self.cell_size
        grid_y = (mouse_y - self.grid_y) // self.cell_size
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self._place_tile(grid_x, grid_y)
    
    def _handle_grid_hover(self, mouse_x, mouse_y):
        """Handle hovering over the grid"""
        if self._is_grid_hover(mouse_x, mouse_y):
            grid_x = (mouse_x - self.grid_x) // self.cell_size
            grid_y = (mouse_y - self.grid_y) // self.cell_size
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.hovered_cell = (grid_x, grid_y)
            else:
                self.hovered_cell = None
        else:
            self.hovered_cell = None
    
    def _is_grid_hover(self, mouse_x, mouse_y):
        """Check if mouse is over the grid"""
        return (self.grid_x <= mouse_x < self.grid_x + self.grid_width * self.cell_size and
                self.grid_y <= mouse_y < self.grid_y + self.grid_height * self.cell_size)
    
    def _place_tile(self, grid_x, grid_y):
        """Place a tile at the given grid position"""
        tool = self.selected_tool
        
        if tool == 0:  # Wall
            self.grid[grid_y][grid_x] = '1'
        elif tool == 1:  # Floor
            self.grid[grid_y][grid_x] = '0'
        elif tool == 2:  # Start
            # Remove existing start
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid[y][x] == 'S':
                        self.grid[y][x] = '0'
            self.grid[grid_y][grid_x] = 'S'
        elif tool == 3:  # Goal
            # Remove existing goal
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid[y][x] == 'G':
                        self.grid[y][x] = '0'
            self.grid[grid_y][grid_x] = 'G'
        elif tool == 4:  # Star
            self.grid[grid_y][grid_x] = '*'
    
    def _save_level(self):
        """Save the current level"""
        try:
            # Create a simple filename
            filename = f"data/levels/level_edited.txt"
            with open(filename, 'w') as f:
                for row in self.grid:
                    f.write(''.join(row) + '\n')
            print(f"Level saved to {filename}")
        except Exception as e:
            print(f"Error saving level: {e}")
    
    def _load_level(self):
        """Load a level file"""
        try:
            filename = f"data/levels/level01.txt"
            with open(filename, 'r') as f:
                lines = f.readlines()
                for y, line in enumerate(lines):
                    if y < self.grid_height:
                        for x, char in enumerate(line.strip()):
                            if x < self.grid_width:
                                self.grid[y][x] = char
            print(f"Level loaded from {filename}")
        except Exception as e:
            print(f"Error loading level: {e}")
    
    def draw(self, screen):
        screen.fill(self.color_bg)
        sw, sh = screen.get_size()
        
        # Back button
        back_rect = pygame.Rect(30, 30, 80, 40)
        back_color = self.color_back_button_hover if self.hovered_back else self.color_back_button
        pygame.draw.rect(screen, back_color, back_rect, border_radius=8)
        
        if self.hovered_back:
            pygame.draw.rect(screen, (150, 200, 255), back_rect, 2, border_radius=8)
        
        back_text = self.font_button.render("Back", True, self.color_back_button_text)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Title
        title_text = self.font_title.render("Edit Map", True, self.color_title)
        title_rect = title_text.get_rect(center=(sw // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Tool selection
        tool_y = 80
        tool_width = 80
        tool_height = 30
        tool_spacing = 10
        
        for i, tool in enumerate(self.tools):
            tool_x = 200 + i * (tool_width + tool_spacing)
            tool_rect = pygame.Rect(tool_x, tool_y, tool_width, tool_height)
            
            # Tool background
            if i == self.selected_tool:
                pygame.draw.rect(screen, self.tool_colors[i], tool_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), tool_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, self.color_grid_bg, tool_rect, border_radius=5)
                pygame.draw.rect(screen, self.tool_colors[i], tool_rect, 2, border_radius=5)
            
            # Tool text
            tool_text = self.font_small.render(tool, True, (255, 255, 255))
            tool_text_rect = tool_text.get_rect(center=tool_rect.center)
            screen.blit(tool_text, tool_text_rect)
        
        # Instructions
        instructions = [
            "Click to place tiles",
            "1-5: Select tool",
            "Ctrl+S: Save",
            "Ctrl+L: Load"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.font_tiny.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (sw - 200, 80 + i * 20))
        
        # Draw grid
        self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        """Draw the editing grid"""
        # Grid background
        grid_rect = pygame.Rect(self.grid_x, self.grid_y, 
                               self.grid_width * self.cell_size, 
                               self.grid_height * self.cell_size)
        pygame.draw.rect(screen, self.color_grid_bg, grid_rect)
        pygame.draw.rect(screen, self.color_grid_border, grid_rect, 2)
        
        # Draw grid lines
        for x in range(self.grid_width + 1):
            start_pos = (self.grid_x + x * self.cell_size, self.grid_y)
            end_pos = (self.grid_x + x * self.cell_size, self.grid_y + self.grid_height * self.cell_size)
            pygame.draw.line(screen, self.color_grid_border, start_pos, end_pos)
        
        for y in range(self.grid_height + 1):
            start_pos = (self.grid_x, self.grid_y + y * self.cell_size)
            end_pos = (self.grid_x + self.grid_width * self.cell_size, self.grid_y + y * self.cell_size)
            pygame.draw.line(screen, self.color_grid_border, start_pos, end_pos)
        
        # Draw cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_x = self.grid_x + x * self.cell_size
                cell_y = self.grid_y + y * self.cell_size
                cell_rect = pygame.Rect(cell_x + 1, cell_y + 1, self.cell_size - 2, self.cell_size - 2)
                
                char = self.grid[y][x]
                
                if char == '1':  # Wall
                    pygame.draw.rect(screen, self.color_wall, cell_rect)
                elif char == 'S':  # Start
                    pygame.draw.rect(screen, self.color_start, cell_rect)
                elif char == 'G':  # Goal
                    pygame.draw.rect(screen, self.color_goal, cell_rect)
                elif char == '*':  # Star
                    pygame.draw.rect(screen, self.color_star, cell_rect)
                else:  # Floor
                    pygame.draw.rect(screen, self.color_floor, cell_rect)
        
        # Draw hovered cell
        if self.hovered_cell:
            hover_x, hover_y = self.hovered_cell
            cell_x = self.grid_x + hover_x * self.cell_size
            cell_y = self.grid_y + hover_y * self.cell_size
            hover_rect = pygame.Rect(cell_x + 1, cell_y + 1, self.cell_size - 2, self.cell_size - 2)
            pygame.draw.rect(screen, self.color_selected, hover_rect, 3)
