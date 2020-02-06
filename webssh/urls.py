from django.urls import path
from .views import web_ssh


urlpatterns = [
    path("webterminal/", web_ssh, name='webssh'),
]