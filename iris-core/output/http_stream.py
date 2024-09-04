import cscore
from output.pipeline import process_image
from util.state import settings
import util.state as state

camera = cscore.CvSource("cvsource", cscore.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
mjpeg_server: cscore.MjpegServer = None


def start():
    global mjpeg_server
    resx, resy = settings.http_stream.max_res
    camera.setResolution(resx, resy)
    mjpeg_server = cscore.MjpegServer("httpserver", 1180)
    mjpeg_server.setSource(camera)
    state.logger.info("Started Camera Stream")


def get_frame():
    camera.putFrame(process_image(settings.http_stream.max_res)[0])


def set_resolution(width, height):
    camera.setResolution(width, height)


if __name__ == "__main__":
    start()
