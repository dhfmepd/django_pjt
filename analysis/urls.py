from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('exp/corp/', views.corp_exp_analy, name='corp_exp_analy'),
    path('exp/normal/', views.normal_exp_analy, name='normal_exp_analy'),
    path('exp/etc/', views.etc_exp_analy, name='etc_exp_analy'),
    path('ocr/receipt/', views.receipt_ocr, name='receipt_ocr'),
]