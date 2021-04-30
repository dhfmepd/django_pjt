from django.urls import path
from django.contrib.auth import views as auth_views
from .views import base_views, utility_views, interface_views

app_name = 'common'

urlpatterns = [
    path('main/', base_views.main, name='main'),
    path('login/', base_views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', base_views.signup, name='signup'),
    path('file/upload/<str:ref_type>/<int:ref_id>/', utility_views.file_upload, name='file_upload'),
    path('file/download/<int:file_id>/', utility_views.file_download, name='file_download'),
    path('file/delete/<int:file_id>/', utility_views.file_delete, name='file_delete'),
    path('data/receive/', interface_views.data_receive, name='data_receive'),
]