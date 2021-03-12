from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Board
from .forms import BoardForm, ReplyForm

def index(request):
    """
    Board 목록 출력
    """
    board_list = Board.objects.order_by('-create_date')
    context = {'board_list': board_list}
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
