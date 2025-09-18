# maze_explorer/game/collectibles.py
from typing import Set, Tuple

class StarCollector:
    def __init__(self, stars: Set[Tuple[int, int]]):
        self.stars = stars.copy()
        self.stars_total = len(stars)
        self.stars_collected = 0
    
    def collect_star_at(self, x: int, y: int) -> bool:
        """Thu thập ngôi sao tại vị trí (x,y). Trả về True nếu có ngôi sao được thu thập"""
        pos = (x, y)
        if pos in self.stars:
            self.stars.remove(pos)
            self.stars_collected += 1
            return True
        return False
    
    def is_complete(self) -> bool:
        """Kiểm tra xem đã thu thập hết ngôi sao chưa"""
        return self.stars_collected == self.stars_total
    
    def get_remaining_stars(self) -> Set[Tuple[int, int]]:
        """Lấy tập hợp các ngôi sao còn lại"""
        return self.stars.copy()
