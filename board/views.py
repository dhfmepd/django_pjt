from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Board

def index(request):
    """
    Board 목록 출력
    """
    board_list = Board.objects.order_by('-create_date')
    context = {'board_list': board_list}
    return render(request, 'board/board_list.html', context)

def detail(request, board_id):
    """
    Board 내용 출력
    """
    board = get_object_or_404(Board, pk=board_id)
    context = {'board': board}
    return render(request, 'board/board_detail.html', context)

def reply_create(request, board_id):
    """
    Board 답변등록
    """
    board = get_object_or_404(Board, pk=board_id)
    board.reply_set.create(content=request.POST.get('content'), create_date=timezone.now())
    return redirect('board:detail', board_id=board.id)
