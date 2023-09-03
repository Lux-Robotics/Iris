import cv2
from flask import Flask, Response
import util.config as constants
import display.pipeline

app = Flask(__name__)


def generate_frames():
    while True:
        frame = display.pipeline.process()
        if frame is None:
            break
        else:
            scale = frame.shape[0] // 720
            frame = cv2.resize(frame, dsize=(int(frame.shape[1] / scale), int(frame.shape[0] / scale)))
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                break

        # Convert the frame to bytes
        frame_bytes = buffer.tobytes()

        # Yield the frame as a response to the client
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/stream')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    start()
