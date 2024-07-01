import pygame
import random
import numpy as np


pygame.init()


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)


BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT


SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, BLUE, ORANGE, GREEN, RED]

class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.choice(SHAPES)
        self.color = SHAPE_COLORS[SHAPES.index(self.shape)]
        self.rotation = 0

    def rotate(self, grid):
        rotated_shape = self.rotate_shape(self.shape)
        if not self.check_collision(grid, 0, 0, rotated_shape):
            self.shape = rotated_shape
        elif not self.check_collision(grid, 1, 0, rotated_shape):
            self.x += 1
            self.shape = rotated_shape
        elif not self.check_collision(grid, -1, 0, rotated_shape):
            self.x -= 1
            self.shape = rotated_shape

    def rotate_shape(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def check_collision(self, grid, dx=0, dy=0, shape=None):
        if shape is None:
            shape = self.shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = self.x + j + dx
                    new_y = self.y + i + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and grid[new_y][new_x] != BLACK)):
                        return True
        return False

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.ai_mode = False
        self.game_count = 0
        self.total_score = 0

    def new_piece(self):
        return Shape(GRID_WIDTH // 2 - 1, 0)

    def add_to_grid(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[piece.y + i][piece.x + j] = piece.color

    def clear_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT - 1, -1, -1):
            if all(cell != BLACK for cell in self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        return lines_cleared




    pygame.quit()