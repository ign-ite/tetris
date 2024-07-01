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
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))

    def draw_ai_stats(self):
        game_count_text = self.font.render(f"Games: {self.game_count}", True, WHITE)
        avg_score_text = self.font.render(f"Avg Score: {self.total_score // max(1, self.game_count)}", True, WHITE)
        self.screen.blit(game_count_text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        self.screen.blit(avg_score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 90))

    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE // 2 - 50, GRID_HEIGHT * BLOCK_SIZE // 2))

    def run_ai(self, ai):
        self.ai_mode = True
        while True:
            self.__init__()
            self.ai_mode = True
            while not self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                action = ai.play(self)
                rotation, x = action
                self.current_piece.x = x
                for _ in range(rotation):
                    self.current_piece.rotate(self.grid)

                while not self.current_piece.check_collision(self.grid, 0, 1):
                    self.current_piece.y += 1

                self.add_to_grid(self.current_piece)
                lines_cleared = self.clear_lines()
                self.score += lines_cleared * 100

                self.current_piece = self.new_piece()
                if self.current_piece.check_collision(self.grid):
                    self.game_over = True

                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_piece(self.current_piece)
                self.draw_score()
                self.draw_ai_stats()
                pygame.display.flip()
                self.clock.tick(30)

            self.game_count += 1
            self.total_score += self.score
            pygame.time.wait(1000)

class TetrisAI:
    def __init__(self, epsilon=0.1, alpha=0.1, gamma=0.9):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = {}

    def get_state(self, game):
        return tuple(map(tuple, game.grid))

    def get_actions(self, game):
        actions = []
        piece = game.current_piece
        for rotation in range(4):
            for x in range(GRID_WIDTH):
                test_piece = Shape(x, 0)
                test_piece.shape = piece.shape
                for _ in range(rotation):
                    test_piece.rotate(game.grid)
                if not test_piece.check_collision(game.grid):
                    actions.append((rotation, x))
        return actions

    def choose_action(self, state, actions):
        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            q_values = [self.get_q_value(state, action) for action in actions]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(actions, q_values) if q == max_q]
            return random.choice(best_actions)

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def update_q_value(self, state, action, reward, next_state, next_actions):
        current_q = self.get_q_value(state, action)
        if next_actions:
            max_next_q = max(self.get_q_value(next_state, next_action) for next_action in next_actions)
        else:
            max_next_q = 0
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

    def train(self, game, episodes=1000):
        for episode in range(episodes):
            game.__init__()
            game.ai_mode = True
            state = self.get_state(game)
            total_reward = 0

            while not game.game_over:
                actions = self.get_actions(game)
                action = self.choose_action(state, actions)

                rotation, x = action
                game.current_piece.x = x
                for _ in range(rotation):
                    game.current_piece.rotate(game.grid)

                while not game.current_piece.check_collision(game.grid, 0, 1):
                    game.current_piece.y += 1

                game.add_to_grid(game.current_piece)
                lines_cleared = game.clear_lines()
                reward = lines_cleared * 100
                total_reward += reward

                next_state = self.get_state(game)
                next_actions = self.get_actions(game)

                self.update_q_value(state, action, reward, next_state, next_actions)

                state = next_state
                game.current_piece = game.new_piece()

                if game.current_piece.check_collision(game.grid):
                    game.game_over = True


                game.screen.fill(BLACK)
                game.draw_grid()
                game.draw_piece(game.current_piece)
                game.draw_score()
                game.draw_ai_stats()
                pygame.display.flip()
                game.clock.tick(60)

            game.game_count += 1
            game.total_score += total_reward
            print(f"Episode {episode + 1}, Score: {total_reward}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

    def play(self, game):
        state = self.get_state(game)
        actions = self.get_actions(game)
        return self.choose_action(state, actions)

if __name__ == "__main__":
    game = TetrisGame()
    ai = TetrisAI()


    ai.train(game, episodes=100)


    game.run_ai(ai)

    pygame.quit()