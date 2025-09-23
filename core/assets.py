# maze_explorer/core/assets.py
import os
from typing import List
import pygame

# ================== LEVEL LOADER ==================
def read_level_txt(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        # Trim trailing whitespace to avoid unintended extra columns from spaces
        rows = [line.rstrip().rstrip("\n\r") for line in f if line.strip()]
    # Recompute width based on trimmed rows
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
    """Load image from data/images with caching."""
    key = name.lower()
    if key in _image_cache:
        return _image_cache[key]
    base_dir = os.path.join("data", "images")
    path = os.path.join(base_dir, name)
    surf = pygame.image.load(path).convert_alpha()
    _image_cache[key] = surf
    return surf
