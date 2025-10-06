import pygame
from typing import List, Optional, Tuple
from algorithms.BFS import bfs_collect_all_stars_with_trace
from algorithms.AStar import astar_collect_all_stars_with_trace
from algorithms.Greedy import greedy_collect_all_stars_with_trace
from algorithms.DFS import dfs_collect_all_stars_with_trace
from algorithms.UCS import ucs_collect_all_stars_with_trace

class AIController:
    def __init__(self):
        self.active: Optional[str] = None  # "BFS" | "AStar" | "Greedy" | "DFS" | "UCS" | others in tương lai
        self.display_active: Optional[str] = None  # luôn giữ tên thuật toán để hiển thị
        self.moves: List[str] = []
        self.move_index: int = 0
        # Tracing
        self.trace_positions: List[Tuple[int, int]] = []
        self.trace_index: int = 0
        self.showing_trace: bool = False
        # Solution execution visualization
        self.solution_path: List[Tuple[int, int]] = []  # gồm cả điểm bắt đầu
        # Thống kê thuật toán
        self.nodes_expanded: int = 0  # Số nút đã duyệt

    def reset(self):
        # Không xóa display_active để vẫn hiển thị tên thuật toán đã chọn
        self.active = None
        self.moves = []
        self.move_index = 0
        self.trace_positions = []
        self.trace_index = 0
        self.showing_trace = False
        self.solution_path = []
        self.nodes_expanded = 0

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
        self.moves = res.get("moves", [])
        self.move_index = 0
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        self.solution_path = res.get("path", [])
        self.nodes_expanded = res.get("nodes_expanded", 0)

    def _compute_astar(self, level_scene):
        rows = self._build_rows_from_scene(level_scene)
        res = astar_collect_all_stars_with_trace(rows)
        if not res.get("found"):
            self.reset()
            return
        self.moves = res.get("moves", [])
        self.move_index = 0
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        self.solution_path = res.get("path", [])
        self.nodes_expanded = res.get("nodes_expanded", 0)

    def _compute_greedy(self, level_scene):
        rows = self._build_rows_from_scene(level_scene)
        res = greedy_collect_all_stars_with_trace(rows)
        if not res.get("found"):
            self.reset()
            return
        self.moves = res.get("moves", [])
        self.move_index = 0
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        self.solution_path = res.get("path", [])
        self.nodes_expanded = res.get("nodes_expanded", 0)

    def _compute_dfs(self, level_scene):
        rows = self._build_rows_from_scene(level_scene)
        res = dfs_collect_all_stars_with_trace(rows)
        if not res.get("found"):
            self.reset()
            return
        self.moves = res.get("moves", [])
        self.move_index = 0
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        self.solution_path = res.get("path", [])
        self.nodes_expanded = res.get("nodes_expanded", 0)

    def _compute_ucs(self, level_scene):
        rows = self._build_rows_from_scene(level_scene)
        res = ucs_collect_all_stars_with_trace(rows)
        if not res.get("found"):
            self.reset()
            return
        self.moves = res.get("moves", [])
        self.move_index = 0
        self.trace_positions = res.get("expanded_order", [])
        self.trace_index = 0
        self.showing_trace = True
        self.solution_path = res.get("path", [])
        self.nodes_expanded = res.get("nodes_expanded", 0)

    def handle_event(self, e, level_scene):
        if e.type != pygame.KEYDOWN:
            return
        # Phím số 1: BFS; 2: DFS; 3: UCS; 4: Greedy; 5: A*
        if e.key == pygame.K_1:
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.active = "BFS"
            self.display_active = "BFS"
            self._compute_bfs(level_scene)
        elif e.key == pygame.K_2:
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.active = "DFS"
            self.display_active = "DFS"
            self._compute_dfs(level_scene)
        elif e.key == pygame.K_3:
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.active = "UCS"
            self.display_active = "UCS"
            self._compute_ucs(level_scene)
        elif e.key == pygame.K_4:
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.active = "Greedy"
            self.display_active = "Greedy"
            self._compute_greedy(level_scene)
        elif e.key == pygame.K_5:
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.active = "AStar"
            self.display_active = "AStar"
            self._compute_astar(level_scene)
        elif e.key in (pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0):
            # Chưa có, tắt AI để người chơi điều khiển
            level_scene.reset_game_state()  # Reset game về trạng thái ban đầu
            self.reset()
            self.display_active = None

    def get_next_step(self) -> Optional[Tuple[int, int]]:
        """Trả về (dx, dy) bước tiếp theo theo AI, hoặc None nếu không có/đã xong."""
        if self.active is None:
            return None
        if self.showing_trace:
            return None
        if self.move_index >= len(self.moves):
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
        """Tiến một frame hiển thị duyệt. Khi xong sẽ chuyển sang phát các moves."""
        if not self.showing_trace:
            return
        self.trace_index += 1
        if self.trace_index >= len(self.trace_positions):
            self.showing_trace = False

    def get_trace_progress(self) -> Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Trả về danh sách ô đã duyệt và ô đang focus."""
        if not self.showing_trace:
            return [], None
        idx = max(0, min(self.trace_index, len(self.trace_positions)))
        visited_list = self.trace_positions[:idx]
        cur = None
        if idx < len(self.trace_positions):
            cur = self.trace_positions[idx]
        return visited_list, cur

    def get_solution_progress(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Trả về (visited_nodes, remaining_nodes) theo tiến độ move_index."""
        if not self.solution_path:
            return [], []
        k = max(0, min(self.move_index, max(0, len(self.solution_path) - 1)))
        visited = self.solution_path[: k + 1]
        remaining = self.solution_path[k + 1 :]
        return visited, remaining