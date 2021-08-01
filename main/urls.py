from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('home', views.home),
    path('login', views.login),
    path('process_login', views.process_login),
    path('apply', views.apply),
    path('process_apply', views.process_apply),
    path('verification', views.verification),
    path('process_verification', views.process_verification),
    path('add_about', views.add_about),
    path('process_edit_profile', views.process_edit_profile),
    path('logout', views.logout), 
    path('review', views.review_redir),
    path('review/<int:num>', views.review),
    path('process_approve', views.process_approve)

]