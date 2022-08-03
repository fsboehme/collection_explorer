from django.urls import path

from collex.views import Home, CollectionColorAddView, ItemColorAddView, ItemColorRemoveView, ItemColorUnemoveView, \
    ItemUpdatePaletteView

app_name = 'collex'
urlpatterns = [
    path(r'', Home.as_view(), name='home'),
    # add color to collection
    path(r'collection/<int:collection_id>/colors/add/<str:hex>', CollectionColorAddView.as_view(),
         name='collection_color_add'),
    # add color to item
    path(r'item/<int:item_id>/colors/add/<str:hex>', ItemColorAddView.as_view(),
         name='item_color_add'),
    # remove color from item
    path(r'item/<int:item_id>/colors/remove/<str:hex>', ItemColorRemoveView.as_view(),
         name='item_color_remove'),
    # unremove color from item
    path(r'item/<int:item_id>/colors/unremove/<str:hex>', ItemColorUnemoveView.as_view(),
         name='item_color_unremove'),
    # update color palette for item
    path(r'item/<int:item_id>/colors/update', ItemUpdatePaletteView.as_view(),
         name='item_update_palette'),
]
