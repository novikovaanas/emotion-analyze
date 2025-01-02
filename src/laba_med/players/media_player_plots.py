import json
import importlib.resources
from collections import defaultdict

import matplotlib.pyplot as plt
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)

import laba_med.reactions
from .media_player import MediaPlayer
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
import matplotlib.pyplot as plt
from collections import deque
import numpy as np


class MediaPlayerPlots(MediaPlayer):
    def __init__(self):
        super().__init__()
        self._likes = defaultdict(int)
        self._dislikes = defaultdict(int)

        # Канвас для графика с увеличенной высотой (вытянутый по вертикали)
        self._figure, self._ax = plt.subplots(
            figsize=(5, 6)
        )  # Увеличиваем высоту графика
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setGeometry(
            800, 500, 600, 350
        )  # Увеличиваем высоту канваса
        self._canvas.setParent(self)

        # Таймер для обновления графика каждую секунду
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_graph)
        self._timer.start(1000)  # Обновление каждую секунду

        # Список для хранения меток времени
        self._timestamps = []
        self.graph_widget = QWidget(self)
        self.graph_widget.setGeometry(
            800, 10, 780, 500
        )  # Позиция и размеры виджета

        # Лейаут для размещения графиков
        self.layout = QVBoxLayout(self.graph_widget)

        # Создание фигуры и канваса для графика эмоций
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Состояния эмоций
        self.emotions = ["Smiling", "Surprised", "Angry", "Neutral"]
        self.time_window = 100
        self.data = {
            emotion: deque([0] * self.time_window, maxlen=self.time_window)
            for emotion in self.emotions
        }
        self.lines = {
            emotion: self.ax.plot([], [], label=emotion)[0]
            for emotion in self.emotions
        }

        # Настройка графика
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, self.time_window)
        self.ax.legend()

        # Таймер для обновления графика
        self.emotion_timer = QTimer(self)
        self.emotion_timer.timeout.connect(self._update_face_reaction_plot)
        self.emotion_timer.start(100)  # Обновление каждые 100 мс

    def _open_video(self, filename):
        super().open_video(filename)
        self._load_reactions()

    def _load_reactions(self):
        file_path = str(
            importlib.resources.files(laba_med.reactions).joinpath(
                f"{self._video_name}.txt"
            ),
        )

        with open(file_path, "r") as file:
            for line in file:
                json_data = json.loads(line)
                timestamp = int(json_data["timestamp"])
                if json_data["reaction"] == 0:
                    self._dislikes[timestamp] += 1
                else:
                    self._likes[timestamp] += 1

    def _update_graph(self):
        """
        Обновляет график каждую секунду,
        показывая количество лайков и дизлайков за последние 2 секунды.
        """
        if self._player.get_time() == -1:
            return

        current_time = int(self._player.get_time() / 1000)

        recent_likes = 0
        recent_dislikes = 0

        for i in range(current_time + 1):
            recent_likes += self._likes[i]
            recent_dislikes += self._dislikes[i]

        # Обновляем график
        self._ax.clear()
        self._ax.bar(
            ["Likes", "Dislikes"],
            [recent_likes, recent_dislikes],
            color=["green", "red"],
        )
        self._ax.set_title(f"Likes and Dislikes from start")
        self._ax.set_ylabel("Count")

        self._canvas.draw()

        self._canvas.flush_events()

    def _update_face_reaction_plot(self):
        """
        Обновляет график эмоций.
        """
        if not self._player.is_playing():
            return

        # Обновление данных эмоций
        self.data["Smiling"].append(
            np.clip(
                self.data["Smiling"][-1] + np.random.uniform(-3, 3), 40, 80
            )
        )
        self.data["Surprised"].append(
            np.clip(
                self.data["Surprised"][-1] + np.random.uniform(-4, 4), 20, 65
            )
        )
        self.data["Angry"].append(
            np.clip(self.data["Angry"][-1] + np.random.uniform(-1, 1), 20, 30)
        )
        self.data["Neutral"].append(
            100
            - max(
                self.data["Smiling"][-1],
                self.data["Surprised"][-1],
                self.data["Angry"][-1],
            )
        )

        # Обновление линий графика
        for emotion, line in self.lines.items():
            line.set_ydata(self.data[emotion])
            line.set_xdata(range(len(self.data[emotion])))

        # Обновление отрисовки
        self.canvas.draw()
