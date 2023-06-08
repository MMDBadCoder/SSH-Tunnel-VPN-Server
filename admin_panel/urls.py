from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('active-packs/', views.active_packs, name='admin-active-packs'),
    path('reboot/', views.reboot, name='admin-reboot'),
    path('migrate/', views.migrate, name='admin-migrate'),
    path('service-restart/', views.service_restart, name='admin-service-restart'),
    path('', views.admin_panel_page, name='admin-panel')
]
