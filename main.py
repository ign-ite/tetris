import pygame
import random


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
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH+6)
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
        kick_x = 0
        if not self.check_collision(grid, kick_x, 0, rotated_shape):
            self.shape = rotated_shape
        elif not self.check_collision(grid, 1, 0, rotated_shape):
            self.shape = rotated_shape
            self.x += 1
        elif not self.check_collision(grid, -1, 0, rotated_shape):
            self.shape = rotated_shape
            self.x -= 1
        elif not self.check_collision(grid, 2, 0, rotated_shape):
            self.shape = rotated_shape
            self.x += 2
        elif not self.check_collision(grid, -2, 0, rotated_shape):
            self.shape = rotated_shape
            self.x -= 2

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

    def new_piece(self):
        return Shape(GRID_WIDTH // 2 - 1, 0)

    def valid_move(self, piece, x, y):
        return not piece.check_collision(self.grid, x - piece.x, y - piece.y)

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

    def draw_grid(self):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[i][j],
                                 (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_piece(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                     ((piece.x + j) * BLOCK_SIZE, (piece.y + i) * BLOCK_SIZE,
                                      BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE +4, 10))

    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE // 2 - 50, GRID_HEIGHT * BLOCK_SIZE // 2))

    def run(self):
        fall_time = 0
        fall_speed = 0.5
        while not self.game_over:
            fall_time += self.clock.get_rawtime()
            self.clock.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece.x - 1, self.current_piece.y):
                            self.current_piece.x -= 1
                    if event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece.x + 1, self.current_piece.y):
                            self.current_piece.x += 1
                    if event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                            self.current_piece.y += 1
                    if event.key == pygame.K_UP:
                        self.current_piece.rotate(self.grid)

            if fall_time / 1000 > fall_speed:
                if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                    self.current_piece.y += 1
                else:
                    self.add_to_grid(self.current_piece)
                    lines_cleared = self.clear_lines()
                    self.score += lines_cleared * 100
                    self.current_piece = self.new_piece()
                    if self.current_piece.check_collision(self.grid):
                        self.game_over = True
                fall_time = 0

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_score()
            if self.game_over:
                self.draw_game_over()
            pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()
