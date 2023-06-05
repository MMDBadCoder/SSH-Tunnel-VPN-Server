from django.urls import path
from . import views

urlpatterns = [
    # this url is for raw use of idpay, app is not synced by idpay, we only set this url in idpay
    # setting to get webhook of payment, nothing more
    path('webhook/<str:pay_key>/', views.webhook, name='idpay-webhook'),
    path('buy/<int:pack_days>/', views.buy_pack, name='user-buy-pack'),
    path('pay/<int:factor_id>/', views.pay_factor, name='user-pay-factor'),
]
