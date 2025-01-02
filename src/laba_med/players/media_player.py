from pathlib import Path

import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
import vlc  # type: ignore


class MediaPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация VLC и плеера
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()

        # Настройка интерфейса
        self.setWindowTitle("mediaplayer")
        self.setGeometry(100, 100, 800, 600)
        self.__set_play_button()
        self.__set_pause_button()
        self.__set_stop_button()
        self.__set_volume_slider()

        # Создание контейнера для VLC окна
        self._videoFrame = QtWidgets.QFrame(self)
        self._videoFrame.setGeometry(10, 10, 780, 500)

        # Связываем VLC плеер с виджетом
        self._player.set_nsobject(self._videoFrame.winId())

        # Переменные
        self._media = None
        self._video_name = None

    def __set_play_button(self):
        self._playButton = QtWidgets.QPushButton("▶ Play", self)
        self._playButton.setGeometry(10, 520, 100, 40)
        self._playButton.clicked.connect(self.play)

    def __set_pause_button(self):
        self._pauseButton = QtWidgets.QPushButton("❚❚ Pause", self)
        self._pauseButton.setGeometry(120, 520, 100, 40)
        self._pauseButton.clicked.connect(self.pause)

    def __set_stop_button(self):
        self._stopButton = QtWidgets.QPushButton("⏹ Stop", self)
        self._stopButton.clicked.connect(self.stop)
        self._stopButton.setGeometry(230, 520, 100, 40)

    def __set_volume_slider(self):
        self._volumeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._volumeSlider.setGeometry(600, 520, 150, 30)
        self._volumeSlider.setRange(0, 100)  # Устанавливаем диапазон громкости
        self._volumeSlider.setValue(
            50
        )  # Устанавливаем начальную громкость на 50%
        self._volumeSlider.valueChanged.connect(self.change_volume)
        self._player.audio_set_volume(50)

    def open_video(self, filename):
        """
        Load video
        """

        self._media = self._instance.media_new(filename)
        self._video_name = Path(filename).stem
        self._player.set_media(self._media)
        self._player.play()

    def play(self):
        """
        Start playing video
        from the beginning
        """
        self._player.set_media(self._media)
        self._player.play()

    def pause(self):
        """
        Pause/Unpause video
        """
        self._player.pause()

    def stop(self):
        """
        Stops video
        """
        self._player.stop()

    def change_volume(self):
        """
        Change volume
        """

        volume = (
            self._volumeSlider.value()
        )  # Получаем текущее значение слайдера
        self._player.audio_set_volume(volume)  # Устанавливаем громкость
