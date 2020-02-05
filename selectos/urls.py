from django.urls import path
from .views import Selectos, delete_user_deployment, pod_num

urlpatterns = [
    path('select/', Selectos.as_view(), name='select'),
    path('delete_user_deployment/', delete_user_deployment, name='delete_user_deployment'),
    path('get_pod_num/', pod_num, name='get_pod_num'),
]
