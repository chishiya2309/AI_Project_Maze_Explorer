import pygame
from core.scene import Scene
from core.assets import load_image


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
        # Panel highlight colors for Team section
        self.color_panel_bg = (0, 0, 0, 140)  # semi-transparent (used via Surface with alpha)
        self.color_panel_border = (100, 150, 255)
        self.color_panel_title = (255, 255, 255)
        self.color_panel_text = (210, 220, 230)

        # Background image for main menu
        self.bg_image = load_image("menu_background.png")
    
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
            from .level_select_scene import LevelSelectScene
            self.game.scenes.switch(LevelSelectScene(self.game))
        elif self.selected_button == 1:  # History
            from .history_scene import HistoryScene
            self.game.scenes.switch(HistoryScene(self.game))
        elif self.selected_button == 2:  # Edit Map
            from .edit_level_select_scene import EditLevelSelectScene
            self.game.scenes.switch(EditLevelSelectScene(self.game))
        elif self.selected_button == 3:  # Quit
            self.game.running = False
    
    def draw(self, screen):
        sw, sh = screen.get_size()
        # Draw background image first, scaled to screen size
        if self.bg_image:
            bg_scaled = pygame.transform.smoothscale(self.bg_image, (sw, sh))
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill(self.color_bg)
        
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
        
        # Vẽ panel nổi bật hiển thị thông tin nhóm (góc phải dưới)
        group_title = "Team 09"
        group_lines = [
            "251ARIN330585_03CLC_AI_Project",
            "23110110 - Lê Quang Hưng",
            "23110078 - Nguyễn Thái Bảo",
            "23110111 - Lương Nguyễn Thành Hưng",
        ]

        # Kích thước panel
        pad_x, pad_y = 16, 12
        content_width = 0
        # Đo kích thước văn bản để tính panel
        title_surf = self.font_small.render(group_title, True, self.color_panel_title)
        content_width = max(content_width, title_surf.get_width())
        line_surfs = [self.font_tiny.render(t, True, self.color_panel_text) for t in group_lines]
        for srf in line_surfs:
            content_width = max(content_width, srf.get_width())
        content_height = title_surf.get_height() + 8 + sum(s.get_height() for s in line_surfs) + (len(line_surfs) - 1) * 4

        panel_width = content_width + pad_x * 2
        panel_height = content_height + pad_y * 2
        panel_x = sw - panel_width - 24
        panel_y = sh - panel_height - 24

        # Nền panel bán trong suốt
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.color_panel_bg)
        # Vẽ viền panel
        pygame.draw.rect(panel_surface, self.color_panel_border, panel_surface.get_rect(), width=2, border_radius=10)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Vẽ nội dung panel
        screen.blit(title_surf, (panel_x + pad_x, panel_y + pad_y))
        y_cursor = panel_y + pad_y + title_surf.get_height() + 8
        for srf in line_surfs:
            screen.blit(srf, (panel_x + pad_x, y_cursor))
            y_cursor += srf.get_height() + 4
