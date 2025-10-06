# maze_explorer/game/level.py
import pygame
import time
from typing import List
from core.engine import (
    COLOR_BG, COLOR_WALL, COLOR_PATH, COLOR_PLAYER, COLOR_GOAL_UNLOCK, 
    COLOR_GOAL_LOCK, COLOR_STAR, GRID_OFFSET_X, GRID_OFFSET_Y, TILE,
    PlayRecord
)
from core.scene import Scene
from game.player import Player
from game.grid import Grid
from game.collectibles import StarCollector
from game.hud import HUD
from core.assets import load_image
import random
from game.ai_control import AIController

class LevelScene(Scene):
    def __init__(self, game, name: str, rows: List[str]):
        super().__init__(game)
        self.name = name
        self.grid = Grid(rows)
        
        # Khởi tạo player và goal
        start_pos, self.goal = self.grid.find_start_goal()
        self.player = Player(*start_pos)
        
        # Khởi tạo star collector
        stars = self.grid.find_stars()
        self.star_collector = StarCollector(stars)
        
        # Game state
        self.score = 0
        self.steps = 0
        self.time_elapsed = 0
        self.cool = 0  # Cooldown cho movement
        self.result = None
        self.timer = 0  # Timer cho hiển thị kết quả
        
        # HUD
        self.hud = HUD()
        # Load images first (needed before layout scaling)
        self.img_carrot_base = load_image("carrot.png")
        self.img_door_closed_base = load_image("closed_door.png")
        self.img_door_open_base = load_image("open_door.png")
        # Background image for play area (below header)
        self.img_bg_base = load_image("background.png")
        # Load all wall variants
        self.img_wall_bases = [
            load_image("tuong1.png"),
            load_image("tuong2.png"),
            load_image("tuong3.png"),
            load_image("tuong4.png"),
        ]
        # Build a deterministic random index map per wall cell so textures stay stable while playing
        self._build_wall_variant_map()
        
        # Load individual bunny direction images
        self.img_bunny_up_base = load_image("bunny_up.png")
        self.img_bunny_down_base = load_image("bunny_down.png")
        self.img_bunny_left_base = load_image("bunny_left.png")
        self.img_bunny_right_base = load_image("bunny_right.png")
        
        # Load chang e image for final map goal
        self.img_chang_e_base = load_image("chang_e.png")

        # View/scale state for responsive rendering
        self.scale = 1.0
        self.min_scale = 0.5
        self.max_scale = 3.0
        self.tile = TILE
        self.offset_x = GRID_OFFSET_X
        self.offset_y = GRID_OFFSET_Y
        self._recompute_layout()
        # AI controller (mặc định: người chơi điều khiển)
        self.ai = AIController()
        # Lưu số nút mở rộng khi hoàn tất để hiển thị sau khi xong
        self.nodes_expanded_display = 0
        # Font hiển thị trạng thái AI
        self.font_ai = pygame.font.SysFont("segoeui", 18, bold=True)
        # Font hiển thị thông tin nhóm
        self.font_group = pygame.font.SysFont("segoeui", 14)
        # Font cho nút Next Level
        self.font_button = pygame.font.SysFont("segoeui", 24, bold=True)
        # Trạng thái hover nút Next
        self._hover_next = False

    def _recompute_layout(self):
        """Recompute tile size and offsets to center the grid for current screen."""
        screen_w, screen_h = self.game.screen.get_size()
        # Keep margins for header only (no footer)
        header_height = 80
        margin_x = 32
        margin_y = 32
        avail_w = max(1, screen_w - margin_x * 2)
        avail_h = max(1, screen_h - header_height - margin_y * 2)
        fit_tile = max(8, min(avail_w // max(1, self.grid.W), avail_h // max(1, self.grid.H)))
        self.tile = max(8, int(fit_tile * self.scale))
        grid_px_w = self.grid.W * self.tile
        grid_px_h = self.grid.H * self.tile
        self.offset_x = (screen_w - grid_px_w) // 2
        self.offset_y = header_height + (avail_h - grid_px_h) // 2
        # Rescale background for the playable area under the header
        try:
            bg_height = max(1, screen_h - header_height)
            self.img_bg = pygame.transform.smoothscale(self.img_bg_base, (screen_w, bg_height))
        except Exception:
            self.img_bg = None
        self._rescale_sprites()

    def _rescale_sprites(self):
        """Scale cached images to current tile size."""
        # Doors fill the tile with small padding similar to previous rectangle
        pad = max(4, self.tile // 6)
        door_size = max(1, self.tile - pad * 2)
        self.door_pad = pad
        self.img_door_closed = pygame.transform.smoothscale(self.img_door_closed_base, (door_size, door_size))
        self.img_door_open = pygame.transform.smoothscale(self.img_door_open_base, (door_size, door_size))
        # Carrot takes about half of the tile
        carrot_size = max(2, self.tile // 2)
        self.img_carrot = pygame.transform.smoothscale(self.img_carrot_base, (carrot_size, carrot_size))
        self.carrot_half = carrot_size // 2
        # Wall fills the entire tile - scale variants
        self.img_walls = [
            pygame.transform.smoothscale(img, (self.tile, self.tile))
            for img in self.img_wall_bases
        ]
        # Scale bunny images to fit tile size
        bunny_size = max(8, self.tile - 4)  # Slightly smaller than tile
        self.img_bunny_up = pygame.transform.smoothscale(self.img_bunny_up_base, (bunny_size, bunny_size))
        self.img_bunny_down = pygame.transform.smoothscale(self.img_bunny_down_base, (bunny_size, bunny_size))
        self.img_bunny_left = pygame.transform.smoothscale(self.img_bunny_left_base, (bunny_size, bunny_size))
        self.img_bunny_right = pygame.transform.smoothscale(self.img_bunny_right_base, (bunny_size, bunny_size))
        
        # Scale chang e image to fit tile size (for final map goal)
        chang_e_size = max(8, self.tile - 4)  # Same size as bunny
        self.img_chang_e = pygame.transform.smoothscale(self.img_chang_e_base, (chang_e_size, chang_e_size))

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            from game.scenes import LevelSelectScene
            self.game.scenes.switch(LevelSelectScene(self.game))
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                mouse_x, mouse_y = e.pos
                # Check if clicking on Back button
                back_rect = pygame.Rect(20, 20, 80, 40)
                if back_rect.collidepoint(mouse_x, mouse_y):
                    from game.scenes import LevelSelectScene
                    self.game.scenes.switch(LevelSelectScene(self.game))
                    return
                # Nếu đã thắng và không phải Level 8: kiểm tra nút Next Level
                if self.result == "WIN" and self.name != "Level 8":
                    sw, sh = self.game.screen.get_size()
                    next_rect = pygame.Rect(sw - 140, sh - 60, 120, 40)
                    if next_rect.collidepoint(mouse_x, mouse_y):
                        self._go_next_level()
                        return
        elif e.type == pygame.VIDEORESIZE:
            self._recompute_layout()
        elif e.type == pygame.MOUSEWHEEL:
            if e.y > 0:
                self.scale = min(self.max_scale, self.scale * 1.1)
            elif e.y < 0:
                self.scale = max(self.min_scale, self.scale / 1.1)
            self._recompute_layout()
        # Bắt phím chọn thuật toán (1 = BFS; số khác: tắt AI)
        self.ai.handle_event(e, self)
        # Cập nhật hover cho nút Next khi đã thắng
        if e.type == pygame.MOUSEMOTION:
            if self.result == "WIN" and self.name != "Level 8":
                mx, my = e.pos
                sw, sh = self.game.screen.get_size()
                next_rect = pygame.Rect(sw - 140, sh - 60, 120, 40)
                self._hover_next = next_rect.collidepoint(mx, my)

    def update(self, dt):
        # Nếu đã thắng: dừng thời gian và không xử lý di chuyển, chờ người chơi chọn
        if self.result:
            return

        self.time_elapsed += dt
        keys = pygame.key.get_pressed()
        self.cool -= dt
        
        if self.cool <= 0:
            dx = dy = 0
            # Nếu AI đang hoạt động thì lấy bước kế tiếp từ AI
            # Nếu đang trình diễn quá trình tìm kiếm, tick và không di chuyển
            if getattr(self.ai, 'showing_trace', False):
                self.ai.tick_trace()
                step = None
            else:
                step = self.ai.get_next_step()
            if step is not None:
                dx, dy = step
            else:
                # Người chơi điều khiển
                if keys[pygame.K_LEFT]:
                    dx = -1
                elif keys[pygame.K_RIGHT]:
                    dx = 1
                elif keys[pygame.K_UP]:
                    dy = -1
                elif keys[pygame.K_DOWN]:
                    dy = 1
            
            if dx or dy:
                # Update direction based on movement
                if dx < 0:
                    self.player.direction = "left"
                elif dx > 0:
                    self.player.direction = "right"
                elif dy < 0:
                    self.player.direction = "up"
                elif dy > 0:
                    self.player.direction = "down"
                
                nx, ny = self.player.gx + dx, self.player.gy + dy
                if not self.grid.is_blocked(nx, ny):
                    self.player.gx, self.player.gy = nx, ny
                    self.steps += 1
                    self._on_step()
                self.cool = 110

    def _on_step(self):
        """Xử lý khi player di chuyển"""
        # Thu thập ngôi sao
        if self.star_collector.collect_star_at(self.player.gx, self.player.gy):
            self.score += 10
        
        # Kiểm tra điều kiện thắng
        player_pos = (self.player.gx, self.player.gy)
        if player_pos == self.goal and self.star_collector.is_complete():
            self._finish()

    def reset_game_state(self):
        """Reset game về trạng thái ban đầu"""
        # Reset player về vị trí ban đầu
        start_pos, _ = self.grid.find_start_goal()
        self.player.gx, self.player.gy = start_pos
        self.player.direction = "down"  # Reset hướng về mặc định
        
        # Reset star collector về trạng thái ban đầu
        stars = self.grid.find_stars()
        self.star_collector = StarCollector(stars)
        
        # Reset game state
        self.score = 0
        self.steps = 0
        self.time_elapsed = 0
        self.cool = 0
        self.result = None
        self.timer = 0
        
        # Reset AI controller
        self.ai.reset()
        self.nodes_expanded_display = 0

    def _finish(self):
        """Kết thúc level"""
        self.result = "WIN"
        # Với Level 8, chuyển sang EndingScene ngay lập tức
        if self.name == "Level 8":
            from game.scenes import EndingScene
            self.game.scenes.switch(EndingScene(self.game))
            # Vẫn ghi lại record trước khi chuyển cảnh
        else:
            # Không auto quay về; hiển thị nút Next Level
            self.timer = 0
        
        # Ghi lại record
        rec = PlayRecord(
            ts=time.time(),
            level_name=self.name,
            result="WIN",
            score=self.score,
            time_elapsed_sec=int(self.time_elapsed // 1000),
            stars_collected=self.star_collector.stars_collected,
            stars_total=self.star_collector.stars_total,
            steps=self.steps,
            solver=(self.ai.active if self.ai.active else "HUMAN"),
            nodes_expanded=self.ai.nodes_expanded
        )
        self.game.stats.add(rec)
        # Lưu để hiển thị trên HUD sau khi hoàn tất thực thi lời giải
        self.nodes_expanded_display = self.ai.nodes_expanded

    def _draw_walls(self, screen):
        """Vẽ tường bằng hình ảnh tuong.png"""
        for y in range(self.grid.H):
            for x in range(self.grid.W):
                if self.grid.get_cell(x, y) == "1":  # Nếu là tường
                    cell_x = self.offset_x + x * self.tile
                    cell_y = self.offset_y + y * self.tile
                    # Lấy chỉ số texture đã gán sẵn cho ô tường này
                    idx = self.wall_variant_idx[y][x]
                    img = self.img_walls[idx]
                    screen.blit(img, (cell_x, cell_y))

    def _build_wall_variant_map(self):
        """Gán ngẫu nhiên 1 trong 4 texture tường cho mỗi ô tường.
        Dùng công thức băm theo (x,y) để kết quả ổn định trong suốt ván chơi.
        """
        self.wall_variant_idx = [[0 for _ in range(self.grid.W)] for _ in range(self.grid.H)]
        for y in range(self.grid.H):
            for x in range(self.grid.W):
                if self.grid.get_cell(x, y) == "1":
                    # Hash-based deterministic pseudo-random in range [0, 3]
                    h = (x * 73856093) ^ (y * 19349663)
                    self.wall_variant_idx[y][x] = h % 4

    def draw(self, screen):
        screen.fill(COLOR_BG)
        # Draw background image under the 80px header so gameplay elements appear on top
        if getattr(self, 'img_bg', None):
            screen.blit(self.img_bg, (0, 80))
        
        # Vẽ nền cho tất cả các ô (đường đi)
        for y in range(self.grid.H):
            for x in range(self.grid.W):
                if self.grid.get_cell(x, y) != "1":  # Chỉ vẽ nền cho ô không phải tường
                    pygame.draw.rect(screen, COLOR_PATH, (
                        self.offset_x + x * self.tile,
                        self.offset_y + y * self.tile,
                        self.tile, self.tile
                    ))
        
        # Vẽ tường bằng hình ảnh
        self._draw_walls(screen)
        
        # Vẽ overlay trực quan hóa quá trình tìm kiếm nếu đang hiển thị
        if getattr(self.ai, 'showing_trace', False):
            visited, cur = self.ai.get_trace_progress()
            # Các ô đã mở rộng: CYAN tươi, alpha trung bình để nổi bật
            for (vx, vy) in visited:
                if self.grid.get_cell(vx, vy) == '1':
                    continue
                rect = pygame.Rect(
                    self.offset_x + vx * self.tile,
                    self.offset_y + vy * self.tile,
                    self.tile, self.tile
                )
                s = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
                s.fill((0, 200, 255, 110))  # cyan, rõ hơn
                screen.blit(s, rect.topleft)
            # Ô hiện tại: TEAL đậm hơn + viền trắng để nhấn mạnh
            if cur is not None:
                cx, cy = cur
                if self.grid.get_cell(cx, cy) != '1':
                    rect = pygame.Rect(
                        self.offset_x + cx * self.tile,
                        self.offset_y + cy * self.tile,
                        self.tile, self.tile
                    )
                    s = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
                    s.fill((0, 255, 200, 160))  # teal đậm
                    screen.blit(s, rect.topleft)
                    # Viền trắng 2px để cực kỳ nổi bật trên mọi nền
                    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        # Vẽ overlay quá trình thực thi lời giải (sau khi trace xong và đang phát moves)
        if self.ai.active and not getattr(self.ai, 'showing_trace', False):
            visited_nodes, remaining_nodes = self.ai.get_solution_progress()
            # visited: XANH LÁ sáng, alpha lớn để dễ thấy
            if visited_nodes:
                s_visited = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
                s_visited.fill((0, 255, 0, 130))
                for (vx, vy) in visited_nodes:
                    if self.grid.get_cell(vx, vy) == '1':
                        continue
                    screen.blit(
                        s_visited,
                        (
                            self.offset_x + vx * self.tile,
                            self.offset_y + vy * self.tile,
                        ),
                    )
            # remaining: TÍM/MAGENTA để phân biệt rõ với visited và trace
            if remaining_nodes:
                s_remain = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
                s_remain.fill((200, 80, 255, 110))
                for (rx, ry) in remaining_nodes:
                    if self.grid.get_cell(rx, ry) == '1':
                        continue
                    screen.blit(
                        s_remain,
                        (
                            self.offset_x + rx * self.tile,
                            self.offset_y + ry * self.tile,
                        ),
                    )

        # Vẽ cà rốt bằng ảnh
        for (x, y) in self.star_collector.get_remaining_stars():
            cx = self.offset_x + x * self.tile + self.tile // 2
            cy = self.offset_y + y * self.tile + self.tile // 2
            screen.blit(self.img_carrot, (cx - self.carrot_half, cy - self.carrot_half))
        
        # Vẽ goal
        gx, gy = self.goal
        is_open = self.star_collector.is_complete()
        
        # Check if this is the final map (level 8)
        if self.name == "Level 8":
            cx = self.offset_x + gx * self.tile + self.tile // 2
            cy = self.offset_y + gy * self.tile + self.tile // 2
            # Center the chang e sprite
            sprite_rect = self.img_chang_e.get_rect(center=(cx, cy))
            screen.blit(self.img_chang_e, sprite_rect)
        else:
            # For other maps, show door as usual
            img = self.img_door_open if is_open else self.img_door_closed
            pad = self.door_pad
            screen.blit(img, (
                self.offset_x + gx * self.tile + pad,
                self.offset_y + gy * self.tile + pad
            ))
        
        # Vẽ player (bunny sprite)
        px = self.offset_x + self.player.gx * self.tile + self.tile // 2
        py = self.offset_y + self.player.gy * self.tile + self.tile // 2
        
        # Select appropriate bunny image based on direction
        direction = self.player.direction
        if direction == "up":
            bunny_img = self.img_bunny_up
        elif direction == "down":
            bunny_img = self.img_bunny_down
        elif direction == "left":
            bunny_img = self.img_bunny_left
        elif direction == "right":
            bunny_img = self.img_bunny_right
        else:
            bunny_img = self.img_bunny_down  # Default fallback
        
        # Center the sprite
        sprite_rect = bunny_img.get_rect(center=(px, py))
        screen.blit(bunny_img, sprite_rect)
        
        # Vẽ HUD
        self.hud.draw_game_hud(
            screen, self.name, self.time_elapsed, self.score,
            self.star_collector.stars_collected, self.star_collector.stars_total,
            self.steps, (self.nodes_expanded_display if self.result == "WIN" else None)
        )
        
        # Vẽ kết quả
        self.hud.draw_result(screen, self.result)

        # Nếu đã thắng và không phải Level 8: vẽ nút Next Level ở góc dưới bên phải
        if self.result == "WIN" and self.name != "Level 8":
            sw, sh = screen.get_size()
            next_rect = pygame.Rect(sw - 140, sh - 60, 120, 40)
            btn_color = (100, 200, 100) if not self._hover_next else (120, 220, 120)
            pygame.draw.rect(screen, btn_color, next_rect, border_radius=8)
            # Viền nhấn khi hover
            if self._hover_next:
                pygame.draw.rect(screen, (150, 250, 150), next_rect, 2, border_radius=8)
            label = self.font_button.render("Next Level", True, (255, 255, 255))
            label_rect = label.get_rect(center=next_rect.center)
            screen.blit(label, label_rect)

        # Hiển thị trạng thái AI (phía dưới header level, bên phải)
        # Luôn hiển thị tên thuật toán đã chọn gần đây (nếu có)
        if getattr(self.ai, 'display_active', None):
            label = f"AI: {self.ai.display_active}"
            surf = self.font_ai.render(label, True, (255, 255, 255))
            sw, sh = screen.get_size()
            rect = surf.get_rect()
            # Đặt ở phía dưới header (80px) và bên phải
            rect.top = 90  # Dưới header 80px + 10px margin
            rect.right = sw - 20
            # nền mờ để dễ đọc
            bg_rect = rect.inflate(12, 8)
            pygame.draw.rect(screen, (0, 0, 0, 0), bg_rect)  # opaque dark bg
            screen.blit(surf, rect)

    def _go_next_level(self):
        """Chuyển sang level kế tiếp nếu có (không áp dụng cho Level 8)."""
        try:
            # Parse số level từ self.name dạng "Level N"
            parts = self.name.strip().split()
            cur_idx = int(parts[-1])  # N hiện tại (1-based)
        except Exception:
            return
        next_idx = cur_idx + 1
        # Không áp dụng cho Level 8
        if next_idx > 8:
            return
        from core.assets import scan_levels
        levels = scan_levels("data/levels")
        # Index trong danh sách là 0-based, file được scan theo thứ tự
        if 1 <= next_idx <= len(levels):
            _, next_rows = levels[next_idx - 1]
            from game.level import LevelScene
            self.game.scenes.switch(LevelScene(self.game, f"Level {next_idx}", next_rows))

