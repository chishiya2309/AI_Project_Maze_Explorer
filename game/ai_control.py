import pygame
from typing import List, Optional, Tuple
from algorithms.BFS import bfs_collect_all_stars


class AIController:
    def __init__(self):
        self.active: Optional[str] = None  # "BFS" | others in tương lai
        self.moves: List[str] = []
        self.move_index: int = 0

    def reset(self):
        self.active = None
        self.moves = []
        self.move_index = 0

    def _build_rows_from_scene(self, level_scene) -> List[str]:
        # Tạo lưới ký tự từ scene hiện tại: sử dụng tường từ grid, sao theo remaining, S/G theo vị trí hiện tại
        W, H = level_scene.grid.W, level_scene.grid.H
        chars = [["0" for _ in range(W)] for _ in range(H)]

        # Walls
        for y in range(H):
            for x in range(W):
                if level_scene.grid.get_cell(x, y) == "1":
                    chars[y][x] = "1"

        # Stars còn lại
        for (sx, sy) in level_scene.star_collector.get_remaining_stars():
            chars[sy][sx] = "*"

        # Goal
        gx, gy = level_scene.goal
        chars[gy][gx] = "G"

        # Start tại vị trí player hiện tại
        px, py = level_scene.player.gx, level_scene.player.gy
        chars[py][px] = "S"

        return ["".join(row) for row in chars]

    def _compute_bfs(self, level_scene):
        rows = self._build_rows_from_scene(level_scene)
        res = bfs_collect_all_stars(rows)
        if not res.get("found"):
            self.reset()
            return
        # moves là danh sách 'U','D','L','R'
        self.moves = res.get("moves", [])
        self.move_index = 0

    def handle_event(self, e, level_scene):
        if e.type != pygame.KEYDOWN:
            return
        # Phím số 1: chạy BFS; các số khác: placeholder
        if e.key == pygame.K_1:
            self.active = "BFS"
            self._compute_bfs(level_scene)
        elif e.key in (pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0):
            # Chưa có, tắt AI để người chơi điều khiển
            self.reset()

    def get_next_step(self) -> Optional[Tuple[int, int]]:
        """Trả về (dx, dy) bước tiếp theo theo AI, hoặc None nếu không có/đã xong."""
        if self.active is None:
            return None
        if self.move_index >= len(self.moves):
            # Hết đường đi => tắt AI
            self.reset()
            return None
        move = self.moves[self.move_index]
        self.move_index += 1
        if move == "U":
            return (0, -1)
        if move == "D":
            return (0, 1)
        if move == "L":
            return (-1, 0)
        if move == "R":
            return (1, 0)
        return None


