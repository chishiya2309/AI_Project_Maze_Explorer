import pygame
from typing import List, Optional, Tuple
from algorithms.BFS import bfs_collect_all_stars


class AIController:
    def __init__(self):
        self.active: Optional[str] = None  # "BFS" | others in tương lai
        self.moves: List[str] = []
        self.move_index: int = 0
        # Progressive visited visualization state
        self._visited_order: List[Tuple[int, int]] = []
        self._reveal_index: int = 0
        self._reveal_acc_ms: int = 0
        self._reveal_interval_ms: int = 30  # tốc độ loang (ms mỗi ô)

    def reset(self):
        self.active = None
        self.moves = []
        self.move_index = 0
        self._visited_order = []
        self._reveal_index = 0
        self._reveal_acc_ms = 0

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
        # compute visited order separately for progressive flood visualization
        self._visited_order = self._compute_bfs_visited(rows)
        self._reveal_index = 0
        self._reveal_acc_ms = 0

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

    def update(self, dt_ms: int):
        """Cập nhật tiến độ loang theo thời gian (ms)."""
        if self.active is None or not self._visited_order:
            return
        self._reveal_acc_ms += dt_ms
        while self._reveal_acc_ms >= self._reveal_interval_ms and self._reveal_index < len(self._visited_order):
            self._reveal_acc_ms -= self._reveal_interval_ms
            self._reveal_index += 1

    def get_revealed_visited(self) -> List[Tuple[int, int]]:
        """Các ô đã được hé lộ (phục vụ vẽ overlay)."""
        if not self._visited_order:
            return []
        upto = max(0, min(self._reveal_index, len(self._visited_order)))
        return self._visited_order[:upto]

    def _compute_bfs_visited(self, rows: List[str]) -> List[Tuple[int, int]]:
        """Tính thứ tự ô được duyệt (pop từ queue) của BFS với không gian trạng thái gồm sao.
        Không trả về đường đi; chỉ trả về visited order để vẽ loang.
        """
        H = len(rows)
        W = len(rows[0]) if H > 0 else 0
        start = None
        goal = None
        stars: List[Tuple[int, int]] = []
        for y in range(H):
            for x in range(W):
                ch = rows[y][x]
                if ch == "S":
                    start = (x, y)
                elif ch == "G":
                    goal = (x, y)
                elif ch == "*":
                    stars.append((x, y))
        if start is None or goal is None:
            return []

        star_index = {pos: i for i, pos in enumerate(stars)}
        all_mask = (1 << len(stars)) - 1

        def blocked(x: int, y: int) -> bool:
            return x < 0 or y < 0 or x >= W or y >= H or rows[y][x] == "1"

        from collections import deque
        State = Tuple[int, int, int]
        q = deque()
        visited = set()
        order: List[Tuple[int, int]] = []
        s: State = (start[0], start[1], 0)
        q.append(s)
        visited.add(s)
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while q:
            x, y, mask = q.popleft()
            order.append((x, y))
            if (x, y) == goal and mask == all_mask:
                # có thể dừng sớm tại đích khi đủ sao
                break
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if blocked(nx, ny):
                    continue
                nmask = mask
                if (nx, ny) in star_index:
                    nmask |= (1 << star_index[(nx, ny)])
                st: State = (nx, ny, nmask)
                if st in visited:
                    continue
                visited.add(st)
                q.append(st)
        return order


