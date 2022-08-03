from django.contrib import admin
from django.apps import apps

# custom action that calls the update_items method on each selected collection
from django.urls import reverse
from django.utils.safestring import mark_safe


def update_items(modeladmin, request, queryset):
    for collection in queryset:
        collection.update_items()
        # add success message
        modeladmin.message_user(request, f"Updated items for {collection.name}")


update_items.short_description = "Update items"


def update_item_palettes(modeladmin, request, queryset):
    for collection in queryset:
        collection.update_color_palettes()
        # add success message
        modeladmin.message_user(request, f"Updated color palettes for {collection.name}")


update_item_palettes.short_description = "Update item palettes"


class CollectionAdmin(admin.ModelAdmin):
    actions = [update_items, update_item_palettes]
    readonly_fields = ['palette']

    def palette(self, obj):
        return render_colors([c._hex for c in obj.colors.all()])


admin.site.register(apps.get_model('collex', 'Collection'), CollectionAdmin)


def update_palettes(modeladmin, request, queryset):
    for item in queryset:
        item.update_color_palette()
        # add success message
        modeladmin.message_user(request, f"Updated color palettes for {item.name}")


update_palettes.short_description = "Update color palette for selected item(s)"


def color_divs(hex_colors):
    divs = []
    for hex in hex_colors:
        divs.append(
            f'<div data-tooltip="{hex}" style="display:inline-block; background-color: {hex}; height: 2rem; width: 2rem;"></div>')
    return divs


def render_colors(hex_colors):
    divs = color_divs(hex_colors)
    return mark_safe(''.join(divs))


item_read_only_fields = ['preview', 'palette', 'removed_colors', 'extractable_colors', 'collection_colors',
                         'update_palette']


class ItemAdmin(admin.ModelAdmin):
    actions = [update_palettes]
    fields = ['collection', 'token_id', 'name'] + item_read_only_fields + ['description', 'metadata', 'tokenUri',
                                                                           'image', 'image_url']
    readonly_fields = item_read_only_fields

    def palette(self, obj):
        """
        render the color palette for the item
        wrapped with links to remove colors
        """
        colors = [item_color.color._hex for item_color in obj.itemcolor_set.filter(manually_removed=False)]
        divs = color_divs(colors)
        output = []
        for i, div in enumerate(divs):
            url = reverse('collex:item_color_remove',
                          kwargs={'item_id': obj.id, 'hex': colors[i].split('#')[1]})
            output.append(f'<a href="{url}">{div}</a>')
        return mark_safe(''.join(output))

    def removed_colors(self, obj):
        """
        render colors that have been manually removed
        wrapped with links to un-remove them
        """
        colors = [color.color._hex for color in obj.itemcolor_set.filter(manually_removed=True)]
        divs = color_divs(colors)
        output = []
        for i, div in enumerate(divs):
            url = reverse('collex:item_color_unremove',
                          kwargs={'item_id': obj.id, 'hex': colors[i].split('#')[1]})
            output.append(f'<a href="{url}">{div}</a>')
        return mark_safe(''.join(output))

    def preview(self, obj):
        """
        renders the image
        """
        return mark_safe(f'<img src="{obj.image.url}" width="300" />')

    def extractable_colors(self, obj):
        """
        renders colors that can be extracted from the item without any external matching
        wrapped with links to add each color to the collection
        """
        colors = obj.extract_colors(tolerance=7, limit=20)
        divs = color_divs(colors)
        output = []
        for i, div in enumerate(divs):
            url = reverse('collex:collection_color_add',
                          kwargs={'collection_id': obj.collection_id, 'hex': colors[i].split('#')[1]})
            output.append(f'<a href="{url}">{div}</a>')
        return mark_safe(''.join(output))

    def collection_colors(self, obj):
        """
        renders colors that have been added to the collection
        wrapped with links to add them to the item
        """
        colors = [color._hex for color in obj.collection.colors.all()]
        divs = color_divs(colors)
        output = []
        for i, div in enumerate(divs):
            url = reverse('collex:item_color_add',
                          kwargs={'item_id': obj.id, 'hex': colors[i].split('#')[1]})
            output.append(f'<a href="{url}">{div}</a>')
        return mark_safe(''.join(output))

    def update_palette(self, obj):
        """
        render a link to update the color palette for the item
        """
        url = reverse('collex:item_update_palette', kwargs={'item_id': obj.id})
        return mark_safe(f'<a href="{url}">Update Palette</a>')


admin.site.register(apps.get_model('collex', 'Item'), ItemAdmin)


# custom admin for Color
class ColorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'preview']

    def preview(self, obj):
        # render div using hex as background color
        return mark_safe(f'<div style="background-color: {obj._hex}; height: 1rem;"></div>')


admin.site.register(apps.get_model('collex', 'Color'), ColorAdmin)

# register all models
models = apps.get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
