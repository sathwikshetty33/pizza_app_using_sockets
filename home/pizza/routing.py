from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/pizza/<order_id>", OrderProgress.as_asgi()),
]