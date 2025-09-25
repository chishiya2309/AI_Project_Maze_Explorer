from collections import deque
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple


Position = Tuple[int, int]
State = Tuple[int, int, int]  # (x, y, collected_mask)


def _parse_level(rows: List[str]) -> Tuple[Position, Position, List[Position], int, int]:
    """Trích xuất S, G, danh sách sao từ ma trận ký tự.

    Ký hiệu lưới:
    - "1": tường (không đi xuyên)
    - "S": vị trí bắt đầu
    - "G": cửa/đích
    - "*": ngôi sao

    Trả về: (start, goal, stars, width, height)
    """
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
    """Lần ngược từ end_state để tạo path (danh sách tọa độ) và moves (UDLR)."""
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


def bfs_collect_all_stars(rows: List[str]) -> Dict[str, object]:
    """Tìm đường đi ngắn nhất bằng BFS: ăn hết sao rồi tới cửa (G).

    - Input: rows (danh sách chuỗi ký tự của level)
    - Output: dict gồm:
        {
          "path": List[(x,y)],        # dãy ô đi qua từ S tới G
          "moves": List[str],          # 'U','D','L','R'
          "steps": int,                # số bước
          "stars_total": int,
          "found": bool                # có tìm thấy hay không
        }
    """
    start, goal, stars, width, height = _parse_level(rows)

    # Ánh xạ vị trí sao -> bit index
    star_index: Dict[Position, int] = {pos: i for i, pos in enumerate(stars)}
    all_mask = (1 << len(stars)) - 1

    # Nếu không có sao, chỉ cần đi tới G
    start_mask = 0

    # BFS trên không gian trạng thái (x, y, mask)
    queue: Deque[State] = deque()
    parents: Dict[State, Tuple[Optional[State], str]] = {}
    visited: Set[State] = set()

    start_state: State = (start[0], start[1], start_mask)
    queue.append(start_state)
    parents[start_state] = (None, "")
    visited.add(start_state)

    directions: List[Tuple[int, int, str]] = [
        (0, -1, "U"),
        (0, 1, "D"),
        (-1, 0, "L"),
        (1, 0, "R"),
    ]

    end_state: Optional[State] = None

    while queue:
        x, y, mask = queue.popleft()

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
            visited.add(nxt)
            parents[nxt] = ((x, y, mask), move)
            queue.append(nxt)

    if end_state is None:
        # Không tìm thấy đường thoả mãn
        return {
            "path": [],
            "moves": [],
            "steps": 0,
            "stars_total": len(stars),
            "found": False,
        }

    path, moves = _reconstruct_path(parents, end_state)
    # path bao gồm cả vị trí bắt đầu; steps là số cạnh (len(moves))
    return {
        "path": path,
        "moves": moves,
        "steps": len(moves),
        "stars_total": len(stars),
        "found": True,
    }


def bfs_collect_at_least_k_stars(rows: List[str], k: int = 3) -> Dict[str, object]:
    """Biến thể: yêu cầu ít nhất k sao trước khi tới G.

    Hữu ích nếu level có >3 sao nhưng chỉ cần 3 để mở cửa.
    Nếu k >= tổng sao thì tương đương bfs_collect_all_stars.
    """
    start, goal, stars, width, height = _parse_level(rows)

    star_index: Dict[Position, int] = {pos: i for i, pos in enumerate(stars)}
    total = len(stars)
    need = min(k, total)

    queue: Deque[State] = deque()
    parents: Dict[State, Tuple[Optional[State], str]] = {}
    visited: Set[State] = set()

    start_state: State = (start[0], start[1], 0)
    queue.append(start_state)
    parents[start_state] = (None, "")
    visited.add(start_state)

    directions: List[Tuple[int, int, str]] = [
        (0, -1, "U"),
        (0, 1, "D"),
        (-1, 0, "L"),
        (1, 0, "R"),
    ]

    end_state: Optional[State] = None

    while queue:
        x, y, mask = queue.popleft()

        # Kiểm tra số sao đã thu
        collected = mask.bit_count()
        if (x, y) == goal and collected >= need:
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
            visited.add(nxt)
            parents[nxt] = ((x, y, mask), move)
            queue.append(nxt)

    if end_state is None:
        return {
            "path": [],
            "moves": [],
            "steps": 0,
            "stars_total": total,
            "found": False,
        }

    path, moves = _reconstruct_path(parents, end_state)
    return {
        "path": path,
        "moves": moves,
        "steps": len(moves),
        "stars_total": total,
        "found": True,
    }


