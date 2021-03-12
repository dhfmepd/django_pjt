from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from ..models import Board

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