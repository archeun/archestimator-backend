from django.views import generic

from .models import *


class IndexView(generic.ListView):
    template_name = 'estimator/index.html'
    context_object_name = 'estimate_list'

    def get_queryset(self):
        return Estimate.objects.all()


class DetailView(generic.DetailView):
    model = Estimate
    template_name = 'estimator/estimation.html'
