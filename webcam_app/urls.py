from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("video_feed/", views.video_feed, name="video_feed"),
    path("capture/", views.capture, name="capture"),
    path("start_stream/", views.start_stream, name="start_stream"),
    path("stop_stream/", views.stop_stream, name="stop_stream"),
]
