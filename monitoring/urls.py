from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitoring_page, name='admin-monitoring')
]
