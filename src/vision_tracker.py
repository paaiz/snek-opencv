import cv2
import numpy as np
import pygame
from src.config import (
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    PROCESS_PANEL_HEIGHT,
    HSV_GREEN_LOWER,
    HSV_GREEN_UPPER,
    MIN_CONTOUR_AREA,
    SENSOR_SMOOTHING_FACTOR,
)

class VisionTracker:
    def __init__(self, camera_index=0):
        self.camera = cv2.VideoCapture(camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.smoothed_x = -1
        self.smoothed_y = -1

    def apply_smoothing(self, raw_x, raw_y):
        if self.smoothed_x == -1 or self.smoothed_y == -1:
            self.smoothed_x = raw_x
            self.smoothed_y = raw_y
        else:
            self.smoothed_x = int(
                SENSOR_SMOOTHING_FACTOR * raw_x
                + (1.0 - SENSOR_SMOOTHING_FACTOR) * self.smoothed_x
            )
            self.smoothed_y = int(
                SENSOR_SMOOTHING_FACTOR * raw_y
                + (1.0 - SENSOR_SMOOTHING_FACTOR) * self.smoothed_y
            )
        return self.smoothed_x, self.smoothed_y

    def reset_smoothing(self):
        self.smoothed_x = -1
        self.smoothed_y = -1

    @staticmethod
    def add_stage_label(stage_frame, label_text):
        header_overlay = stage_frame.copy()
        cv2.rectangle(header_overlay, (0, 0), (stage_frame.shape[1], 24), (0, 0, 0), -1)
        cv2.addWeighted(header_overlay, 0.65, stage_frame, 0.35, 0, stage_frame)
        cv2.putText(
            stage_frame,
            label_text,
            (8, 17),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    @classmethod
    def build_process_panel(cls, hsv_frame, green_mask, isolated_green_frame):
        first_width = CAMERA_WIDTH // 3
        second_width = CAMERA_WIDTH // 3
        third_width = CAMERA_WIDTH - first_width - second_width

        hsv_preview = cv2.resize(hsv_frame, (first_width, PROCESS_PANEL_HEIGHT))
        mask_bgr = cv2.cvtColor(green_mask, cv2.COLOR_GRAY2BGR)
        mask_preview = cv2.resize(mask_bgr, (second_width, PROCESS_PANEL_HEIGHT))
        isolated_preview = cv2.resize(
            isolated_green_frame, (third_width, PROCESS_PANEL_HEIGHT)
        )

        cls.add_stage_label(hsv_preview, "1. HSV SPACE")
        cls.add_stage_label(mask_preview, "2. BINARY MASK")
        cls.add_stage_label(isolated_preview, "3. GREEN RESULT")

        process_panel = np.hstack((hsv_preview, mask_preview, isolated_preview))

        divider_one_x = first_width
        divider_two_x = first_width + second_width
        cv2.line(
            process_panel,
            (divider_one_x, 0),
            (divider_one_x, PROCESS_PANEL_HEIGHT),
            (200, 200, 200),
            1,
        )
        cv2.line(
            process_panel,
            (divider_two_x, 0),
            (divider_two_x, PROCESS_PANEL_HEIGHT),
            (200, 200, 200),
            1,
        )
        return process_panel

    def read_frame(self):
        is_frame_read, camera_frame = self.camera.read()
        if not is_frame_read:
            self.reset_smoothing()
            empty_camera = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
            empty_process = np.zeros(
                (PROCESS_PANEL_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8
            )
            return (
                empty_camera,
                empty_process,
                {"sensor_x": -1, "sensor_y": -1, "is_detected": False},
            )

        camera_frame = cv2.flip(camera_frame, 1)

        hsv_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv_frame, HSV_GREEN_LOWER, HSV_GREEN_UPPER)
        green_mask = cv2.erode(green_mask, None, iterations=2)
        green_mask = cv2.dilate(green_mask, None, iterations=2)

        isolated_green_frame = cv2.bitwise_and(
            camera_frame, camera_frame, mask=green_mask
        )

        contours, _ = cv2.findContours(
            green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        sensor_x, sensor_y = -1, -1
        is_detected = False

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest_contour)

            if contour_area >= MIN_CONTOUR_AREA:
                moments = cv2.moments(largest_contour)
                if moments["m00"] != 0:
                    raw_x = int(moments["m10"] / moments["m00"])
                    raw_y = int(moments["m01"] / moments["m00"])
                    sensor_x, sensor_y = self.apply_smoothing(raw_x, raw_y)
                    is_detected = True

                    cv2.circle(camera_frame, (sensor_x, sensor_y), 10, (0, 0, 255), -1)
                    cv2.circle(
                        camera_frame, (sensor_x, sensor_y), 12, (255, 255, 255), 2
                    )

                    cv2.drawContours(
                        isolated_green_frame,
                        [largest_contour],
                        -1,
                        (0, 255, 255),
                        2,
                    )
                    cv2.circle(
                        isolated_green_frame, (sensor_x, sensor_y), 8, (0, 0, 255), -1
                    )

        if not is_detected:
            self.reset_smoothing()

        process_frame = self.build_process_panel(
            hsv_frame, green_mask, isolated_green_frame
        )

        tracking_data = {
            "sensor_x": sensor_x,
            "sensor_y": sensor_y,
            "is_detected": is_detected,
        }
        return camera_frame, process_frame, tracking_data

    @staticmethod
    def to_pygame_surface(cv_frame):
        rgb_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        transposed_frame = np.swapaxes(rgb_frame, 0, 1)
        return pygame.surfarray.make_surface(transposed_frame)

    def release(self):
        if self.camera.isOpened():
            self.camera.release()
