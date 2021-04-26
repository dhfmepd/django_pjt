from django.urls import path
from . import views

app_name = 'sample'

urlpatterns = [
    path('chartjs/', views.chart_js, name='chart_js'),
    path('apiopen/', views.api_open, name='api_open'),
    path('oraconn/', views.ora_conn, name='ora_conn'),
    path('sqlexec/', views.sql_exec, name='sql_exec'),
    path('imageocr/', views.image_ocr, name='image_ocr'),
    path('emailsend/', views.email_send, name='email_send'),
]