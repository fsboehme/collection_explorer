from django.views.generic import TemplateView, RedirectView

from collex.models import Collection, Item


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['collection'] = Collection.objects.first()
        return context


class CollectionColorAddView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        collection = Collection.objects.get(pk=kwargs['collection_id'])
        hex = kwargs['hex']
        collection.add_color(hex)
        return self.request.META.get('HTTP_REFERER')


class ItemColorAddView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        item = Item.objects.get(pk=kwargs['item_id'])
        hex = kwargs['hex']
        item.add_color(hex)
        return self.request.META.get('HTTP_REFERER')


class ItemColorRemoveView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        item = Item.objects.get(pk=kwargs['item_id'])
        hex = kwargs['hex']
        item.remove_color(hex)
        return self.request.META.get('HTTP_REFERER')


class ItemColorUnemoveView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        item = Item.objects.get(pk=kwargs['item_id'])
        hex = kwargs['hex']
        item.unremove_color(hex)
        return self.request.META.get('HTTP_REFERER')


class ItemUpdatePaletteView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        item = Item.objects.get(pk=kwargs['item_id'])
        item.update_color_palette()
        return self.request.META.get('HTTP_REFERER')