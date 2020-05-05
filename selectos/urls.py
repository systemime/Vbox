from django.urls import path
from .views import Selectos, delete_user_deployment, pod_num, remove_all

urlpatterns = [
    path('select/', Selectos.as_view(), name='select'),
    path('delete_user_deployment/', delete_user_deployment, name='delete_user_deployment'),
    path('get_pod_num/', pod_num, name='get_pod_num'),
    path('remove_all/', remove_all, name='remove_all_pod'),
]
