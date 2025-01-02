import importlib.resources
from multiprocessing import Process
import os

import PySide6.QtWidgets as QtWidgets

from laba_med.players import MediaPlayerReactions
import laba_med.videos
import laba_med.webcam_analyze


def start_webcam_analyze(file_name: str):
    laba_med.webcam_analyze.main(file_name)


def main():
    app = QtWidgets.QApplication([])
    player = MediaPlayerReactions()
    player.show()
    video_name = "draka.mp4"
    path = importlib.resources.files(laba_med.videos).joinpath(
        video_name
    )  # сюда вставляешь название видоса который хочешь запустить
    video_name_without_extension = os.path.splitext(video_name)[0]
    print(video_name_without_extension, type(video_name_without_extension))

    process = Process(
        target=start_webcam_analyze, args=(video_name_without_extension,)
    )
    process.start()

    player.open_video(path)

    app.exec()

    if process.is_alive():
        process.terminate()


if __name__ == "__main__":
    main()
