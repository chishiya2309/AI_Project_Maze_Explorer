import pygame
from typing import List, Optional, Tuple
from algorithms.BFS import bfs_collect_all_stars, bfs_collect_all_stars_with_trace


class AIController:
    def __init__(self):
        self.active: Optional[str] = None  # "BFS" | others in tương lai
        self.moves: List[str] = []
        self.move_index: int = 0
        # Tracing
        self.trace_positions: List[Tuple[int, int]] = []
        self.trace_index: int = 0
        self.showing_trace: bool = False
        # Solution execution visualization
        self.solution_path: List[Tuple[int, int]] = []  # gồm cả điểm bắt đầu

    def reset(self):
        self.active = None
        self.moves = []
        self.move_index = 0
        self.trace_positions = []
        self.trace_index = 0
        self.showing_trace = False
        self.solution_path = []

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
        res = bfs_collect_all_stars_with_trace(rows)
        if not res.get("found"):
            self.reset()
            return
        # moves là danh sách 'U','D','L','R'
        self.moves = res.get("moves", [])
        self.move_index = 0
        # Tracing
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        # Lưu path để hiển thị quá trình thực thi lời giải
        self.solution_path = res.get("path", [])

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
        # Nếu đang hiển thị quá trình duyệt, trả None để game update không di chuyển player
        if self.showing_trace:
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

    def tick_trace(self):
        """Tiến một frame hiển thị duyệt BFS. Khi xong sẽ chuyển sang phát các moves."""
        if not self.showing_trace:
            return
        self.trace_index += 1
        if self.trace_index >= len(self.trace_positions):
            self.showing_trace = False

    def get_trace_progress(self) -> Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Trả về danh sách ô đã duyệt và ô đang focus.

        - visited_list: các ô đã duyệt đến chỉ số trace_index
        - current: ô hiện tại (nếu còn), else None
        """
        if not self.showing_trace:
            return [], None
        idx = max(0, min(self.trace_index, len(self.trace_positions)))
        visited_list = self.trace_positions[:idx]
        cur = None
        if idx < len(self.trace_positions):
            cur = self.trace_positions[idx]
        return visited_list, cur

    def get_solution_progress(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Trả về (visited_nodes, remaining_nodes) theo tiến độ move_index.

        - visited_nodes: các ô đã đi qua (bao gồm start đến vị trí hiện tại)
        - remaining_nodes: các ô còn lại từ vị trí hiện tại tới đích
        """
        if not self.solution_path:
            return [], []
        # path có độ dài = len(moves) + 1
        k = max(0, min(self.move_index, max(0, len(self.solution_path) - 1)))
        # Tại thời điểm trước khi thực hiện move thứ k+1, đang đứng ở node index k
        visited = self.solution_path[: k + 1]
        remaining = self.solution_path[k + 1 :]
        return visited, remaining


