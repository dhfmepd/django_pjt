from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from ..models import Board, Reply
from ..forms import ReplyForm
from common.models import File
from common.forms import FileForm

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
            return redirect('{}#reply_{}'.format(
                resolve_url('board:detail', board_id=board.id), reply.id))

    # 입력 파라미터
    page = request.POST.get('page', '1')  # 페이지
    so = request.POST.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        reply_list = board.reply_set.all().annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    else:  # recent
        reply_list = board.reply_set.all().order_by('-create_date')

    paginator = Paginator(reply_list, 5)  # 페이지당 5개씩 보여주기
    page_obj = paginator.get_page(page)

    # 첨부파일 Modal 폼
    fileForm = FileForm()
    # 첨부파일 목록
    file_list = File.objects.filter(ref_type='board', ref_id=board.id).order_by('-create_date')

    context = {'board': board, 'reply_list': page_obj, 'so': so, 'fileForm': fileForm, 'file_list': file_list,
               'ref_type': 'board', 'ref_id': board.id, 'form': form}
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
            return redirect('{}#reply_{}'.format(
                resolve_url('board:detail', board_id=reply.board.id), reply.id))
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