from django.urls import path
from django.conf.urls import url
from .views import login, logout, Registered, profile, index, bash_info

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout', logout, name='logout'),
    path('registered/', Registered.as_view(), name='registered'),
    path('profile/', profile, name='profile'),
    path('index/', index, name='index'),
    path('bash_info/', bash_info, name='bash_info'),  # 异步加载信息传递方案
]
