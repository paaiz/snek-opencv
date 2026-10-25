class BaseState:
    def __init__(self, snake_game, font_title, font_normal):
        self.snake_game = snake_game
        self.font_title = font_title
        self.font_normal = font_normal

    def enter(self):
        pass

    def handle_event(self, event):
        return None

    def update(self, tracking_data, current_time):
        return None

    def draw_camera(self, camera_frame, tracking_data):
        pass

    def draw_game(self, game_surface):
        pass
