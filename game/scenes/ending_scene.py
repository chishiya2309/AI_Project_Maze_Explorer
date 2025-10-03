import os
import pygame
from core.scene import Scene
import cv2


class EndingScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 24, bold=True)
        self.info = None
        self.cap = None
        self.frame_surface = None
        self.finished = False
        # Playback control
        self.playback_speed = 0.5  # 0.5x speed
        self.frame_interval_ms = 33.3  # default ~30fps, will be overwritten if possible
        self._frame_timer_ms = 0.0
        self._init_video()

    def _init_video(self):
        try:
            import cv2  # Lazy import; only needed here
        except Exception:
            self.info = "Missing OpenCV (cv2). Unable to play ending video. Press any key to return."
            return

        # Try common locations
        candidates = [
            os.path.join("data", "video", "Ending_Video.mp4"),
            os.path.join("data", "Ending_Video.mp4"),  # legacy path fallback
        ]
        video_path = None
        for p in candidates:
            if os.path.isfile(p):
                video_path = p
                break

        if video_path is None:
            self.info = "Ending_Video.mp4 not found. Press any key to return."
            return

        self.cv2 = cv2
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.info = "Failed to open video. Press any key to return."
            self.cap = None
            return

        # Determine frame interval from video FPS
        fps = self.cap.get(self.cv2.CAP_PROP_FPS) or 0
        if fps and fps > 0:
            self.frame_interval_ms = 1000.0 / float(fps)

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            # Any key to skip/end
            from .menu_scene import MenuScene
            self.game.scenes.switch(MenuScene(self.game))
        elif e.type == pygame.MOUSEBUTTONDOWN:
            from .menu_scene import MenuScene
            self.game.scenes.switch(MenuScene(self.game))

    def update(self, dt):
        if self.finished or self.cap is None:
            return

        # Advance timer; only read next frame when enough time has elapsed for target speed
        self._frame_timer_ms += dt
        target_interval = self.frame_interval_ms / max(1e-6, self.playback_speed)
        if self._frame_timer_ms < target_interval:
            return
        self._frame_timer_ms -= target_interval

        ok, frame = self.cap.read()
        if not ok:
            # Video ended
            self.finished = True
            from .menu_scene import MenuScene
            self.game.scenes.switch(MenuScene(self.game))
            return

        # Convert BGR -> RGB
        frame_rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape

        # Scale to fit screen while preserving aspect ratio
        sw, sh = self.game.screen.get_size()
        scale = min(sw / w, sh / h)
        tw, th = int(w * scale), int(h * scale)
        frame_resized = self.cv2.resize(frame_rgb, (tw, th), interpolation=self.cv2.INTER_AREA)

        # Create pygame surface from buffer
        self.frame_surface = pygame.image.frombuffer(frame_resized.tobytes(), (tw, th), "RGB")

    def draw(self, screen):
        screen.fill((0, 0, 0))
        sw, sh = screen.get_size()

        if self.info is not None:
            # Show info text fallback
            text = self.font.render(self.info, True, (255, 255, 255))
            rect = text.get_rect(center=(sw // 2, sh // 2))
            screen.blit(text, rect)
            hint = self.font.render("Press any key to return to menu", True, (180, 180, 180))
            rect2 = hint.get_rect(center=(sw // 2, sh // 2 + 40))
            screen.blit(hint, rect2)
            return

        if self.frame_surface is not None:
            fw, fh = self.frame_surface.get_size()
            rect = self.frame_surface.get_rect(center=(sw // 2, sh // 2))
            screen.blit(self.frame_surface, rect)



