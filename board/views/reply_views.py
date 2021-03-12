from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Board, Reply
from ..forms import ReplyForm

@login_required(login_url='common:login')
def reply_create(request, board_id):
    """
    Reply 등록
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.create_date = timezone.now()
            reply.board = board
            reply.save()
            return redirect('board:detail', board_id=board.id)
    else:
        form = ReplyForm()
    context = {'board': board, 'form': form}
    return render(request, 'board/board_detail.html', context)

@login_required(login_url='common:login')
def reply_modify(request, reply_id):
    """
    Reply 수정
    """
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user != reply.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('board:detail', board_id=reply.board.id)

    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.modify_date = timezone.now()
            reply.save()
            return redirect('board:detail', board_id=reply.board.id)
    else:
        form = ReplyForm(instance=reply)
    context = {'reply': reply, 'form': form}
    return render(request, 'board/reply_form.html', context)

@login_required(login_url='common:login')
def reply_delete(request, reply_id):
    """
    Reply 삭제
    """
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user != reply.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        reply.delete()
    return redirect('board:detail', board_id=reply.board.id)