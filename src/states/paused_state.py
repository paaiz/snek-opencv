import os
import pygame
from src.config import (
    PANEL_WIDTH,
    PANEL_HEIGHT,
    COLOR_YELLOW,
    COLOR_WHITE,
    COLOR_GRAY,
    COLOR_SNAKE,
    PAUSE_COUNTDOWN_SECONDS,
    FONT_BOLD_PATH,
)
from src.states.base_state import BaseState
from src.camera_ui import CameraUI


class PausedState(BaseState):
    def __init__(self, snake_game, font_title, font_normal):
        super().__init__(snake_game, font_title, font_normal)
        if os.path.exists(FONT_BOLD_PATH):
            self.font_countdown = pygame.font.Font(FONT_BOLD_PATH, 72)
        else:
            self.font_countdown = pygame.font.SysFont("consolas", 90, bold=True)
        self.countdown_start_time = None
        self.is_keyboard_resuming = False
        self.last_dpad_direction = None

    def enter(self):
        self.countdown_start_time = None
        self.is_keyboard_resuming = False
        self.last_dpad_direction = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_SPACE):
                if self.countdown_start_time is None:
                    self.countdown_start_time = pygame.time.get_ticks()
                    self.is_keyboard_resuming = True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.snake_game.set_direction("UP")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.snake_game.set_direction("DOWN")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.snake_game.set_direction("LEFT")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.snake_game.set_direction("RIGHT")
        return None

    def get_remaining_seconds(self, current_time):
        if self.countdown_start_time is None:
            return None
        elapsed_ms = current_time - self.countdown_start_time
        total_countdown_ms = PAUSE_COUNTDOWN_SECONDS * 1000
        if elapsed_ms >= total_countdown_ms:
            return 0
        return (total_countdown_ms - elapsed_ms + 999) // 1000

    def update(self, tracking_data, current_time):
        is_detected = tracking_data["is_detected"]
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]

        if is_detected:
            if self.countdown_start_time is None:
                self.countdown_start_time = current_time

            detected_direction = CameraUI.get_dpad_direction(sensor_x, sensor_y)
            if detected_direction and detected_direction != self.last_dpad_direction:
                self.snake_game.set_direction(detected_direction)
            self.last_dpad_direction = detected_direction
        else:
            self.last_dpad_direction = None
            if not self.is_keyboard_resuming:
                self.countdown_start_time = None

        remaining_seconds = self.get_remaining_seconds(current_time)
        if remaining_seconds is not None and remaining_seconds <= 0:
            self.snake_game.last_move_time = current_time
            return "PLAYING"

        return None

    def draw_camera(self, camera_frame, tracking_data):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        current_time = pygame.time.get_ticks()
        remaining_seconds = self.get_remaining_seconds(current_time)

        if remaining_seconds is not None and remaining_seconds > 0:
            CameraUI.draw_status_label(
                camera_frame,
                f"SIAP-SIAP: {remaining_seconds}s",
                (0, 255, 255),
                font_scale=0.85,
            )
        else:
            CameraUI.draw_status_label(
                camera_frame,
                "PAUSED (Sensor Hilang)",
                (0, 0, 255),
                font_scale=0.8,
            )

        CameraUI.draw_dpad_buttons(camera_frame, sensor_x, sensor_y)

    def draw_game(self, game_surface):
        self.snake_game.draw(game_surface, self.font_normal)

        overlay_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 160))
        game_surface.blit(overlay_surface, (0, 0))

        current_time = pygame.time.get_ticks()
        remaining_seconds = self.get_remaining_seconds(current_time)

        if remaining_seconds is not None and remaining_seconds > 0:
            ready_title = self.font_title.render("SIAP - SIAP!", True, COLOR_YELLOW)
            countdown_number = self.font_countdown.render(
                str(remaining_seconds), True, COLOR_SNAKE
            )
            direction_hint = self.font_normal.render(
                "Posisikan tangan di tombol arah...", True, COLOR_WHITE
            )

            game_surface.blit(
                ready_title,
                ready_title.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - 80)),
            )
            game_surface.blit(
                countdown_number,
                countdown_number.get_rect(
                    center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 5)
                ),
            )
            game_surface.blit(
                direction_hint,
                direction_hint.get_rect(
                    center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 80)
                ),
            )
        else:
            pause_title = self.font_title.render("PAUSED", True, COLOR_YELLOW)
            primary_hint = self.font_normal.render(
                "Arahkan tangan kembali ke kamera", True, COLOR_WHITE
            )
            secondary_hint = self.font_normal.render(
                f"(Countdown {PAUSE_COUNTDOWN_SECONDS} detik akan mulai saat terdeteksi)",
                True,
                COLOR_GRAY,
            )

            game_surface.blit(
                pause_title,
                pause_title.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - 40)),
            )
            game_surface.blit(
                primary_hint,
                primary_hint.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 10)),
            )
            game_surface.blit(
                secondary_hint,
                secondary_hint.get_rect(
                    center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 45)
                ),
            )
