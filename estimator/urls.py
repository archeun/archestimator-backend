from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'resources', views.ResourceViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'phases', views.PhaseViewSet)
router.register(r'estimates', views.EstimateViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'sub_activities', views.SubActivityViewSet)
router.register(r'activity_work_entries', views.ActivityWorkEntriesViewSet)
router.register(r'sub_activity_work_entries', views.SubActivityWorkEntriesViewSet)

app_name = 'estimator'
urlpatterns = [
    path('api/', include(router.urls)),
]
