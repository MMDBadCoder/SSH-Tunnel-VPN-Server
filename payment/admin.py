from django.contrib import admin

from payment.models import Credit, PaymentFactor, WebhookReports


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentFactor)
class PaymentFactorAdmin(admin.ModelAdmin):
    pass


@admin.register(WebhookReports)
class WebhookReportAdmin(admin.ModelAdmin):
    pass
