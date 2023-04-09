from django.urls import path
from . import views

urlpatterns = [
    path('start/<int:pack_id>/', views.start_pack, name='user-start-pack'),
    path('putty/<int:pack_id>/', views.get_putty_shell_file, name='user-putty-cmd'),
    path('active/', views.all_active_packs, name='admin-active-packs'),
    path('', views.home_view, name='user-home')
]



