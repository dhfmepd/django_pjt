from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('file/upload/<str:ref_type>/<int:ref_id>/', views.file_upload, name='file_upload'),
    path('file/delete/<int:file_id>/', views.file_delete, name='file_delete'),
]