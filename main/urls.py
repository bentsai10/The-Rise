from django.urls import path, include
from . import views

urlpatterns = [
    path('home', views.index),
    path('login', views.login),
    path('process_login', views.process_login),
    path('apply', views.apply),
    path('process_apply', views.process_apply),
]