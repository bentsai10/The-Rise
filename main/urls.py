from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('home', views.home),
    path('login', views.login),
    path('process_login', views.process_login),
    path('register', views.register),
    path('process_register', views.process_register),
    path('verification', views.verify),
    path('process_verification', views.process_verification),
    path('resend_verification', views.resend_verification),
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
    path('load_discussion_banner', views.load_discussion_banner), 
    path('process_response_post', views.process_response_post),
    path('load_response/<int:num>/<int:num2>', views.load_responses), 
    path('load_response_banner', views.load_response_banner), 
    path('favorite_space/<int:num>', views.process_favorite_space),
    path('<int:num>/<str:lorem>', views.discussion_button_pressed),
    path('save_discussion/<int:num>', views.process_save_discussion),
    path('process_space_search', views.process_space_search),
    path('display_spaces', views.display_spaces),
    path('preview', views.preview)
]

handler404 = views.handler404
handler500 = views.handler500