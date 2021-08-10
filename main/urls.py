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
    path('edit_profile', views.edit_profile),
    path('process_edit_profile', views.process_edit_profile),
    path('logout', views.logout), 
    path('review', views.review_redir),
    path('review/<int:num>', views.review),
    path('process_approve', views.process_approve),
    path('my_profile', views.my_profile), 
    path('profile/<int:num>', views.profile), 
    path('process_discussion_post', views.process_discussion_post),
    path('spaces', views.add_space), 
    path('process_add_space', views.process_add_space),
    path('<int:network>/<int:space>', views.space), 
    path('load_discussion_banner', views.load_discussion_banner)
]