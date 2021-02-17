from django.urls import path

from .views import login, callback


app_name = 'jasmin_auth'

urlpatterns = [
    path('login/', login, name = 'login'),
    path('callback/', callback, name = 'callback'),
]
