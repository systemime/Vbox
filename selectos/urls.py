from django.urls import path
from .views import Selectos, delete_user_deployment

urlpatterns = [
    path('select/', Selectos.as_view(), name='select'),
    path('delete_user_deployment/', delete_user_deployment, name='delete_user_deployment'),
]
