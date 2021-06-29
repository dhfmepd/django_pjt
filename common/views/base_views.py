from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from board.models import Board
from common.models import Menu
from common.forms import UserForm

def get_menu_list():
    # 메뉴구조 0~2 Level로 구성
    menu_list = Menu.objects.filter(level=0).order_by('sort_no')

    root_menu_list = []
    # 1 Level 리스트
    for root_menu in menu_list:
        child_menu_list = []
        # 2 Level 리스트
        for child_menu in root_menu.children.all():
            leaf_menu_list = []
            # 3 Level 리스트
            for leaf_menu in child_menu.children.all():
                leaf_menu_list.append({'id': leaf_menu.id,
                                       'title': leaf_menu.title,
                                       'level': leaf_menu.level,
                                       'url': leaf_menu.url,
                                       'argument': leaf_menu.argument})
            # 2 Level 추가
            child_menu_list.append({'id': child_menu.id,
                                    'title': child_menu.title,
                                    'icon': child_menu.icon,
                                    'children': leaf_menu_list})
        # 1 Level 추가
        root_menu_list.append({'id': root_menu.id,
                               'title': root_menu.title,
                               'children': child_menu_list})
    return root_menu_list

def signup(request):
    """
    계정생성
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render(request, 'common/index.html')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

def index(request):
    """
    Home 출력
    """
    if request.user.is_authenticated == True:
        return redirect('common:main')

    context = {}
    return render(request, 'common/index.html', context)

@login_required(login_url='common:login')
def main(request):
    """
    Dashboard 출력
    """
    # 1. Menu List 설정
    menu_list = request.session.get('menu_list')

    if menu_list is None:
        request.session['menu_list'] = get_menu_list()

    # 2. ReceiveHistory 처리(차트포함)
    top_info = get_top_info()
    chart_list = get_chart_info()

    bar_label = []
    c_bar_data = []
    e_bar_data = []

    if top_info is not None:
        c_total_count = '{:,}'.format(top_info[0])
        e_total_count = '{:,}'.format(top_info[1])
        last_create_date = top_info[2]
        text_analy_rate = top_info[3]
    else:
        c_total_count = '{:,}'.format(0)
        e_total_count = '{:,}'.format(0)
        last_create_date = 'N/A'
        text_analy_rate = '0'

    for r_idx, chart_info in enumerate(chart_list):
        bar_label.append(chart_info[0])
        c_bar_data.append(str(chart_info[1]))
        e_bar_data.append(str(chart_info[2]))

    # 3. 공지사항 Board 조회
    board_list = Board.objects.filter(menu='1').order_by('-create_date')
    paginator = Paginator(board_list, 5)
    page_obj = paginator.get_page(1)

    context = {'c_total_count': c_total_count, 'e_total_count': e_total_count, 'last_create_date': last_create_date, 'text_analy_rate': text_analy_rate,
               'board_list': page_obj, 'bar_label': bar_label, 'c_bar_data': c_bar_data, 'e_bar_data': e_bar_data}

    return render(request, 'common/main.html', context)

def get_top_info():
    sql_str = "SELECT TMP.c_total_count "
    sql_str += "     , TMP.e_total_count "
    sql_str += "     , TMP.last_create_date "
    sql_str += "     , ROUND(IFNULL(TMP.e_ml_fin_count / TMP.e_total_count, 0), 0) AS e_ml_fin_rate "
    sql_str += "  FROM ( "
    sql_str += "	SELECT (SELECT COUNT(1) FROM EX_CORPCARD_ASK) AS c_total_count "
    sql_str += "		 , (SELECT COUNT(1) FROM EX_EXPN_ETC) AS e_total_count "
    sql_str += "		 , (SELECT MAX(create_date) FROM common_receivehistory) AS last_create_date "
    sql_str += "         , (SELECT COUNT(1) FROM EX_EXPN_ETC WHERE LABEL_CATE_CD IS NOT NULL) AS e_ml_fin_count "
    sql_str += "	  FROM DUAL) TMP "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_chart_info():
    sql_str = "SELECT A.KEY_YM "
    sql_str += "    , IFNULL((SELECT COUNT(1) FROM EX_CORPCARD_ASK WHERE IF_DH BETWEEN A.FROM_DATE AND A.TO_DATE), 0) AS C_COUNT "
    sql_str += "    , IFNULL((SELECT COUNT(1) FROM EX_EXPN_ETC WHERE IF_DH BETWEEN A.FROM_DATE AND A.TO_DATE), 0) AS E_COUNT "
    sql_str += "FROM ( "
    sql_str += "	SELECT DATE_FORMAT(NOW(), '%Y-%m') AS KEY_YM, LAST_DAY(NOW() - INTERVAL 1 MONTH) + INTERVAL 1 DAY AS FROM_DATE, LAST_DAY(NOW()) AS TO_DATE "
    sql_str += "	UNION ALL "
    sql_str += "	SELECT DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH), '%Y-%m') AS KEY_YM, LAST_DAY(NOW() - INTERVAL 2 MONTH) + INTERVAL 1 DAY AS FROM_DATE, LAST_DAY(NOW() - INTERVAL 1 MONTH) AS TO_DATE "
    sql_str += "	UNION ALL "
    sql_str += "	SELECT DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 2 MONTH), '%Y-%m') AS KEY_YM, LAST_DAY(NOW() - INTERVAL 3 MONTH) + INTERVAL 1 DAY AS FROM_DATE, LAST_DAY(NOW() - INTERVAL 2 MONTH) AS TO_DATE "
    sql_str += ") A "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def page_not_found(request, exception):
    """
    404 Page not found
    """
    print('=========================404=========================')
    return render(request, 'common/404.html', {})