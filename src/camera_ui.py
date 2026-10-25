import cv2
from src.config import (
    DPAD_CENTER_X,
    DPAD_CENTER_Y,
    DPAD_INNER_OFFSET,
    BUTTON_W_BOX,
    BUTTON_A_BOX,
    BUTTON_S_BOX,
    BUTTON_D_BOX,
)

class CameraUI:
    @staticmethod
    def is_point_inside_box(point_x, point_y, box_coords):
        left, top, right, bottom = box_coords
        return left < point_x < right and top < point_y < bottom

    @staticmethod
    def draw_status_label(camera_frame, status_text, text_color, font_scale=0.75):
        (text_width, text_height), baseline = cv2.getTextSize(
            status_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
        )
        box_right = 20 + text_width
        box_bottom = 16 + text_height + baseline
        cv2.rectangle(camera_frame, (6, 6), (box_right, box_bottom), (0, 0, 0), -1)
        cv2.rectangle(camera_frame, (6, 6), (box_right, box_bottom), text_color, 1)
        cv2.putText(
            camera_frame,
            status_text,
            (12, 12 + text_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            text_color,
            2,
            cv2.LINE_AA,
        )

    @classmethod
    def draw_button(
        cls,
        camera_frame,
        box_coords,
        label_text,
        sensor_x,
        sensor_y,
        text_offset_x=25,
        text_offset_y=55,
        font_scale=1.2,
    ):
        is_hovered = cls.is_point_inside_box(sensor_x, sensor_y, box_coords)
        left, top, right, bottom = box_coords

        background_color = (0, 255, 0) if is_hovered else (0, 0, 0)
        border_color = (255, 255, 255) if is_hovered else (200, 0, 0)
        text_color = (0, 0, 0) if is_hovered else (255, 255, 255)

        cv2.rectangle(camera_frame, (left, top), (right, bottom), background_color, -1)
        cv2.rectangle(camera_frame, (left, top), (right, bottom), border_color, 2)

        cv2.putText(
            camera_frame,
            label_text,
            (left + text_offset_x, top + text_offset_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            text_color,
            3,
            cv2.LINE_AA,
        )
        return is_hovered

    @classmethod
    def get_dpad_direction(cls, sensor_x, sensor_y):
        if cls.is_point_inside_box(sensor_x, sensor_y, BUTTON_W_BOX):
            return "UP"
        if cls.is_point_inside_box(sensor_x, sensor_y, BUTTON_S_BOX):
            return "DOWN"
        if cls.is_point_inside_box(sensor_x, sensor_y, BUTTON_A_BOX):
            return "LEFT"
        if cls.is_point_inside_box(sensor_x, sensor_y, BUTTON_D_BOX):
            return "RIGHT"
        return None

    @classmethod
    def draw_dpad_buttons(cls, camera_frame, sensor_x, sensor_y):
        deadzone_left = DPAD_CENTER_X - DPAD_INNER_OFFSET
        deadzone_top = DPAD_CENTER_Y - DPAD_INNER_OFFSET
        deadzone_right = DPAD_CENTER_X + DPAD_INNER_OFFSET
        deadzone_bottom = DPAD_CENTER_Y + DPAD_INNER_OFFSET
        cv2.rectangle(
            camera_frame,
            (deadzone_left, deadzone_top),
            (deadzone_right, deadzone_bottom),
            (100, 100, 100),
            1,
        )
        cls.draw_button(camera_frame, BUTTON_W_BOX, "W", sensor_x, sensor_y)
        cls.draw_button(camera_frame, BUTTON_A_BOX, "A", sensor_x, sensor_y)
        cls.draw_button(camera_frame, BUTTON_S_BOX, "S", sensor_x, sensor_y)
        cls.draw_button(camera_frame, BUTTON_D_BOX, "D", sensor_x, sensor_y)
