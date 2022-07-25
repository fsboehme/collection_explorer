from django.views.generic import TemplateView

from collex.models import Collection


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['collection'] = Collection.objects.first()
        return context