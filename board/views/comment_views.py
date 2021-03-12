from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Board, Reply, Comment
from ..forms import CommentForm

@login_required(login_url='common:login')
def comment_create_board(request, board_id):
    """
    Board Comment 등록
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.board = board
            comment.save()
            return redirect('board:detail', board_id=board.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'board/comment_form.html', context)

@login_required(login_url='common:login')
def comment_modify_board(request, comment_id):
    """
    Board Comment 수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('board:detail', board_id=comment.board.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('board:detail', board_id=comment.board.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'board/comment_form.html', context)

@login_required(login_url='common:login')
def comment_delete_board(request, comment_id):
    """
    Board Comment 삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('board:detail', board_id=comment.board.id)
    else:
        comment.delete()
    return redirect('board:detail', board_id=comment.board.id)

@login_required(login_url='common:login')
def comment_create_reply(request, reply_id):
    """
    Reply Comment 등록
    """
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.reply = reply
            comment.save()
            return redirect('board:detail', board_id=comment.reply.board.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'board/comment_form.html', context)


@login_required(login_url='common:login')
def comment_modify_reply(request, comment_id):
    """
    Reply Comment 수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('board:detail', board_id=comment.reply.board.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('board:detail', board_id=comment.reply.board.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'board/comment_form.html', context)


@login_required(login_url='common:login')
def comment_delete_reply(request, comment_id):
    """
    Reply Comment 삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('board:detail', board_id=comment.reply.board.id)
    else:
        comment.delete()
    return redirect('board:detail', board_id=comment.reply.board.id)