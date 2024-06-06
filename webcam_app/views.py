from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, HttpResponse
import cv2
import atexit
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

camera = None  # Initially, the camera is not opened


def init_camera():
    global camera
    if camera is None or not camera.isOpened():
        logger.debug("Initializing camera...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            logger.error("Could not start camera.")
            raise RuntimeError("Could not start camera.")
        logger.debug("Camera initialized.")


def release_camera():
    global camera
    if camera is not None and camera.isOpened():
        logger.debug("Releasing camera...")
        camera.release()
        camera = None
        logger.debug("Camera released.")


def gen_frames():
    while True:
        if camera is None or not camera.isOpened():
            logger.debug("Camera is not opened or has been released.")
            break
        success, frame = camera.read()  # read the camera frame
        if not success:
            logger.error("Failed to read frame from camera.")
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                logger.error("Failed to encode frame to JPEG.")
                break
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def index(request):
    streaming = request.session.get("streaming", False)
    return render(request, "webcam_app/index.html", {"streaming": streaming})


def video_feed(request):
    streaming = request.session.get("streaming", False)
    if streaming:
        init_camera()
        return StreamingHttpResponse(
            gen_frames(), content_type="multipart/x-mixed-replace; boundary=frame"
        )
    else:
        return HttpResponse("Streaming is stopped.")


def capture(request):
    init_camera()
    success, frame = camera.read()  # type: ignore
    if success:
        filename = "captured_frame.jpg"
        cv2.imwrite(filename, frame)
        return redirect("index")  # Redirect to the index view after capturing
    else:
        return HttpResponse("Failed to capture frame", status=500)


def start_stream(request):
    request.session["streaming"] = True
    init_camera()
    return redirect("index")


def stop_stream(request):
    request.session["streaming"] = False
    release_camera()
    return redirect("index")


def cleanup_camera():
    release_camera()


atexit.register(cleanup_camera)
