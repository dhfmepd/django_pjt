from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from common.models import Menu, File
from ..models import Board
from common.forms import FileForm

@login_required(login_url='common:login')
def list(request, menu_id):
    """
    Board 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    op = request.GET.get('op', 'a')  # 검색기준
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준
    count = request.GET.get('count', '10')  # 조회건수

    # 정렬
    if so == 'recommend':
        board_list = Board.objects.filter(menu=menu_id).annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        board_list = Board.objects.filter(menu=menu_id).annotate(num_reply=Count('reply')).order_by('-num_reply', '-create_date')
    else:  # recent
        board_list = Board.objects.filter(menu=menu_id).order_by('-create_date')

    if kw:
        if op == 'a':
            board_list = board_list.filter(
                Q(subject__icontains=kw) |  # 제목검색
                Q(content__icontains=kw)    # 내용검색
            ).distinct()
        elif op == 'b':
            board_list = board_list.filter(
                Q(subject__icontains=kw)    # 제목검색
            ).distinct()
        elif op == 'c':
            board_list = board_list.filter(
                Q(author__username__icontains=kw)  # Board 글쓴이검색
            ).distinct()
        elif op == 'd':
            board_list = board_list.filter(
                Q(reply__content__icontains=kw)    # Reply 내용검색
            ).distinct()
        else:
            board_list = board_list.filter(
                Q(reply__author__username__icontains=kw)  # Reply 글쓴이검색
            ).distinct()

    # 페이징처리
    paginator = Paginator(board_list, count)
    page_obj = paginator.get_page(page)

    menu = Menu.objects.get(id=menu_id)

    context = {'board_list': page_obj, 'page': page, 'kw': kw, 'so': so, 'op': op, 'count': count, 'menu': menu}
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
    
    # 조회수 증가
    board.hit_count += 1
    board.save()

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

    context = {'board': board, 'reply_list': page_obj, 'so': so, 'page': page, 'fileForm': fileForm, 'file_list': file_list, 'ref_type': 'board', 'ref_id': board.id}
    return render(request, 'board/board_detail.html', context)