import pygame
from core.scene import Scene


class MapSizeSelectionScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font_button = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_size = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_tiny = pygame.font.SysFont("segoeui", 16)
        
        # Colors
        self.color_bg = (20, 30, 40)  # Dark background
        self.color_title = (255, 255, 255)  # White title
        self.color_back_button = (100, 150, 255)  # Blue back button
        self.color_back_button_hover = (120, 170, 255)  # Lighter blue for hover
        self.color_back_button_text = (255, 255, 255)  # White text
        
        # Size preset colors
        self.color_preset_bg = (40, 50, 70)  # Dark blue preset background
        self.color_preset_hover = (60, 80, 100)  # Lighter blue for hover
        self.color_preset_selected = (80, 120, 160)  # Even lighter for selected
        self.color_preset_text = (255, 255, 255)  # White text on presets
        self.color_preset_border = (100, 150, 200)  # Border color
        
        # Custom size colors
        self.color_custom_bg = (60, 40, 80)  # Purple background for custom
        self.color_custom_hover = (80, 60, 100)  # Lighter purple for hover
        self.color_custom_selected = (100, 80, 120)  # Even lighter for selected
        self.color_custom_border = (120, 80, 160)  # Purple border
        
        # Form input - improved with better defaults and validation
        self.rows = 15
        self.cols = 15
        self.input_rows = False
        self.input_cols = False
        self.hovered_back = False
        
        # Input validation and limits
        self.min_size = 10
        self.max_size = 50
        self.input_text_rows = "15"
        self.input_text_cols = "15"
        self.cursor_blink = 0
        self.cursor_visible = True
        
        # Form layout - improved sizing and positioning
        self.form_width = 400
        self.form_height = 280
        self.input_width = 140
        self.input_height = 45
        self.label_width = 120
        self.input_spacing = 60
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                from .edit_level_select_scene import EditLevelSelectScene
                self.game.scenes.switch(EditLevelSelectScene(self.game))
            elif e.key == pygame.K_RETURN:
                self._create_map()
            # Keyboard navigation between inputs
            elif e.key == pygame.K_TAB:
                # Switch between rows and cols input
                if self.input_rows:
                    self.input_rows = False
                    self.input_cols = True
                elif self.input_cols:
                    self.input_cols = False
                    self.input_rows = True
                else:
                    self.input_rows = True
            elif self.input_rows or self.input_cols:
                # Handle text input with proper validation
                if e.key == pygame.K_BACKSPACE:
                    if self.input_rows and len(self.input_text_rows) > 0:
                        self.input_text_rows = self.input_text_rows[:-1]
                        self._update_rows_from_text()
                    elif self.input_cols and len(self.input_text_cols) > 0:
                        self.input_text_cols = self.input_text_cols[:-1]
                        self._update_cols_from_text()
                elif (e.key >= pygame.K_0 and e.key <= pygame.K_9) or (e.key >= pygame.K_KP0 and e.key <= pygame.K_KP9):
                    # Handle both regular number keys and numpad keys
                    if e.key >= pygame.K_0 and e.key <= pygame.K_9:
                        digit = str(e.key - pygame.K_0)
                    else:  # numpad keys
                        digit = str(e.key - pygame.K_KP0)
                    
                    if self.input_rows:
                        # Limit input length to prevent huge numbers
                        if len(self.input_text_rows) < 3:
                            self.input_text_rows += digit
                            self._update_rows_from_text()
                    elif self.input_cols:
                        # Limit input length to prevent huge numbers
                        if len(self.input_text_cols) < 3:
                            self.input_text_cols += digit
                            self._update_cols_from_text()
                elif e.key == pygame.K_DELETE:
                    # Clear current input
                    if self.input_rows:
                        self.input_text_rows = ""
                        self.rows = self.min_size
                    elif self.input_cols:
                        self.input_text_cols = ""
                        self.cols = self.min_size
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                mouse_x, mouse_y = e.pos
                sw, sh = self.game.screen.get_size()
                
                # Check back button
                back_rect = pygame.Rect(30, 30, 80, 40)
                if back_rect.collidepoint(mouse_x, mouse_y):
                    from .edit_level_select_scene import EditLevelSelectScene
                    self.game.scenes.switch(EditLevelSelectScene(self.game))
                    return
                
                # Check form input clicks
                self._check_form_input_click(mouse_x, mouse_y, sw, sh)
        elif e.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            
            # Check if hovering over back button
            back_rect = pygame.Rect(30, 30, 80, 40)
            self.hovered_back = back_rect.collidepoint(mouse_x, mouse_y)
            
            # Set cursor
            if self.hovered_back:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _check_form_input_click(self, mouse_x, mouse_y, sw, sh):
        """Check if mouse clicked on form input fields"""
        # Calculate form position (centered)
        form_x = (sw - self.form_width) // 2
        form_y = (sh - self.form_height) // 2
        
        # Rows input field - positioned at right edge
        rows_input_rect = pygame.Rect(form_x + self.form_width - self.input_width - 20, form_y + 35, self.input_width, self.input_height)
        if rows_input_rect.collidepoint(mouse_x, mouse_y):
            self.input_rows = True
            self.input_cols = False
            return
        
        # Cols input field - positioned at right edge
        cols_input_rect = pygame.Rect(form_x + self.form_width - self.input_width - 20, form_y + 95, self.input_width, self.input_height)
        if cols_input_rect.collidepoint(mouse_x, mouse_y):
            self.input_rows = False
            self.input_cols = True
            return
        
        # Click outside - deselect all inputs
        self.input_rows = False
        self.input_cols = False
    
    def _update_rows_from_text(self):
        """Update rows value from text input with validation"""
        if not self.input_text_rows:
            # Allow empty input - don't auto-fill with min_size
            self.rows = 0  # Use 0 to indicate empty/invalid
            return
        
        try:
            value = int(self.input_text_rows)
            if value < self.min_size or value > self.max_size:
                self.rows = value  # Keep the invalid value for error display
            else:
                self.rows = value
        except ValueError:
            self.rows = 0  # Invalid input
    
    def _update_cols_from_text(self):
        """Update cols value from text input with validation"""
        if not self.input_text_cols:
            # Allow empty input - don't auto-fill with min_size
            self.cols = 0  # Use 0 to indicate empty/invalid
            return
        
        try:
            value = int(self.input_text_cols)
            if value < self.min_size or value > self.max_size:
                self.cols = value  # Keep the invalid value for error display
            else:
                self.cols = value
        except ValueError:
            self.cols = 0  # Invalid input
    
    def _is_valid_size(self):
        """Check if current size is valid"""
        return (self.min_size <= self.rows <= self.max_size and 
                self.min_size <= self.cols <= self.max_size and
                self.rows > 0 and self.cols > 0)
    
    def _get_validation_message(self):
        """Get validation error message"""
        if not self.input_text_rows and not self.input_text_cols:
            return "Please enter map dimensions"
        elif not self.input_text_rows:
            return "Please enter number of rows"
        elif not self.input_text_cols:
            return "Please enter number of columns"
        elif self.rows < self.min_size or self.rows > self.max_size:
            return f"Rows must be between {self.min_size} and {self.max_size}"
        elif self.cols < self.min_size or self.cols > self.max_size:
            return f"Columns must be between {self.min_size} and {self.max_size}"
        else:
            return ""
    
    def _create_map(self):
        """Create a new map with entered size"""
        # Only create if input is valid
        if not self._is_valid_size():
            return  # Don't create map if input is invalid
        
        # Use the validated values
        width = self.cols
        height = self.rows
        
        # Create map with smooth transition
        from .edit_map_scene import EditMapScene
        self.game.scenes.switch(EditMapScene(self.game, "new_map", None, width, height))
    
    def draw(self, screen):
        screen.fill(self.color_bg)
        sw, sh = screen.get_size()
        
        # Update cursor blink
        self.cursor_blink += 1
        if self.cursor_blink >= 30:  # Blink every 30 frames (0.5 seconds at 60fps)
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink = 0
        
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
        title_text = self.font_title.render("Enter Map Size", True, self.color_title)
        title_rect = title_text.get_rect(center=(sw // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Form container
        form_x = (sw - self.form_width) // 2
        form_y = (sh - self.form_height) // 2
        
        # Form background with shadow effect
        shadow_rect = pygame.Rect(form_x + 4, form_y + 4, self.form_width, self.form_height)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)
        
        form_rect = pygame.Rect(form_x, form_y, self.form_width, self.form_height)
        pygame.draw.rect(screen, self.color_custom_bg, form_rect, border_radius=12)
        
        # Enhanced border for active form
        border_color = (150, 200, 255) if (self.input_rows or self.input_cols) else self.color_custom_border
        border_width = 3 if (self.input_rows or self.input_cols) else 2
        pygame.draw.rect(screen, border_color, form_rect, border_width, border_radius=12)
        
        # Rows input section - label left, input right
        rows_label = self.font_size.render("Số dòng (Rows):", True, self.color_preset_text)
        screen.blit(rows_label, (form_x + 20, form_y + 40))
        
        # Position input field at the right edge of the form
        rows_input_rect = pygame.Rect(form_x + self.form_width - self.input_width - 20, form_y + 35, self.input_width, self.input_height)
        
        # Enhanced input field styling
        if self.input_rows:
            # Active input - bright background with glow effect
            pygame.draw.rect(screen, (255, 255, 150), rows_input_rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 0), rows_input_rect, 3, border_radius=8)
        else:
            # Inactive input
            pygame.draw.rect(screen, self.color_preset_bg, rows_input_rect, border_radius=8)
            pygame.draw.rect(screen, self.color_preset_border, rows_input_rect, 2, border_radius=8)
        
        # Input text with better positioning - show actual input text
        display_text = self.input_text_rows if self.input_text_rows else ""
        if not display_text:
            display_text = "Enter rows"
        rows_text = self.font_size.render(display_text, True, (0, 0, 0) if self.input_rows else self.color_preset_text)
        rows_text_rect = rows_text.get_rect(center=rows_input_rect.center)
        screen.blit(rows_text, rows_text_rect)
        
        # Cols input section - label left, input right
        cols_label = self.font_size.render("Số cột (Cols):", True, self.color_preset_text)
        screen.blit(cols_label, (form_x + 20, form_y + 100))
        
        # Position input field at the right edge of the form
        cols_input_rect = pygame.Rect(form_x + self.form_width - self.input_width - 20, form_y + 95, self.input_width, self.input_height)
        
        # Enhanced input field styling
        if self.input_cols:
            # Active input - bright background with glow effect
            pygame.draw.rect(screen, (255, 255, 150), cols_input_rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 0), cols_input_rect, 3, border_radius=8)
        else:
            # Inactive input
            pygame.draw.rect(screen, self.color_preset_bg, cols_input_rect, border_radius=8)
            pygame.draw.rect(screen, self.color_preset_border, cols_input_rect, 2, border_radius=8)
        
        # Input text with better positioning - show actual input text
        display_text = self.input_text_cols if self.input_text_cols else ""
        if not display_text:
            display_text = "Enter cols"
        cols_text = self.font_size.render(display_text, True, (0, 0, 0) if self.input_cols else self.color_preset_text)
        cols_text_rect = cols_text.get_rect(center=cols_input_rect.center)
        screen.blit(cols_text, cols_text_rect)
        
        # Add blinking cursor indicator for active input
        if (self.input_rows or self.input_cols) and self.cursor_visible:
            cursor_x = form_x + self.form_width - self.input_width - 20 + self.input_width - 15
            cursor_y = form_y + 35 + 10 if self.input_rows else form_y + 95 + 10
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 20), 2)
        
        # Instructions with better styling - positioned better for new form size
        instructions_bg = pygame.Rect(sw - 280, 70, 260, 160)
        pygame.draw.rect(screen, (40, 50, 70), instructions_bg, border_radius=8)
        pygame.draw.rect(screen, (100, 150, 200), instructions_bg, 2, border_radius=8)
        
        instructions = [
            "Click to select input",
            "Tab: Switch input", 
            "0-9 or Numpad: Enter numbers",
            "Backspace: Delete",
            "Delete: Clear field",
            "Enter: Create map",
            f"Range: {self.min_size}-{self.max_size}"
        ]
        
        for i, instruction in enumerate(instructions):
            color = (255, 255, 100) if i < 5 else (200, 200, 200)
            inst_text = self.font_tiny.render(instruction, True, color)
            screen.blit(inst_text, (sw - 270, 80 + i * 20))
        
        # Current size display with validation status
        if self._is_valid_size():
            size_text = f"Map size: {self.rows} x {self.cols}"
            size_color = (100, 255, 100)
        else:
            size_text = f"Current: {self.rows if self.rows > 0 else '?'} x {self.cols if self.cols > 0 else '?'}"
            size_color = (255, 100, 100)
        
        size_surface = self.font_small.render(size_text, True, size_color)
        size_rect = size_surface.get_rect(center=(sw // 2, form_y + self.form_height + 50))
        screen.blit(size_surface, size_rect)
        
        # Validation message - more detailed and helpful
        validation_msg = self._get_validation_message()
        if validation_msg:
            # Error message background
            error_bg = pygame.Rect(sw // 2 - 180, form_y + self.form_height + 70, 360, 35)
            pygame.draw.rect(screen, (40, 20, 20), error_bg, border_radius=8)
            pygame.draw.rect(screen, (255, 100, 100), error_bg, 2, border_radius=8)
            
            warning_surface = self.font_tiny.render(validation_msg, True, (255, 200, 200))
            warning_rect = warning_surface.get_rect(center=(sw // 2, form_y + self.form_height + 87))
            screen.blit(warning_surface, warning_rect)
        else:
            # Success message
            success_text = "Valid map size - Press Enter to create"
            success_surface = self.font_tiny.render(success_text, True, (100, 255, 100))
            success_rect = success_surface.get_rect(center=(sw // 2, form_y + self.form_height + 80))
            screen.blit(success_surface, success_rect)
