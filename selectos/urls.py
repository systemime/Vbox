from django.urls import path
from .views import Selectos, delete_user_pod

urlpatterns = [
    path('select/', Selectos.as_view(), name='select'),
    path('delete_user_pod', delete_user_pod, name='delete_user_pod'),
]
