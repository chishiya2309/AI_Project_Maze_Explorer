import pygame

SPEED = 10

class Player:
    def __init__(self, x, y, images, cell_size):
        self.pos_x = x * cell_size
        self.pos_y = y * cell_size
        self.grid_x = x
        self.grid_y = y
        self.images = images
        self.current_image = self.images['front']
        self.cell_size = cell_size
        self.velocity = (0, 0)

    def move(self, dx, dy, maze):
        if self.velocity == (0, 0):
            vx = dx * SPEED
            vy = dy * SPEED
            new_grid_x = self.grid_x + dx
            new_grid_y = self.grid_y + dy
            if not maze.is_wall_or_obstacle(new_grid_x, new_grid_y):
                self.velocity = (vx, vy)
                if dx == 1:
                    self.set_direction('right')
                elif dx == -1:
                    self.set_direction('left')
                elif dy == 1:
                    self.set_direction('front')
                elif dy == -1:
                    self.set_direction('behind')

    def set_direction(self, direction):
        if direction in self.images:
            self.current_image = self.images[direction]

    def update(self, maze):
        if self.velocity != (0, 0):
            vx, vy = self.velocity
            new_pos_x = self.pos_x + vx
            new_pos_y = self.pos_y + vy
            new_grid_x = int((new_pos_x + self.current_image.get_width() / 2) // self.cell_size)
            new_grid_y = int((new_pos_y + self.current_image.get_height() / 2) // self.cell_size)

            if maze.is_wall_or_obstacle(new_grid_x, new_grid_y):
                image_width = self.current_image.get_width()
                image_height = self.current_image.get_height()
                if vx > 0:
                    self.pos_x = (self.grid_x + 1) * self.cell_size - image_width
                elif vx < 0:
                    self.pos_x = self.grid_x * self.cell_size
                if vy > 0:
                    self.pos_y = (self.grid_y + 1) * self.cell_size - image_height
                elif vy < 0:
                    self.pos_y = self.grid_y * self.cell_size
                self.velocity = (0, 0)
            else:
                if new_grid_x != self.grid_x or new_grid_y != self.grid_y:
                    maze.collect_pellet(new_grid_x, new_grid_y)
                    self.grid_x = new_grid_x
                    self.grid_y = new_grid_y
                self.pos_x = new_pos_x
                self.pos_y = new_pos_y

    def draw(self, screen):
        draw_x = self.pos_x + (self.cell_size - self.current_image.get_width()) / 2
        draw_y = self.pos_y + (self.cell_size - self.current_image.get_height()) / 2
        screen.blit(self.current_image, (draw_x, draw_y))