import pygame

class Maze:
    def __init__(self, level_data, tile_images, cell_size):
        self.width = len(level_data[0])
        self.height = len(level_data)
        self.data = [row[:] for row in level_data]
        self.tile_images = tile_images
        self.cell_size = cell_size
        self.start_x, self.start_y = self._find_start()
        self.data[self.start_y][self.start_x] = 0

    def _find_start(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.data[y][x] == 2:
                    return x, y
        return 0, 0

    def is_wall_or_obstacle(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x] in (1, 4)
        return True

    def collect_pellet(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height and self.data[y][x] == 3:
            self.data[y][x] = 0

    def has_pellets(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.data[y][x] == 3:
                    return True
        return False

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.data[y][x]
                if tile_type in self.tile_images:
                    image = pygame.transform.scale(self.tile_images[tile_type], (self.cell_size, self.cell_size))
                    screen.blit(image, (x * self.cell_size, y * self.cell_size))
                else:
                    color = (128, 128, 128) if tile_type == 1 else (255, 255, 255)
                    pygame.draw.rect(screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))