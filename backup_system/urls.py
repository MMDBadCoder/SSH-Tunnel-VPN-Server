from django.urls import path

from backup_system import views

urlpatterns = [
    path('download-backup/', views.download_backup, name='download-backup'),
    path('inject-backup/', views.backup_inject, name='inject-backup'),
    path('', views.backup_page, name='backup-page'),
]

