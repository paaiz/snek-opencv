import pygame
from src.config import (
    PANEL_WIDTH,
    PANEL_HEIGHT,
    COLOR_DANGER,
    COLOR_WHITE,
    COLOR_GRAY,
    BUTTON_RETRY_BOX,
    BUTTON_MENU_BOX,
)
from src.states.base_state import BaseState
from src.camera_ui import CameraUI


class GameOverState(BaseState):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_SPACE):
                self.snake_game.reset()
                return "PLAYING"
            elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                return "MENU"
        return None

    def update(self, tracking_data, current_time):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        is_detected = tracking_data["is_detected"]

        if is_detected:
            if CameraUI.is_point_inside_box(sensor_x, sensor_y, BUTTON_RETRY_BOX):
                self.snake_game.reset()
                return "PLAYING"
            elif CameraUI.is_point_inside_box(sensor_x, sensor_y, BUTTON_MENU_BOX):
                return "MENU"

        return None

    def draw_camera(self, camera_frame, tracking_data):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        CameraUI.draw_status_label(camera_frame, "GAME OVER", (0, 0, 255))

        CameraUI.draw_button(
            camera_frame,
            BUTTON_RETRY_BOX,
            "RETRY",
            sensor_x,
            sensor_y,
            40,
            50,
            font_scale=1.0,
        )
        CameraUI.draw_button(
            camera_frame,
            BUTTON_MENU_BOX,
            "MENU",
            sensor_x,
            sensor_y,
            50,
            50,
            font_scale=1.0,
        )

    def draw_game(self, game_surface):
        self.snake_game.draw(game_surface, self.font_normal)

        overlay_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 170))
        game_surface.blit(overlay_surface, (0, 0))

        game_over_title = self.font_title.render("GAME OVER", True, COLOR_DANGER)
        final_score_text = self.font_normal.render(
            f"Final Score: {self.snake_game.score}", True, COLOR_WHITE
        )
        action_hint = self.font_normal.render(
            "Sentuh RETRY atau MENU di kamera", True, COLOR_GRAY
        )

        game_surface.blit(
            game_over_title,
            game_over_title.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - 50)),
        )
        game_surface.blit(
            final_score_text,
            final_score_text.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 10)),
        )
        game_surface.blit(
            action_hint,
            action_hint.get_rect(center=(PANEL_WIDTH / 2, PANEL_HEIGHT / 2 + 50)),
        )
