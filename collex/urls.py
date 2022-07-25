from django.urls import path

from collex.views import Home

urlpatterns = [
    path(r'', Home.as_view(), name='home')
]
