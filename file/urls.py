from django.urls import path
from django.conf.urls import url
from .views import File_upload

urlpatterns = [
    path('file_upload/', File_upload.as_view(), name='file_upload'),
    # path('file_list/', xxxx, name='file_list')
]