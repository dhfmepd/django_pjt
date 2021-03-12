from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from ..models import Board, Reply

@login_required(login_url='common:login')
def vote_board(request, board_id):
    """
    Board Vote 등록
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.user == board.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        board.voter.add(request.user)
    return redirect('board:detail', board_id=board.id)

@login_required(login_url='common:login')
def vote_reply(request, reply_id):
    """
    Reply Vote 등록
    """
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user == reply.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        reply.voter.add(request.user)
    return redirect('board:detail', board_id=reply.board.id)