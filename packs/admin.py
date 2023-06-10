from django.contrib import admin

from packs.models import Pack, TempUsageTraffic


@admin.action(description="Start pack")
def start_pack(modeladmin, request, queryset):
    for pack in queryset.all():
        pack.run_pack()


@admin.action(description="Finish pack")
def finish_pack(modeladmin, request, queryset):
    for pack in queryset.all():
        pack.finish()
        pack.create_usage_factor()


class PackAdmin(admin.ModelAdmin):
    actions = [start_pack, finish_pack]
    list_filter = ('started', 'finished')


admin.site.register(Pack, PackAdmin)


@admin.register(TempUsageTraffic)
class TempUsageTrafficAdmin(admin.ModelAdmin):
    pass
