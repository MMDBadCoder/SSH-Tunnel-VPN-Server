from django.contrib import admin

from payment.models import Credit


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    pass
