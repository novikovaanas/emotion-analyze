from collections import deque
import importlib.resources
import json

import cv2
import mediapipe as mp  # type: ignore
import matplotlib.pyplot as plt

import laba_med.reactions


# Инициализация MediaPipe для обнаружения лица и ключевых точек
def analyze_expression(landmarks):
    left_mouth = landmarks[61]
    right_mouth = landmarks[291]
    top_mouth = landmarks[0]
    bottom_mouth = landmarks[17]
    left_eye_top = landmarks[386]
    left_eye_bottom = landmarks[374]
    right_eye_top = landmarks[159]
    right_eye_bottom = landmarks[145]

    # Расчёт расстояний между ключевыми точками
    mouth_width = (
        (left_mouth.x - right_mouth.x) ** 2
        + (left_mouth.y - right_mouth.y) ** 2
    ) ** 0.5
    mouth_height = (
        (top_mouth.x - bottom_mouth.x) ** 2
        + (top_mouth.y - bottom_mouth.y) ** 2
    ) ** 0.5
    left_eye_height = abs(left_eye_top.y - left_eye_bottom.y)
    right_eye_height = abs(right_eye_top.y - right_eye_bottom.y)

    # Рассчёт интенсивности эмоций
    smiling_intensity = min(
        int((mouth_width / (mouth_height * 2.5)) * 85), 100
    )
    surprised_intensity = min(
        int((mouth_height / (mouth_width * 1.2)) * 100), 100
    )
    angry_intensity = min(
        int((0.05 / (left_eye_height + right_eye_height)) * 25), 100
    )
    neutral_intensity = 100 - max(
        smiling_intensity, surprised_intensity, angry_intensity
    )

    return {
        "Smiling": smiling_intensity,
        "Surprised": surprised_intensity,
        "Angry": angry_intensity,
        "Neutral": neutral_intensity,
    }


def main(video_name: str):
    file_path = str(
        importlib.resources.files(laba_med.reactions).joinpath(
            f"{video_name}_face_recogn.txt"
        ),
    )

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5
    )

    # Инициализация OpenCV для работы с веб-камерой
    cap = cv2.VideoCapture(0)

    # Инициализация графика
    plt.ion()
    fig, ax = plt.subplots()
    time_window = 100  # Количество отсчётов, видимых на графике
    emotions = ["Smiling", "Surprised", "Angry", "Neutral"]
    data = {
        emotion: deque([0] * time_window, maxlen=time_window)
        for emotion in emotions
    }
    lines = {
        emotion: ax.plot([], [], label=emotion)[0] for emotion in emotions
    }
    ax.set_ylim(0, 100)
    ax.set_xlim(0, time_window)
    ax.legend()

    # Основной цикл обработки видео
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Не удалось захватить изображение с камеры.")
            break

        # Отражение по горизонтали для более естественного отображения
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Обработка кадра с помощью MediaPipe
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                # Анализ эмоций
                expressions = analyze_expression(landmarks)

                with open(file_path, mode="a") as file:
                    json_reaction = json.dumps(expressions)

                    file.write(json_reaction + "\n")

                # Обновление данных для графика
                for emotion, intensity in expressions.items():
                    data[emotion].append(intensity)

                # Вывод интенсивности эмоций на экран
                y_position = 30
                for expression, intensity in expressions.items():
                    cv2.putText(
                        frame,
                        f"{expression}: {intensity}%",
                        (10, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )
                    y_position += 30

                # Отображение сетки лица (опционально)
                for landmark in landmarks:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

        # Отображение результата
        cv2.imshow("Emotion Detection", frame)

        # Обновление графика
        for emotion, line in lines.items():
            line.set_ydata(data[emotion])
            line.set_xdata(range(len(data[emotion])))
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Нажатие клавиши 'q' для выхода
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show()
