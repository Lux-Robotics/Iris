import cscore
from output.pipeline import process_image
from util.config import settings

camera = cscore.CvSource("cvsource", cscore.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
mjpeg_server: cscore.MjpegServer = None


def start():
    global mjpeg_server
    resx, resy = settings["http_stream"]["max_res"]
    camera.setResolution(resx, resy)
    mjpeg_server = cscore.MjpegServer("httpserver", 5801)
    mjpeg_server.setSource(camera)
    print("stream started")


def put_frame(img):
    camera.putFrame(img)


def get_frame():
    camera.putFrame(process_image(settings["http_stream"]["max_res"])[0])


def set_resolution(width, height):
    camera.setResolution(width, height)


if __name__ == "__main__":
    start()
