from django.urls import path
from django.contrib.auth import views as auth_views
from .views import base_views, utility_views, interface_views, analysis_view, expense_view

app_name = 'common'

urlpatterns = [
    path('main/', base_views.main, name='main'),
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', base_views.signup, name='signup'),
    path('file/upload/<str:ref_type>/<int:ref_id>/', utility_views.file_upload, name='file_upload'),
    path('file/download/<int:file_id>/', utility_views.file_download, name='file_download'),
    path('file/delete/<int:file_id>/', utility_views.file_delete, name='file_delete'),
    path('interface/ora/', interface_views.interface_ora, name='interface_ora'),
    path('analysis/nlp/', analysis_view.analysis_nlp, name='analysis_nlp'),
    path('analysis/ocr/', analysis_view.analysis_ocr, name='analysis_ocr'),
    path('popup/image/', analysis_view.popup_image, name='popup_image'),
]