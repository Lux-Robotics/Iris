import uvicorn
import asyncio
import cv2

from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer
from util.config import settings, logger
import output.pipeline


web = WebGear(skip_generate_webdata=True)


async def generate_frames():
    while True:
        try:
            frame, scale = output.pipeline.process_image(settings.http_stream.max_res)
            if frame is None:
                break
            else:
                # Encode the frame in JPEG format
                encode_param = [
                    int(cv2.IMWRITE_JPEG_QUALITY),
                    settings.http_stream.quality,
                ]
                ret, buffer = cv2.imencode(".jpg", frame, encode_param)

            # Convert the frame to bytes
            if ret:
                encoded_img = buffer.tobytes()

                # Yield the frame as a response to the client
                yield (
                    b"--frame\r\nContent-Type:image/jpeg\r\n\r\n"
                    + encoded_img
                    + b"\r\n"
                )
                await asyncio.sleep(0)
        except Exception as e:
            logger.exception(e)


def start():
    web.config["generator"] = generate_frames
    uvicorn.run(web(), host="0.0.0.0", port=5800)


if __name__ == "__main__":
    start()
