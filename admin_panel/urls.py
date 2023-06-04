from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adtive-packs/', views.active_packs, name='admin-active-packs'),
    path('', views.admin_panel_page, name='admin-panel')
]
