# pylint: disable=ungrouped-imports,no-member

from django.contrib import admin

try:
    from docker_utils.admin import PortableModelAdmin as ModelAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin as ModelAdmin # pylint: disable=useless-import-alias

from .models import Vocabulary, List, ListItem

@admin.register(Vocabulary)
class VocabularyAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'definition',)

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected vocabularies'

    actions = ['export_objects',]

@admin.register(List)
class ListAdmin(ModelAdmin):
    list_display = ('name', 'vocabulary',)
    search_fields = ('name', 'description',)
    list_filter = ('vocabulary',)

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected lists'

    actions = ['export_objects',]

class ListItemTagFilter(admin.SimpleListFilter):
    title = 'tags'

    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        all_tags = []

        for list_item in ListItem.objects.all():
            for tag in list_item.tags:
                if (tag in all_tags) is False:
                    all_tags.append(tag)

        all_tags.sort()

        lookups_list = []

        for label in all_tags:
            lookups_list.append((label, label))

        return lookups_list

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(tags__contains=[self.value()])

@admin.register(ListItem)
class ListItemAdmin(ModelAdmin):
    list_display = ('name', 'value', 'member_of', 'item_type', 'tags',)
    search_fields = ('name', 'value', 'item_type', 'tags',)
    list_filter = ('member_of', 'item_type', ListItemTagFilter,)

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected list items'

    actions = ['export_objects',]
