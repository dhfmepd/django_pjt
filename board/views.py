from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Board
from .forms import BoardForm, ReplyForm
from django.core.paginator import Paginator

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

def board_create(request):
    """
    Board 등록
    """
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.create_date = timezone.now()
            board.save()
            return redirect('board:index')
    else:
        form = BoardForm()
    context = {'form': form}
    return render(request, 'board/board_form.html', context )

def reply_create(request, board_id):
    """
    Board 답변등록
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.create_date = timezone.now()
            reply.board = board
            reply.save()
            return redirect('board:detail', board_id=board.id)
    else:
        form = ReplyForm()
    context = {'board': board, 'form': form}
    return render(request, 'board/board_detail.html', context)
