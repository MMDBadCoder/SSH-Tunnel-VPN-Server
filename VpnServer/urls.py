from django.urls import path, include

urlpatterns = [
    path('account/', include('accounting.urls')),
    path('payment/', include('payment.urls')),
    path('admin/', include('admin_panel.urls')),
    path('backup/', include('backup_system.urls')),
    path('pack/', include('packs.urls')),
    path('', include('accounting.urls')),
]
