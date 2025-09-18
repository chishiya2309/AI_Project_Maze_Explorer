# maze_explorer/core/assets.py
import os
from typing import List

# ================== LEVEL LOADER ==================
def read_level_txt(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        rows = [line.rstrip("\n") for line in f if line.strip()]
    w = max(len(r) for r in rows)
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
