import pygame
from src.states.base_state import BaseState
from src.camera_ui import CameraUI


class PlayingState(BaseState):
    def __init__(self, snake_game, font_title, font_normal):
        super().__init__(snake_game, font_title, font_normal)
        self.was_sensor_detected = False
        self.last_dpad_direction = None

    def enter(self):
        self.was_sensor_detected = False
        self.last_dpad_direction = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.snake_game.set_direction("UP")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.snake_game.set_direction("DOWN")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.snake_game.set_direction("LEFT")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.snake_game.set_direction("RIGHT")
            elif event.key == pygame.K_p:
                return "PAUSED"
        return None

    def update(self, tracking_data, current_time):
        is_detected = tracking_data["is_detected"]
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]

        if is_detected:
            self.was_sensor_detected = True
            detected_direction = CameraUI.get_dpad_direction(sensor_x, sensor_y)
            if detected_direction and detected_direction != self.last_dpad_direction:
                self.snake_game.set_direction(detected_direction)
            self.last_dpad_direction = detected_direction
        else:
            self.last_dpad_direction = None
            if self.was_sensor_detected:
                return "PAUSED"

        has_collided = self.snake_game.update(current_time)
        if has_collided:
            return "GAME_OVER"

        return None

    def draw_camera(self, camera_frame, tracking_data):
        sensor_x = tracking_data["sensor_x"]
        sensor_y = tracking_data["sensor_y"]
        CameraUI.draw_status_label(camera_frame, "PLAYING", (0, 255, 0))
        CameraUI.draw_dpad_buttons(camera_frame, sensor_x, sensor_y)

    def draw_game(self, game_surface):
        self.snake_game.draw(game_surface, self.font_normal)
