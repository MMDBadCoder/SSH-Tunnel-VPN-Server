from django.contrib import admin

from payment.models import Credit, PaymentFactor, WebhookReports, ManualPaymentReport


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_reminded_credit_pretty', 'user', 'payment_factor',
                    'webhook_report', 'manual_payment', 'is_last_credit')
    ordering = ['-id']
    list_filter = ['user', 'is_last_credit']


@admin.register(PaymentFactor)
class PaymentFactorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_human_readable_pay_amount', 'pay_for', 'related_pack', 'payed')


@admin.register(WebhookReports)
class WebhookReportAdmin(admin.ModelAdmin):
    pass


@admin.register(ManualPaymentReport)
class ManualPaymentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_amount_pretty')
    list_filter = ['user']
