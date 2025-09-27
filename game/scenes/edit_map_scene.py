import pygame
from core.scene import Scene


class EditMapScene(Scene):
    def __init__(self, game, level_name="new_map", existing_rows=None, width=None, height=None):
        super().__init__(game)
        self.level_name = level_name
        self.existing_rows = existing_rows
        self.custom_width = width
        self.custom_height = height
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
        
        # Grid settings - will be set dynamically based on loaded level or custom size
        if self.custom_width and self.custom_height:
            self.grid_width = self.custom_width
            self.grid_height = self.custom_height
        else:
            self.grid_width = 15  # Default size
            self.grid_height = 15  # Default size
        self.cell_size = 25
        self.min_cell_size = 10  # Minimum cell size for zoom out
        self.max_cell_size = 50  # Maximum cell size for zoom in
        self.grid_x = 50
        self.grid_y = 100
        
        # Zoom and scroll settings
        self.zoom_level = 1.0
        self.scroll_x = 0
        self.scroll_y = 0
        self.dragging_scroll = False
        self.last_mouse_pos = (0, 0)
        
        # Editor state
        self.selected_tool = 0  # 0=Wall, 1=Floor, 2=Start, 3=Goal, 4=Star
        self.tools = ["Wall", "Floor", "Start", "Goal", "Star"]
        self.tool_colors = [self.color_wall, self.color_floor, self.color_start, self.color_goal, self.color_star]
        
        # Grid data (0=floor, 1=wall, S=start, G=goal, *=star)
        self.grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        if self.existing_rows:
            # Load existing level
            self._load_existing_level()
        else:
            # Create new level with default setup
            self._setup_new_level()
        
        self.hovered_back = False
        self.hovered_cell = None
        self.dragging = False
    
    def _load_existing_level(self):
        """Load an existing level into the grid"""
        if not self.existing_rows:
            return
        
        # Get actual dimensions of the level
        actual_height = len(self.existing_rows)
        actual_width = len(self.existing_rows[0]) if self.existing_rows else 0
        
        # Update grid dimensions to match the actual level
        self.grid_width = actual_width
        self.grid_height = actual_height
        
        # Recreate grid with correct dimensions
        self.grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Load existing level data
        for y, row in enumerate(self.existing_rows):
            if y < self.grid_height:
                for x, char in enumerate(row):
                    if x < self.grid_width:
                        self.grid[y][x] = char
        
        # Center the grid on screen
        self._center_grid()
    
    def _center_grid(self):
        """Center the grid on the screen"""
        # Get screen dimensions (we'll get them in the draw method)
        # For now, set default centering
        self.grid_x = 50
        self.grid_y = 100
    
    def _update_grid_position(self, screen_width, screen_height):
        """Update grid position to center it on screen"""
        # Calculate actual cell size based on zoom
        actual_cell_size = int(self.cell_size * self.zoom_level)
        actual_cell_size = max(self.min_cell_size, min(self.max_cell_size, actual_cell_size))
        
        grid_pixel_width = self.grid_width * actual_cell_size
        grid_pixel_height = self.grid_height * actual_cell_size
        
        # Center horizontally and vertically, leaving space for UI
        base_x = (screen_width - grid_pixel_width) // 2
        base_y = (screen_height - grid_pixel_height) // 2 + 50  # +50 for title space
        
        # Apply scroll offset
        self.grid_x = base_x + self.scroll_x
        self.grid_y = base_y + self.scroll_y
    
    def _setup_new_level(self):
        """Setup a new level with default configuration"""
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
        
        # Center the grid on screen
        self._center_grid()
    
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                from .menu_scene import MenuScene
                self.game.scenes.switch(MenuScene(self.game))
            elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                self.selected_tool = e.key - pygame.K_1
            elif e.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self._save_level()
            elif e.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self._load_level()
            elif e.key == pygame.K_PLUS or e.key == pygame.K_EQUALS:
                self._zoom_in()
            elif e.key == pygame.K_MINUS:
                self._zoom_out()
            elif e.key == pygame.K_0:
                self._reset_zoom()
        elif e.type == pygame.MOUSEWHEEL:
            # Handle zoom with mouse wheel
            if e.y > 0:  # Scroll up - zoom in
                self._zoom_in()
            elif e.y < 0:  # Scroll down - zoom out
                self._zoom_out()
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
                
                # Check if clicking on grid for editing
                if self._is_grid_hover(mouse_x, mouse_y):
                    self._handle_grid_click(mouse_x, mouse_y)
                    self.dragging = True
                else:
                    # Start dragging for scroll
                    self.dragging_scroll = True
                    self.last_mouse_pos = (mouse_x, mouse_y)
            elif e.button == 2:  # Middle click - reset zoom
                self._reset_zoom()
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:  # Left click release
                self.dragging = False
                self.dragging_scroll = False
        elif e.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = e.pos
            sw, sh = self.game.screen.get_size()
            
            # Check if hovering over back button
            back_rect = pygame.Rect(30, 30, 80, 40)
            self.hovered_back = back_rect.collidepoint(mouse_x, mouse_y)
            
            # Handle scroll dragging
            if self.dragging_scroll:
                dx = mouse_x - self.last_mouse_pos[0]
                dy = mouse_y - self.last_mouse_pos[1]
                self.scroll_x += dx
                self.scroll_y += dy
                self.last_mouse_pos = (mouse_x, mouse_y)
            
            # Check grid hover
            self._handle_grid_hover(mouse_x, mouse_y)
            
            # Handle dragging for editing
            if self.dragging:
                self._handle_grid_click(mouse_x, mouse_y)
            
            # Set cursor
            if self.hovered_back or self._is_grid_hover(mouse_x, mouse_y):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif self.dragging_scroll:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _handle_grid_click(self, mouse_x, mouse_y):
        """Handle clicking on the grid"""
        if not self._is_grid_hover(mouse_x, mouse_y):
            return
        
        # Calculate actual cell size based on zoom
        actual_cell_size = int(self.cell_size * self.zoom_level)
        actual_cell_size = max(self.min_cell_size, min(self.max_cell_size, actual_cell_size))
        
        # Calculate grid position
        grid_x = (mouse_x - self.grid_x) // actual_cell_size
        grid_y = (mouse_y - self.grid_y) // actual_cell_size
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self._place_tile(grid_x, grid_y)
    
    def _handle_grid_hover(self, mouse_x, mouse_y):
        """Handle hovering over the grid"""
        if self._is_grid_hover(mouse_x, mouse_y):
            # Calculate actual cell size based on zoom
            actual_cell_size = int(self.cell_size * self.zoom_level)
            actual_cell_size = max(self.min_cell_size, min(self.max_cell_size, actual_cell_size))
            
            grid_x = (mouse_x - self.grid_x) // actual_cell_size
            grid_y = (mouse_y - self.grid_y) // actual_cell_size
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.hovered_cell = (grid_x, grid_y)
            else:
                self.hovered_cell = None
        else:
            self.hovered_cell = None
    
    def _is_grid_hover(self, mouse_x, mouse_y):
        """Check if mouse is over the grid"""
        actual_cell_size = int(self.cell_size * self.zoom_level)
        actual_cell_size = max(self.min_cell_size, min(self.max_cell_size, actual_cell_size))
        
        grid_pixel_width = self.grid_width * actual_cell_size
        grid_pixel_height = self.grid_height * actual_cell_size
        
        return (self.grid_x <= mouse_x < self.grid_x + grid_pixel_width and
                self.grid_y <= mouse_y < self.grid_y + grid_pixel_height)
    
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
            # Create filename based on level name
            if self.level_name == "new_map":
                # Generate a unique filename for new maps
                import time
                timestamp = int(time.time())
                filename = f"data/levels/level_custom_{timestamp}.txt"
            else:
                # For existing levels, save to the original file (ghi đè lên file cũ)
                # Đảm bảo tên file có extension .txt
                if not self.level_name.endswith('.txt'):
                    filename = f"data/levels/{self.level_name}.txt"
                else:
                    filename = f"data/levels/{self.level_name}"
            
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
                
                # Get actual dimensions
                actual_height = len(lines)
                actual_width = len(lines[0].strip()) if lines else 0
                
                # Update grid dimensions
                self.grid_width = actual_width
                self.grid_height = actual_height
                
                # Recreate grid with correct dimensions
                self.grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
                
                # Load data
                for y, line in enumerate(lines):
                    if y < self.grid_height:
                        for x, char in enumerate(line.strip()):
                            if x < self.grid_width:
                                self.grid[y][x] = char
                
                # Center the grid
                self._center_grid()
                
            print(f"Level loaded from {filename}")
        except Exception as e:
            print(f"Error loading level: {e}")
    
    def _zoom_in(self):
        """Zoom in the grid"""
        self.zoom_level = min(2.0, self.zoom_level * 1.2)
    
    def _zoom_out(self):
        """Zoom out the grid"""
        self.zoom_level = max(0.3, self.zoom_level / 1.2)
    
    def _reset_zoom(self):
        """Reset zoom to fit the screen"""
        # Calculate zoom level to fit the grid on screen
        # This will be called in _update_grid_position
        self.zoom_level = 1.0
        self.scroll_x = 0
        self.scroll_y = 0
    
    def draw(self, screen):
        screen.fill(self.color_bg)
        sw, sh = screen.get_size()
        
        # Update grid position to center it
        self._update_grid_position(sw, sh)
        
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
        if self.level_name == "new_map":
            title_text = self.font_title.render("Create New Map", True, self.color_title)
        else:
            title_text = self.font_title.render(f"Edit {self.level_name}", True, self.color_title)
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
            "Ctrl+S: Save, Ctrl+L: Load",
            "Mouse wheel: Zoom",
            "Drag: Scroll, 0: Reset zoom"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.font_tiny.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (sw - 200, 80 + i * 20))
        
        # Draw grid
        self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        """Draw the editing grid"""
        # Calculate actual cell size based on zoom
        actual_cell_size = int(self.cell_size * self.zoom_level)
        actual_cell_size = max(self.min_cell_size, min(self.max_cell_size, actual_cell_size))
        
        # Grid background
        grid_rect = pygame.Rect(self.grid_x, self.grid_y, 
                               self.grid_width * actual_cell_size, 
                               self.grid_height * actual_cell_size)
        pygame.draw.rect(screen, self.color_grid_bg, grid_rect)
        pygame.draw.rect(screen, self.color_grid_border, grid_rect, 2)
        
        # Draw grid lines
        for x in range(self.grid_width + 1):
            start_pos = (self.grid_x + x * actual_cell_size, self.grid_y)
            end_pos = (self.grid_x + x * actual_cell_size, self.grid_y + self.grid_height * actual_cell_size)
            pygame.draw.line(screen, self.color_grid_border, start_pos, end_pos)
        
        for y in range(self.grid_height + 1):
            start_pos = (self.grid_x, self.grid_y + y * actual_cell_size)
            end_pos = (self.grid_x + self.grid_width * actual_cell_size, self.grid_y + y * actual_cell_size)
            pygame.draw.line(screen, self.color_grid_border, start_pos, end_pos)
        
        # Draw cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_x = self.grid_x + x * actual_cell_size
                cell_y = self.grid_y + y * actual_cell_size
                cell_rect = pygame.Rect(cell_x + 1, cell_y + 1, actual_cell_size - 2, actual_cell_size - 2)
                
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
            cell_x = self.grid_x + hover_x * actual_cell_size
            cell_y = self.grid_y + hover_y * actual_cell_size
            hover_rect = pygame.Rect(cell_x + 1, cell_y + 1, actual_cell_size - 2, actual_cell_size - 2)
            pygame.draw.rect(screen, self.color_selected, hover_rect, 3)
