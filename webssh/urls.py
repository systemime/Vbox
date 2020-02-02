from django.urls import path
from .views import web_terminal


urlpatterns = [
    path("webterminal/", web_terminal, name='webterminal'),
]