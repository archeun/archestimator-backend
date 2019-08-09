from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'phases', views.PhaseViewSet)
router.register(r'estimates', views.EstimateViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'sub_activities', views.SubActivityViewSet)
# router.register(r'phase/<int:phaseId>/estimates/', views.PhaseViewSet.get_estimates)

app_name = 'estimator'
urlpatterns = [
    path('api/', include(router.urls)),
]
