import os
from typing import List
import pygame

# ================== LEVEL LOADER ==================
def read_level_txt(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        # Xóa khoảng trắng ở cuối để tránh tạo thêm cột ngoài ý muốn do các dấu cách.
        rows = [line.rstrip().rstrip("\n\r") for line in f if line.strip()]
    # Tính toán lại chiều rộng dựa trên các hàng đã xóa khoảng trắng.
    w = max(len(r) for r in rows) if rows else 0
    rows = [r.ljust(w, "1") for r in rows]
    return rows

def scan_levels(directory: str):
    if not os.path.isdir(directory): 
        return []
    out = []
    for name in sorted(os.listdir(directory)):
        if name.endswith(".txt"):
            out.append((name, read_level_txt(os.path.join(directory, name))))
    return out

# ================== IMAGE LOADER ==================
_image_cache = {}

def load_image(name: str) -> pygame.Surface:
    """Tải ảnh từ thư mục data/images với cơ chế lưu tạm (caching)."""
    key = name.lower()
    if key in _image_cache:
        return _image_cache[key]
    base_dir = os.path.join("data", "images")
    path = os.path.join(base_dir, name)
    surf = pygame.image.load(path).convert_alpha()
    _image_cache[key] = surf
    return surf
