import importlib.resources

import PySide6.QtWidgets as QtWidgets

from laba_med.players import MediaPlayerPlots
import laba_med.videos


def main():
    app = QtWidgets.QApplication([])
    player = MediaPlayerPlots()
    player.show()
    path = importlib.resources.files(laba_med.videos).joinpath(
        "draka.mp4"
    )  # сюда вставляешь название видоса который хочешь запустить
    player._open_video(path)  # Укажите путь к вашему видеофайлу
    app.exec()


if __name__ == "__main__":
    main()
