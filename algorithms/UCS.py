from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from heapq import heappush, heappop

Position = Tuple[int, int]
State = Tuple[int, int, int]  # (x, y, collected_mask)

def _parse_level(rows: List[str]) -> Tuple[Position, Position, List[Position], int, int]:
    """Trích xuất S, G, danh sách sao từ ma trận ký tự."""
    height = len(rows)
    width = len(rows[0]) if height > 0 else 0
    start: Optional[Position] = None
    goal: Optional[Position] = None
    stars: List[Position] = []

    for y in range(height):
        for x in range(width):
            ch = rows[y][x]
            if ch == "S":
                start = (x, y)
            elif ch == "G":
                goal = (x, y)
            elif ch == "*":
                stars.append((x, y))

    if start is None or goal is None:
        raise ValueError("Level không hợp lệ: thiếu S hoặc G")

    return start, goal, stars, width, height

def _is_blocked(rows: List[str], x: int, y: int, width: int, height: int) -> bool:
    if x < 0 or y < 0 or x >= width or y >= height:
        return True
    return rows[y][x] == "1"

def _reconstruct_path(
    parents: Dict[State, Tuple[Optional[State], str]],
    end_state: State,
) -> Tuple[List[Position], List[str]]:
    """Lần ngược từ end_state để tạo path và moves (UDLR)."""
    path_rev: List[Position] = []
    moves_rev: List[str] = []
    cur: Optional[State] = end_state
    while cur is not None:
        (x, y, _) = cur
        path_rev.append((x, y))
        prev, move = parents[cur]
        if move:
            moves_rev.append(move)
        cur = prev

    path_rev.reverse()
    moves_rev.reverse()
    return path_rev, moves_rev

def ucs_collect_all_stars_with_trace(rows: List[str]) -> Dict[str, object]:
    """Tìm đường đi ngắn nhất bằng UCS: thu thập hết sao rồi tới cửa (G).

    - Input: rows (danh sách chuỗi ký tự của level)
    - Output: dict gồm:
        {
          "path": List[(x,y)],        # dãy ô đi qua từ S tới G
          "moves": List[str],          # 'U','D','L','R'
          "steps": int,                # số bước
          "stars_total": int,
          "found": bool,               # có tìm thấy hay không
          "expanded_order": List[(x,y)]  # thứ tự các ô được mở rộng
        }
    """
    start, goal, stars, width, height = _parse_level(rows)

    # Ánh xạ vị trí sao -> bit index
    star_index: Dict[Position, int] = {pos: i for i, pos in enumerate(stars)}
    all_mask = (1 << len(stars)) - 1

    start_mask = 0

    # Hàng đợi ưu tiên cho UCS (min-heap): (g_score, state)
    queue: List[Tuple[int, State]] = []
    parents: Dict[State, Tuple[Optional[State], str]] = {}
    g_scores: Dict[State, int] = {}  # Chi phí từ start đến state
    visited: Set[State] = set()
    expanded_order: List[Position] = []

    start_state: State = (start[0], start[1], start_mask)
    heappush(queue, (0, start_state))
    parents[start_state] = (None, "")
    g_scores[start_state] = 0
    visited.add(start_state)

    directions: List[Tuple[int, int, str]] = [
        (0, -1, "U"),
        (0, 1, "D"),
        (-1, 0, "L"),
        (1, 0, "R"),
    ]

    end_state: Optional[State] = None

    while queue:
        g_score, (x, y, mask) = heappop(queue)
        expanded_order.append((x, y))

        # Điều kiện thắng: đứng ở G và đã gom đủ sao
        if (x, y) == goal and mask == all_mask:
            end_state = (x, y, mask)
            break

        for dx, dy, move in directions:
            nx, ny = x + dx, y + dy
            if _is_blocked(rows, nx, ny, width, height):
                continue

            next_mask = mask
            pos = (nx, ny)
            if pos in star_index:
                next_mask = mask | (1 << star_index[pos])

            nxt: State = (nx, ny, next_mask)
            if nxt in visited:
                continue

            # Tính chi phí g (từ start đến nxt)
            tentative_g = g_scores[(x, y, mask)] + 1

            heappush(queue, (tentative_g, nxt))
            visited.add(nxt)
            parents[nxt] = ((x, y, mask), move)
            g_scores[nxt] = tentative_g

    if end_state is None:
        return {
            "path": [],
            "moves": [],
            "steps": 0,
            "stars_total": len(stars),
            "found": False,
            "expanded_order": expanded_order,
        }

    path, moves = _reconstruct_path(parents, end_state)
    return {
        "path": path,
        "moves": moves,
        "steps": len(moves),
        "stars_total": len(stars),
        "found": True,
        "expanded_order": expanded_order,
    }