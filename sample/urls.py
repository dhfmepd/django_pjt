from django.urls import path
from . import views

app_name = 'sample'

urlpatterns = [
    path('api/open/', views.api_open, name='api_open'),
    path('email/send/', views.email_send, name='email_send'),
    path('ora/conn/', views.ora_conn, name='ora_conn'),
    path('data/labeling/', views.data_labeling, name='data_labeling'),
]