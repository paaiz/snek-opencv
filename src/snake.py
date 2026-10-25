import random
import pygame
from src.config import (
    PANEL_WIDTH,
    PANEL_HEIGHT,
    GRID_SIZE,
    SNAKE_MOVE_DELAY_MS,
    MIN_FOOD_COUNT,
    MAX_FOOD_COUNT,
    SCORE_PER_FOOD,
    COLOR_BG,
    COLOR_GRID,
    COLOR_SNAKE,
    COLOR_FOOD,
    COLOR_WHITE,
)

OPPOSITE_DIRECTIONS = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

class SnakeGame:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.move_delay_ms = SNAKE_MOVE_DELAY_MS
        self.body_segments = []
        self.current_direction = "UP"
        self.direction_queue = []
        self.food_positions = []
        self.score = 0
        self.is_alive = True
        self.last_move_time = 0
        self.reset()

    def get_random_free_position(self):
        max_cols = PANEL_WIDTH // self.grid_size
        max_rows = PANEL_HEIGHT // self.grid_size

        while True:
            candidate_position = [
                random.randrange(0, max_cols) * self.grid_size,
                random.randrange(0, max_rows) * self.grid_size,
            ]
            if (
                candidate_position not in self.body_segments
                and candidate_position not in self.food_positions
            ):
                return candidate_position

    def spawn_random_foods(self):
        target_food_count = random.randint(MIN_FOOD_COUNT, MAX_FOOD_COUNT)
        while len(self.food_positions) < target_food_count:
            self.food_positions.append(self.get_random_free_position())

    def reset(self):
        start_x = PANEL_WIDTH // 2
        start_y = PANEL_HEIGHT // 2
        self.body_segments = [[start_x, start_y]]
        self.current_direction = "UP"
        self.direction_queue = []
        self.food_positions = []
        self.spawn_random_foods()
        self.score = 0
        self.is_alive = True
        self.last_move_time = pygame.time.get_ticks()

    def set_direction(self, requested_direction):
        if requested_direction not in OPPOSITE_DIRECTIONS:
            return

        reference_direction = (
            self.direction_queue[-1]
            if self.direction_queue
            else self.current_direction
        )

        if (
            requested_direction != reference_direction
            and requested_direction != OPPOSITE_DIRECTIONS[reference_direction]
            and len(self.direction_queue) < 2
        ):
            self.direction_queue.append(requested_direction)

    def update(self, current_time):
        if not self.is_alive:
            return True

        if current_time - self.last_move_time < self.move_delay_ms:
            return False

        if self.direction_queue:
            self.current_direction = self.direction_queue.pop(0)

        head_x, head_y = self.body_segments[0]
        if self.current_direction == "UP":
            head_y -= self.grid_size
        elif self.current_direction == "DOWN":
            head_y += self.grid_size
        elif self.current_direction == "LEFT":
            head_x -= self.grid_size
        elif self.current_direction == "RIGHT":
            head_x += self.grid_size

        head_x %= PANEL_WIDTH
        head_y %= PANEL_HEIGHT

        new_head = [head_x, head_y]
        self.body_segments.insert(0, new_head)

        if new_head in self.food_positions:
            self.food_positions.remove(new_head)
            self.score += SCORE_PER_FOOD
            self.spawn_random_foods()
        else:
            self.body_segments.pop()

        if new_head in self.body_segments[1:]:
            self.is_alive = False
            return True

        self.last_move_time = current_time
        return False

    def draw_grid(self, game_surface):
        for x in range(0, PANEL_WIDTH, self.grid_size):
            pygame.draw.line(game_surface, COLOR_GRID, (x, 0), (x, PANEL_HEIGHT))
        for y in range(0, PANEL_HEIGHT, self.grid_size):
            pygame.draw.line(game_surface, COLOR_GRID, (0, y), (PANEL_WIDTH, y))

    def draw(self, game_surface, score_font):
        game_surface.fill(COLOR_BG)
        self.draw_grid(game_surface)

        for food_x, food_y in self.food_positions:
            food_rect = pygame.Rect(
                food_x,
                food_y,
                self.grid_size,
                self.grid_size,
            )
            pygame.draw.rect(game_surface, COLOR_FOOD, food_rect)

        for segment_x, segment_y in self.body_segments:
            segment_rect = pygame.Rect(
                segment_x, segment_y, self.grid_size, self.grid_size
            )
            pygame.draw.rect(game_surface, COLOR_SNAKE, segment_rect)
            pygame.draw.rect(game_surface, COLOR_BG, segment_rect, 1)

        score_surface = score_font.render(f"Score: {self.score}", True, COLOR_WHITE)
        game_surface.blit(score_surface, (10, 10))
