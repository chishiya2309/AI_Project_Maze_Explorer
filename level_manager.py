class LevelManager:
    def __init__(self, levels_dir):
        self.levels_dir = levels_dir

    def load_level(self, level_num):
        filename = f"{self.levels_dir}level{level_num}.txt"
        try:
            with open(filename, 'r') as f:
                level_data = []
                for line in f:
                    row = [int(cell) for cell in line.strip().split()]
                    level_data.append(row)
                return level_data
        except FileNotFoundError:
            print(f"Level {level_num} not found! Using default.")
            if level_num == 1:
                return [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 3, 1, 0, 1, 1, 1, 0, 1],
                    [1, 0, 1, 1, 0, 0, 0, 1, 0, 1],
                    [1, 0, 0, 0, 0, 1, 0, 0, 4, 1],
                    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
                    [1, 0, 0, 1, 0, 0, 0, 0, 3, 1],
                    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                ]
            elif level_num == 2:
                return [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 2, 0, 1, 0, 0, 1, 0, 0, 1],
                    [1, 0, 3, 1, 3, 1, 1, 4, 0, 1],
                    [1, 1, 0, 0, 0, 1, 0, 0, 3, 1],
                    [1, 0, 1, 4, 1, 1, 1, 1, 0, 1],
                    [1, 3, 0, 0, 0, 0, 0, 1, 3, 1],
                    [1, 1, 1, 1, 4, 1, 0, 1, 0, 1],
                    [1, 0, 3, 0, 0, 1, 3, 0, 0, 1],
                    [1, 0, 1, 1, 1, 1, 0, 4, 3, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                ]
            elif level_num == 3:
                return [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 3, 1, 3, 1, 3, 1, 2, 1],
                    [1, 0, 1, 4, 0, 0, 0, 1, 0, 1],
                    [1, 3, 0, 1, 3, 1, 3, 0, 3, 1],
                    [1, 1, 1, 0, 1, 4, 1, 1, 0, 1],
                    [1, 0, 3, 0, 0, 0, 0, 3, 0, 1],
                    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                    [1, 3, 0, 0, 3, 0, 3, 0, 3, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                ]
            else:
                return [[1]*10 for _ in range(10)]