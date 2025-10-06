from collections import deque
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple
from heapq import heappush, heappop

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

def _bfs_distance(rows: List[str], start: Position, width: int, height: int) -> Dict[Position, int]:
    """Tính khoảng cách BFS từ start đến tất cả các ô trong lưới."""
    distances: Dict[Position, int] = {}
    queue = deque([(start, 0)])
    visited: Set[Position] = {start}
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    while queue:
        (x, y), dist = queue.popleft()
        distances[(x, y)] = dist
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and not _is_blocked(rows, nx, ny, width, height):
                visited.add((nx, ny))
                queue.append(((nx, ny), dist + 1))
    
    return distances

def _precompute_distances(rows: List[str], start: Position, goal: Position, stars: List[Position], width: int, height: int) -> Dict[Tuple[Position, Position], int]:
    """Tiền xử lý khoảng cách BFS giữa tất cả POI (S, G, stars)."""
    poi_list = [start, goal] + stars
    poi_to_index = {poi: i for i, poi in enumerate(poi_list)}
    distances: Dict[Tuple[Position, Position], int] = {}
    
    # Tính khoảng cách từ mỗi POI đến tất cả các ô
    poi_distances = {}
    for poi in poi_list:
        poi_distances[poi] = _bfs_distance(rows, poi, width, height)
    
    # Lưu khoảng cách giữa các POI
    for i, poi1 in enumerate(poi_list):
        for j, poi2 in enumerate(poi_list):
            if i != j:
                if poi2 in poi_distances[poi1]:
                    distances[(poi1, poi2)] = poi_distances[poi1][poi2]
                else:
                    # Nếu không thể đến được, dùng khoảng cách Manhattan làm upper bound
                    distances[(poi1, poi2)] = abs(poi1[0] - poi2[0]) + abs(poi1[1] - poi2[1])
    
    return distances

def _get_distance(distances: Dict[Tuple[Position, Position], int], pos1: Position, pos2: Position) -> int:
    """Lấy khoảng cách giữa hai vị trí từ ma trận đã tính sẵn."""
    if (pos1, pos2) in distances:
        return distances[(pos1, pos2)]
    elif (pos2, pos1) in distances:
        return distances[(pos2, pos1)]
    else:
        # Fallback: Manhattan distance
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def _compute_mst_weight(remaining_stars: List[Position], distances: Dict[Tuple[Position, Position], int]) -> int:
    """Tính trọng số MST của các sao còn lại bằng thuật toán Prim."""
    if not remaining_stars:
        return 0
    if len(remaining_stars) == 1:
        return 0
    
    # Sử dụng Prim's algorithm
    mst_weight = 0
    visited: Set[Position] = {remaining_stars[0]}
    remaining = set(remaining_stars[1:])
    
    while remaining:
        min_dist = float('inf')
        min_star = None
        
        for visited_star in visited:
            for remaining_star in remaining:
                dist = _get_distance(distances, visited_star, remaining_star)
                if dist < min_dist:
                    min_dist = dist
                    min_star = remaining_star
        
        if min_star is not None:
            mst_weight += min_dist
            visited.add(min_star)
            remaining.remove(min_star)
    
    return mst_weight

def _compute_heuristic_mst(current_pos: Position, remaining_stars: List[Position], goal: Position, distances: Dict[Tuple[Position, Position], int]) -> int:
    """Tính heuristic MST admissible: d(cur, R) + MST(R) + d(R, G)."""
    if not remaining_stars:
        return _get_distance(distances, current_pos, goal)
    
    # d(cur, R): khoảng cách ngắn nhất từ vị trí hiện tại đến một sao trong R
    min_dist_to_stars = min(_get_distance(distances, current_pos, star) for star in remaining_stars)
    
    # MST(R): trọng số cây khung nhỏ nhất của các sao còn lại
    mst_weight = _compute_mst_weight(remaining_stars, distances)
    
    # d(R, G): khoảng cách ngắn nhất từ một sao trong R đến goal
    min_dist_stars_to_goal = min(_get_distance(distances, star, goal) for star in remaining_stars)
    
    return min_dist_to_stars + mst_weight + min_dist_stars_to_goal

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

def astar_collect_all_stars_with_trace(rows: List[str]) -> Dict[str, object]:
    """Tìm đường đi ngắn nhất bằng A* với heuristic MST admissible.

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

    # Tiền xử lý khoảng cách BFS
    distances = _precompute_distances(rows, start, goal, stars, width, height)
    
    # Ánh xạ vị trí sao -> bit index
    star_index: Dict[Position, int] = {pos: i for i, pos in enumerate(stars)}
    all_mask = (1 << len(stars)) - 1

    # Nếu không có sao, chỉ cần đi tới G
    start_mask = 0

    # Hàng đợi ưu tiên cho A* (min-heap): (f_score, state)
    queue: List[Tuple[int, State]] = []
    parents: Dict[State, Tuple[Optional[State], str]] = {}
    g_scores: Dict[State, int] = {}  # Chi phí từ start đến state
    closed_set: Set[State] = set()  # Các state đã "đóng"
    expanded_order: List[Position] = []

    start_state: State = (start[0], start[1], start_mask)
    
    # Cache cho MST theo mask để tối ưu
    mst_cache: Dict[int, int] = {}
    
    def get_heuristic(state: State) -> int:
        """Tính heuristic MST cho state hiện tại."""
        x, y, mask = state
        current_pos = (x, y)
        
        # Lấy danh sách sao còn lại
        remaining_stars = [stars[i] for i in range(len(stars)) if not (mask & (1 << i))]
        
        # Kiểm tra cache MST
        cache_key = mask
        if cache_key not in mst_cache:
            mst_cache[cache_key] = _compute_mst_weight(remaining_stars, distances)
        
        return _compute_heuristic_mst(current_pos, remaining_stars, goal, distances)
    
    # Khởi tạo
    h_score = get_heuristic(start_state)
    heappush(queue, (h_score, start_state))
    parents[start_state] = (None, "")
    g_scores[start_state] = 0

    directions: List[Tuple[int, int, str]] = [
        (0, -1, "U"),
        (0, 1, "D"),
        (-1, 0, "L"),
        (1, 0, "R"),
    ]

    end_state: Optional[State] = None

    while queue:
        _, (x, y, mask) = heappop(queue)
        
        # Bỏ qua nếu đã xử lý state này
        if (x, y, mask) in closed_set:
            continue
            
        closed_set.add((x, y, mask))
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
            
            # Bỏ qua nếu đã đóng
            if nxt in closed_set:
                continue

            # Tính chi phí g (từ start đến nxt)
            tentative_g = g_scores[(x, y, mask)] + 1

            # Chỉ cập nhật nếu tìm được đường tốt hơn
            if tentative_g < g_scores.get(nxt, float('inf')):
                g_scores[nxt] = tentative_g
                parents[nxt] = ((x, y, mask), move)
                
                # Tính f_score với heuristic MST
                h_score = get_heuristic(nxt)
                f_score = tentative_g + h_score
                
                heappush(queue, (f_score, nxt))

    if end_state is None:
        return {
            "path": [],
            "moves": [],
            "steps": 0,
            "stars_total": len(stars),
            "found": False,
            "expanded_order": expanded_order,
            "nodes_expanded": len(expanded_order),
        }

    path, moves = _reconstruct_path(parents, end_state)
    return {
        "path": path,
        "moves": moves,
        "steps": len(moves),
        "stars_total": len(stars),
        "found": True,
        "expanded_order": expanded_order,
        "nodes_expanded": len(expanded_order),
    }