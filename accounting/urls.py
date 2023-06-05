from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    path('sign-up/', views.signup_view, name='user-sign-up'),
    path('', views.home_view, name='user-home')
]
