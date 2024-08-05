from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Sum

from admin_panel.models import GiftPack, HomeMessage, MigrateServer
from packs.models import Pack
from payment.models import ManualPaymentReport, WebhookReports, Credit


@admin.action(description="Grant gifts")
def grant_gifts(modeladmin, request, queryset):
    for gift in queryset.all():
        if gift.all_users:
            users = User.objects.filter(is_active=True)
        elif gift.active_users:
            users = []
            for pack in Pack.get_active_packs():
                users.append(pack.user)
        else:
            users = []
        for user in users:
            Pack.objects.create(user=user, days=gift.days, free_traffic=gift.free_traffic, label=gift.title)


class GiftPackAdmin(admin.ModelAdmin):
    actions = [grant_gifts]


admin.site.register(GiftPack, GiftPackAdmin)


@admin.register(HomeMessage)
class HomeMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(MigrateServer)
class MigrateServerAdmin(admin.ModelAdmin):
    list_display = ('server_host', 'server_ssh_port', 'server_ssh_username', 'server_ssh_password', 'get_logs_url')


class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'email', 'is_active', 'get_credit', 'get_sum_of_payments')
    list_filter = ['is_active']
    search_fields = ('first_name', 'email')
    ordering = ['first_name']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def get_sum_of_payments(self, obj):
        manual_amount = ManualPaymentReport.objects.filter(user=obj).aggregate(Sum('amount'))
        manual_amount = manual_amount['amount__sum'] if manual_amount['amount__sum'] is not None else 0
        web_amount = WebhookReports.objects.filter(mail=obj.email).aggregate(Sum('amount'))
        web_amount = web_amount['amount__sum'] if web_amount['amount__sum'] is not None else 0
        total_amount = int(manual_amount + web_amount / 10)
        return f'{total_amount:,}'

    get_sum_of_payments.short_description = 'All Payments'

    def get_credit(self, obj):
        return f'{Credit.get_credit(obj):,}'

    get_credit.short_description = 'Credit'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
