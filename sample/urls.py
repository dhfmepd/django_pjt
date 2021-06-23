from django.urls import path
from . import views

app_name = 'sample'

urlpatterns = [
    path('api/open/', views.api_open, name='api_open'),
    path('email/send/', views.email_send, name='email_send'),
]