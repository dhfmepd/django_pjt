"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from common.views import base_views
from django.contrib import messages
from django.shortcuts import redirect

def protected_file(request, path, document_root=None):
    messages.error(request, "접근 불가")
    return redirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('common/', include('common.urls')),
    path('board/', include('board.urls')),
    path('analysis/', include('analysis.urls')),
    path('sample/', include('sample.urls')),
    path('', base_views.index, name='index'),  # '/' 에 해당되는 path
] + static(settings.UPLOAD_URL, protected_file, document_root=settings.UPLOAD_ROOT)
# DEBUG False 에 페이지 발동
handler404 = 'common.views.base_views.page_not_found'
admin.site.site_header = 'CJ ONE EXPENSE Admin'
admin.site.site_title = 'CJ ONE EXPENSE Admin Portal'
admin.site.index_title = 'Welcome to CJ ONE EXPENSE Admin Portal'