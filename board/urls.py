from django.urls import path

from . import views

app_name = 'board'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:board_id>/', views.detail, name='detail'),
    path('board/create/', views.board_create, name='board_create'),
    path('board/modify/<int:board_id>/', views.board_modify, name='board_modify'),
    path('board/delete/<int:board_id>/', views.board_delete, name='board_delete'),
    path('reply/create/<int:board_id>/', views.reply_create, name='reply_create'),
    path('reply/modify/<int:reply_id>/', views.reply_modify, name='reply_modify'),
    path('reply/delete/<int:reply_id>/', views.reply_delete, name='reply_delete'),
]