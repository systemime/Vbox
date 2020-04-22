from django.urls import path
from .views import monitor

urlpatterns = [
    path('', monitor, name='monitor')
]
