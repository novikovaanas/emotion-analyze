import json
import importlib.resources

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)

from matplotlib.figure import Figure
import PySide6.QtWidgets as QtWidgets

import laba_med.reactions
from laba_med.players.media_player import MediaPlayer


class MediaPlayerReactions(MediaPlayer):
    def __init__(self):
        super().__init__()

        # Переменные для лайков и дизлайков
        self._likes = 0
        self._dislikes = 0
        self._reactions = []  # Список для хранения реакций
        self._timestamps = []  # Список для хранения временных меток

        self._set_like_button()
        self._set_like_count_label()
        self._set_dislike_button()
        self._set_dislike_count_label()

        # Настройка графика
        self._setup_chart()

    def _set_like_button(self):
        self._likeButton = QtWidgets.QPushButton("\ud83d\udc4d Like", self)
        self._likeButton.clicked.connect(self._like)
        self._likeButton.setGeometry(340, 520, 100, 40)

    def _set_like_count_label(self):
        self._likeCountLabel = QtWidgets.QLabel(f"Likes: {self._likes}", self)
        self._likeCountLabel.setGeometry(10, 460, 200, 40)
        self._likeCountLabel.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green;"
        )

    def _set_dislike_button(self):
        self._dislikeButton = QtWidgets.QPushButton(
            "\ud83d\udc4e Dislike", self
        )
        self._dislikeButton.clicked.connect(self._dislike)
        self._dislikeButton.setGeometry(450, 520, 100, 40)

    def _set_dislike_count_label(self):
        self._dislikeCountLabel = QtWidgets.QLabel(
            f"Dislikes: {self._dislikes}", self
        )
        self._dislikeCountLabel.setGeometry(220, 460, 200, 40)
        self._dislikeCountLabel.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: red;"
        )

    def _setup_chart(self):
        """Инициализация графика"""
        self._figure = Figure()
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setParent(self)
        self._canvas.setGeometry(800, 10, 540, 400)
        self._ax = self._figure.add_subplot(111)
        self._ax.set_title("Balance of Reactions")
        self._ax.set_xlabel("Time (s)")
        self._ax.set_ylabel("Balance (Likes - Dislikes)")
        (self._line,) = self._ax.plot([], [], label="Balance", color="blue")
        self._ax.legend()

    def _like(self):
        """Увеличение количества лайков, сохранение реакции и запись в файл."""
        if self._player.is_playing():
            self._likes += 1
            self._likeCountLabel.setText(f"Likes: {self._likes}")
            self._save_reaction("like", self._player.get_time())
            self._update_chart()

    def _dislike(self):
        """Увеличение количества дизлайков, сохранение реакции и запись в файл."""
        if self._player.is_playing():
            self._dislikes += 1
            self._dislikeCountLabel.setText(f"Dislikes: {self._dislikes}")
            self._save_reaction("dislike", self._player.get_time())
            self._update_chart()

    def _play(self):
        """Пуск воспроизведения видео"""
        super().play()
        self._reset_reactions()
        self._update_chart()

    def _stop(self):
        """Остановка воспроизведения видео"""
        super().stop()
        self._reset_reactions()
        self._update_chart()

    def _reset_reactions(self):
        """Сброс лайков, дизлайков и реакций."""
        self._likes = 0
        self._dislikes = 0
        self._reactions = []
        self._timestamps = []
        self._likeCountLabel.setText(f"Likes: {self._likes}")
        self._dislikeCountLabel.setText(f"Dislikes: {self._dislikes}")

    def _save_reaction(self, reaction, timestamp):
        """Сохранение реакции в список и запись в файл."""

        self._reactions.append(reaction)
        self._timestamps.append(timestamp // 1000)
        file_path = str(
            importlib.resources.files(laba_med.reactions).joinpath(
                f"{self._video_name}.txt"
            ),
        )

        with open(file_path, mode="a") as file:
            json_reaction = json.dumps(
                {
                    "reaction": 1 if reaction == "like" else 0,
                    "timestamp": timestamp // 1000,
                }
            )

            file.write(json_reaction + "\n")

    def _update_chart(self):
        """Обновление графика реакции."""
        balance = 0
        balances = []
        for reaction in self._reactions:
            if reaction == "like":
                balance += 1
            elif reaction == "dislike":
                balance -= 1
            balances.append(balance)

        self._line.set_data(self._timestamps, balances)
        self._ax.relim()
        self._ax.autoscale_view()
        self._canvas.draw()
