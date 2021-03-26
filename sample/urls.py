from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'sample'

urlpatterns = [
    path('chartjs/', views.chart_js, name='chart_js'),
    path('apiopen/', views.api_open, name='api_open'),
]