from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'phases', views.PhaseViewSet)

app_name = 'estimator'
urlpatterns = [
    path('api/', include(router.urls)),
]
