from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from common.models import Menu
from ..models import Board

@login_required(login_url='common:login')
def list(request, menu_id):
    """
    Board 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        board_list = Board.objects.filter(menu=menu_id).annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        board_list = Board.objects.filter(menu=menu_id).annotate(num_reply=Count('reply')).order_by('-num_reply', '-create_date')
    else:  # recent
        board_list = Board.objects.filter(menu=menu_id).order_by('-create_date')

    if kw:
        board_list = board_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(reply__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(board_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    menu = Menu.objects.get(id=menu_id)

    context = {'board_list': page_obj, 'page': page, 'kw': kw, 'so': so, 'menu': menu}
    return render(request, 'board/board_list.html', context)

@login_required(login_url='common:login')
def detail(request, board_id):
    """
    Board 상세 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    so = request.GET.get('so', 'recent')  # 정렬기준

    # 조회
    board = get_object_or_404(Board, pk=board_id)

    # 정렬
    if so == 'recommend':
        reply_list = board.reply_set.all().annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    else:  # recent
        reply_list = board.reply_set.all().order_by('-create_date')

    paginator = Paginator(reply_list, 5)  # 페이지당 5개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'board': board, 'reply_list': page_obj, 'so': so}
    return render(request, 'board/board_detail.html', context)