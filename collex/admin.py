from django.contrib import admin
from django.apps import apps


# custom action that calls the update_items method on each selected collection
def update_items(modeladmin, request, queryset):
    for collection in queryset:
        collection.update_items()
        # add success message
        modeladmin.message_user(request, f"Updated items for {collection.name}")


update_items.short_description = "Update items"


# custom admin for Collection model
class CollectionAdmin(admin.ModelAdmin):
    actions = [update_items]


# register the models with the admin
admin.site.register(apps.get_model('collex', 'Collection'), CollectionAdmin)


# register all models
models = apps.get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
