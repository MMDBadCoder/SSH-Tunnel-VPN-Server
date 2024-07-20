from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from admin_panel.models import GiftPack, HomeMessage
from packs.models import Pack


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


class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'email', 'is_active')
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


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
