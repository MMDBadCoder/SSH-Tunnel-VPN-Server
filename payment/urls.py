from django.urls import path
from . import views

urlpatterns = [
    # this url is for raw use of idpay, app is not synced by idpay, we only set this url in idpay
    # setting to get webhook of payment, nothing more
    path('webhook/<str:pay_key>/', views.webhook, name='idpay-webhook'),
    path('new-pack/<int:pack_days>/', views.buy_new_pack, name='user-buy-new-pack'),
    path('pay-factor/<int:factor_id>/', views.pay_factor, name='user-pay-factor'),
]
