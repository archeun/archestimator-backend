from django.urls import path

from . import views

app_name = 'estimator'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('/estimation/<int:estimation_id>/', views.DetailView.as_view(), name='detail'),
]