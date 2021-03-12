from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Board, Reply
from .forms import BoardForm, ReplyForm

def index(request):
    """
    Board 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')

    # 조회
    board_list = Board.objects.order_by('-create_date')
    # 페이징처리
    paginator = Paginator(board_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'board_list': page_obj}
    return render(request, 'board/board_list.html', context)

def detail(request, board_id):
    """
    Board 상세 출력
    """
    board = get_object_or_404(Board, pk=board_id)
    context = {'board': board}
    return render(request, 'board/board_detail.html', context)

@login_required(login_url='common:login')
def board_create(request):
    """
    Board 등록
    """
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.author = request.user
            board.create_date = timezone.now()
            board.save()
            return redirect('board:index')
    else:
        form = BoardForm()
    context = {'form': form}
    return render(request, 'board/board_form.html', context )

@login_required(login_url='common:login')
def board_modify(request, board_id):
    """
    Board 질문수정
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.user != board.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('board:detail', board_id=board.id)

    if request.method == "POST":
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            board = form.save(commit=False)
            board.author = request.user
            board.modify_date = timezone.now()  # 수정일시 저장
            board.save()
            return redirect('board:detail', board_id=board.id)
    else:
        form = BoardForm(instance=board)
    context = {'form': form}
    return render(request, 'board/board_form.html', context)

@login_required(login_url='common:login')
def board_delete(request, board_id):
    """
    Board 질문삭제
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.user != board.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('board:detail', board_id=board.id)
    board.delete()
    return redirect('board:index')

@login_required(login_url='common:login')
def reply_create(request, board_id):
    """
    Board 답변등록
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
    Board 답변수정
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
    Board 답변삭제
    """
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user != reply.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        reply.delete()
    return redirect('board:detail', board_id=reply.board.id)