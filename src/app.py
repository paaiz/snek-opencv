import os
import sys
import pygame

from src.config import (
    CAMERA_HEIGHT,
    PANEL_WIDTH,
    PANEL_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLOR_WHITE,
    FONT_REGULAR_PATH,
    FONT_BOLD_PATH,
)
from src.vision_tracker import VisionTracker
from src.snake import SnakeGame
from src.states import MenuState, PlayingState, PausedState, GameOverState


class GameApp:
    def __init__(self):
        pygame.init()
        self.window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("It's a snek!")
        self.frame_clock = pygame.time.Clock()

        self.font_title = self.load_font(
            FONT_BOLD_PATH, 36, fallback_name="consolas", is_bold=True
        )
        self.font_normal = self.load_font(
            FONT_REGULAR_PATH, 16, fallback_name="consolas", is_bold=True
        )

        self.game_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        self.snake_game = SnakeGame()
        self.vision_tracker = VisionTracker()

        self.game_states = {
            "MENU": MenuState(self.snake_game, self.font_title, self.font_normal),
            "PLAYING": PlayingState(self.snake_game, self.font_title, self.font_normal),
            "PAUSED": PausedState(self.snake_game, self.font_title, self.font_normal),
            "GAME_OVER": GameOverState(
                self.snake_game, self.font_title, self.font_normal
            ),
        }

        self.current_state_key = "MENU"
        self.current_state = self.game_states[self.current_state_key]
        self.is_running = True

    @staticmethod
    def load_font(font_path, font_size, fallback_name="consolas", is_bold=False):
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, font_size)
        return pygame.font.SysFont(fallback_name, font_size, bold=is_bold)

    def change_state(self, next_state_key):
        if next_state_key and next_state_key in self.game_states:
            self.current_state_key = next_state_key
            self.current_state = self.game_states[self.current_state_key]
            self.current_state.enter()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            else:
                next_state_key = self.current_state.handle_event(event)
                self.change_state(next_state_key)

    def render(self, camera_frame, process_frame, tracking_data):
        self.current_state.draw_camera(camera_frame, tracking_data)
        self.current_state.draw_game(self.game_surface)

        camera_surface = VisionTracker.to_pygame_surface(camera_frame)
        process_surface = VisionTracker.to_pygame_surface(process_frame)

        self.window_surface.blit(camera_surface, (0, 0))
        self.window_surface.blit(process_surface, (0, CAMERA_HEIGHT))
        self.window_surface.blit(self.game_surface, (PANEL_WIDTH, 0))

        pygame.draw.line(
            self.window_surface,
            COLOR_WHITE,
            (0, CAMERA_HEIGHT),
            (PANEL_WIDTH, CAMERA_HEIGHT),
            2,
        )
        pygame.draw.line(
            self.window_surface,
            COLOR_WHITE,
            (PANEL_WIDTH, 0),
            (PANEL_WIDTH, WINDOW_HEIGHT),
            2,
        )

        pygame.display.flip()

    def run(self):
        while self.is_running:
            current_time = pygame.time.get_ticks()
            self.handle_events()

            camera_frame, process_frame, tracking_data = (
                self.vision_tracker.read_frame()
            )

            next_state_key = self.current_state.update(tracking_data, current_time)
            self.change_state(next_state_key)

            self.render(camera_frame, process_frame, tracking_data)
            self.frame_clock.tick(FPS)

        self.vision_tracker.release()
        pygame.quit()
        sys.exit()
