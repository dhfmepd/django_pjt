from django.urls import path

from .views import base_views, board_views, reply_views, comment_views, vote_views

app_name = 'board'

urlpatterns = [
    path('board/<int:menu_id>', base_views.list, name='list'),
    path('board/detail/<int:board_id>/', base_views.detail, name='detail'),
    path('board/create/<int:menu_id>', board_views.board_create, name='board_create'),
    path('board/modify/<int:board_id>/', board_views.board_modify, name='board_modify'),
    path('board/delete/<int:board_id>/', board_views.board_delete, name='board_delete'),
    path('reply/create/<int:board_id>/', reply_views.reply_create, name='reply_create'),
    path('reply/modify/<int:reply_id>/', reply_views.reply_modify, name='reply_modify'),
    path('reply/delete/<int:reply_id>/', reply_views.reply_delete, name='reply_delete'),
    path('comment/create/board/<int:board_id>/', comment_views.comment_create_board, name='comment_create_board'),
    path('comment/modify/board/<int:comment_id>/', comment_views.comment_modify_board, name='comment_modify_board'),
    path('comment/delete/board/<int:comment_id>/', comment_views.comment_delete_board, name='comment_delete_board'),
    path('comment/create/reply/<int:reply_id>/', comment_views.comment_create_reply, name='comment_create_reply'),
    path('comment/modify/reply/<int:comment_id>/', comment_views.comment_modify_reply, name='comment_modify_reply'),
    path('comment/delete/reply/<int:comment_id>/', comment_views.comment_delete_reply, name='comment_delete_reply'),
    path('vote/board/<int:board_id>/', vote_views.vote_board, name='vote_board'),
    path('vote/reply/<int:reply_id>/', vote_views.vote_reply, name='vote_reply'),
]