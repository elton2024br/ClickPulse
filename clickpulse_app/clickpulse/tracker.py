import time
from datetime import datetime
from pynput import mouse


class MouseTracker:
    def __init__(self, database, on_click_callback=None):
        self._db = database
        self._on_click_callback = on_click_callback
        self._listener = None
        self._last_activity = datetime.now()
        self._running = False
        self._paused = False
        self._last_move_time = 0.0

    def start(self):
        if self._running:
            return
        self._running = True
        self._last_activity = datetime.now()
        self._listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move,
            on_scroll=self._on_scroll,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._last_activity = datetime.now()

    def _on_click(self, x, y, button, pressed):
        if not pressed or self._paused:
            return
        button_map = {
            mouse.Button.left: "left",
            mouse.Button.right: "right",
            mouse.Button.middle: "middle",
        }
        button_str = button_map.get(button, "left")
        self._db.insert_click(button_str, int(x), int(y))
        self._last_activity = datetime.now()
        if self._on_click_callback:
            try:
                self._on_click_callback(button_str, int(x), int(y))
            except Exception:
                pass

    def _on_move(self, x, y):
        if self._paused:
            return
        now = time.monotonic()
        if now - self._last_move_time >= 0.1:
            self._last_move_time = now
            self._last_activity = datetime.now()

    def _on_scroll(self, x, y, dx, dy):
        if not self._paused:
            self._last_activity = datetime.now()

    @property
    def last_activity_time(self):
        return self._last_activity

    @property
    def is_running(self):
        return self._running

    @property
    def is_paused(self):
        return self._paused
