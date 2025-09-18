# maze_explorer/game/grid.py
from typing import List, Tuple, Set

class Grid:
    def __init__(self, rows: List[str]):
        self.grid = [list(r) for r in rows]
        self.H = len(self.grid)
        self.W = len(self.grid[0])
    
    def find_start_goal(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Tìm vị trí start (S) và goal (G)"""
        s = g = None
        for y in range(self.H):
            for x in range(self.W):
                if self.grid[y][x] == "S": 
                    s = (x, y)
                if self.grid[y][x] == "G": 
                    g = (x, y)
        return s, g
    
    def find_stars(self) -> Set[Tuple[int, int]]:
        """Tìm tất cả vị trí các ngôi sao (*)"""
        return {(x, y) for y in range(self.H) for x in range(self.W) if self.grid[y][x] == "*"}
    
    def is_blocked(self, x: int, y: int) -> bool:
        """Kiểm tra xem vị trí (x,y) có bị chặn không"""
        return x < 0 or y < 0 or x >= self.W or y >= self.H or self.grid[y][x] == "1"
    
    def get_cell(self, x: int, y: int) -> str:
        """Lấy ký tự tại vị trí (x,y)"""
        if 0 <= x < self.W and 0 <= y < self.H:
            return self.grid[y][x]
        return "1"  # Trả về wall nếu ngoài biên
