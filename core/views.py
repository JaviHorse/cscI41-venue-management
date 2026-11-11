from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
