from django.urls import path
from . import views

app_name = 'konlpy'

urlpatterns = [
    path('apiopen/', views.api_open, name='api_open'),
]