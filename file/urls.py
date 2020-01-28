from django.urls import path
from django.conf.urls import url
from .views import show_file_upload

urlpatterns = [
    path('show_file_update', show_file_upload, name='show_file_update')
]