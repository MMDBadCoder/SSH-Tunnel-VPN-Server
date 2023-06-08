from django.contrib import admin
from django.contrib.auth.models import User

from admin_panel.models import GiftPack, HomeMessage
from packs.models import Pack


# Register your models here.
@admin.action(description="Grant gifts")
def grant_gifts(modeladmin, request, queryset):
    for gift in queryset.all():
        if gift.all_users:
            users = User.objects.filter(is_active=True)
        elif gift.active_users:
            users = []
            for pack in Pack.objects.filter(started=True, finished=False):
                users.append(pack.user)
        else:
            users = []
        for user in users:
            Pack.objects.create(user=user, days=gift.days, free_traffic=gift.free_traffic, label=gift.label)


class GiftPackAdmin(admin.ModelAdmin):
    actions = [grant_gifts]


admin.site.register(GiftPack, GiftPackAdmin)


@admin.register(HomeMessage)
class HomeMessageAdmin(admin.ModelAdmin):
    pass
