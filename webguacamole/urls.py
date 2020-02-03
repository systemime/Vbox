from django.urls import path
from . import views


app_name = "webguacamole"
urlpatterns = [
    path('terminal/<int:pod_id>', views.terminal, name='terminal'),  # webvnc页面
    # http://127.0.0.1/webguacamole/terminal/
]
