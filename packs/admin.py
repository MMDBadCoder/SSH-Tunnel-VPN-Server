from django.contrib import admin

from packs.models import Pack, UsageTraffic


@admin.action(description="Start pack")
def start_pack(modeladmin, request, queryset):
    for pack in queryset.all():
        pack.run_pack()


@admin.action(description="Finish pack")
def finish_pack(modeladmin, request, queryset):
    for pack in queryset.all():
        pack.finish()


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    actions = [start_pack, finish_pack]
    list_display = ('user', 'days', 'get_started_from', 'get_human_readable_usage', 'started', 'finished')
    list_filter = ('started', 'finished')


@admin.register(UsageTraffic)
class TempUsageTrafficAdmin(admin.ModelAdmin):
    list_display = ('pack', 'get_human_readable_usage', 'get_user')
    list_filter = ['committed']
