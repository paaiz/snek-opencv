import pygame
from src.config import (
    PANEL_WIDTH,
    PANEL_HEIGHT,
    COLOR_BG,
    COLOR_WHITE,
    COLOR_GRAY,
    BUTTON_START_BOX,
)
from src.states.base_state import BaseState
from src.camera_ui import CameraUI


class MenuState(BaseState):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_SPACE,
            pygame.K_RETURN,
        ):
            self.snake_game.reset()
            return "PLAYING"
        return None

    def update(self, tracking_data, current_time):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        is_detected = tracking_data["is_detected"]

        if is_detected and CameraUI.is_point_inside_box(
            sensor_x, sensor_y, BUTTON_START_BOX
        ):
            self.snake_game.reset()
            return "PLAYING"

        return None

    def draw_camera(self, camera_frame, tracking_data):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        CameraUI.draw_status_label(camera_frame, "MAIN MENU", (255, 255, 0))
        CameraUI.draw_button(
            camera_frame, BUTTON_START_BOX, "START", sensor_x, sensor_y, 35, 55
        )

    def draw_rainbow_title(
        self, game_surface, prefix_text, rainbow_text, center_x, center_y
    ):
        current_time = pygame.time.get_ticks()
        total_width, total_height = self.font_title.size(prefix_text + rainbow_text)
        start_x = int(center_x - total_width // 2)
        start_y = int(center_y - total_height // 2)

        prefix_surface = self.font_title.render(prefix_text, True, COLOR_WHITE)
        game_surface.blit(prefix_surface, (start_x, start_y))
        char_offset_x = self.font_title.size(prefix_text)[0]

        for index, character in enumerate(rainbow_text):
            hue = int((current_time * 0.25 + index * 25) % 360)
            char_color = pygame.Color(0)
            char_color.hsva = (hue, 100, 100, 100)

            char_surface = self.font_title.render(character, True, char_color)
            game_surface.blit(char_surface, (start_x + char_offset_x, start_y))
            char_offset_x += self.font_title.size(character)[0]

    def draw_game(self, game_surface):
        game_surface.fill(COLOR_BG)
        self.snake_game.draw_grid(game_surface)

        self.draw_rainbow_title(
            game_surface, "It's a ", "Snek!", PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - 40
        )

        primary_hint = self.font_normal.render(
            "Arahkan tangan ke tombol START", True, COLOR_WHITE
        )
        secondary_hint = self.font_normal.render(
            "atau tekan SPACE untuk mulai", True, COLOR_GRAY
        )

        game_surface.blit(
            primary_hint,
            primary_hint.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 20)),
        )
        game_surface.blit(
            secondary_hint,
            secondary_hint.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 50)),
        )
