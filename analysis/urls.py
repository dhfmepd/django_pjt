from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('normal-exp/', views.normal_exp_analy, name='normal_exp_analy'),
]