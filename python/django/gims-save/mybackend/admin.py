from django.contrib import admin
from .models import MiscMessage, PhenoTypeLists, PhenoTypeCategory, InputTypes, HistoryCategory, HistoryLists, GeneLists, GeneCategory


class MiscMessageAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'type', 'content']


class ListsTypesAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc']


class PhenoTypeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'priority']


class GeneCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'priority']


class PhenoTypeListsAdmin(admin.ModelAdmin):
    list_display = ['category', 'type', 'name', 'desc', 'priority']


class HistoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'priority']


class HistoryListsAdmin(admin.ModelAdmin):
    list_display = ['category', 'type', 'name', 'desc', 'priority']


class GeneListsAdmin(admin.ModelAdmin):
    list_display = ['category', 'name',  'desc', 'priority']


admin.site.register(MiscMessage, MiscMessageAdmin)
admin.site.register(InputTypes, ListsTypesAdmin)
admin.site.register(PhenoTypeCategory, PhenoTypeCategoryAdmin)
admin.site.register(PhenoTypeLists, PhenoTypeListsAdmin)
admin.site.register(HistoryCategory, HistoryCategoryAdmin)
admin.site.register(HistoryLists, HistoryListsAdmin)
admin.site.register(GeneCategory, GeneCategoryAdmin)
admin.site.register(GeneLists, GeneListsAdmin)