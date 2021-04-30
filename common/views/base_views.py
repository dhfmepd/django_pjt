from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from board.models import Board, Comment, Reply
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
                                    'children': leaf_menu_list})
        # 1 Level 추가
        root_menu_list.append({'id': root_menu.id,
                               'title': root_menu.title,
                               'children': child_menu_list})
    return root_menu_list

def login(request):
    if request.method == 'POST':
        # data는 forms.form 두번쨰 인자이므로 data = 은 생략 가능
        form = AuthenticationForm(request, data = request.POST) # 먼저 request 인자를 받아야함
        if form.is_valid():
            # 메뉴정보 세션저장
            request.session['menu_list'] = get_menu_list()

            # 세션 CREATE/ form.get_user는 User 객체 반환
            auth_login(request, form.get_user())
            return redirect('common:main') # 로그인 성공시 메인페이지 이동
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'common/login.html', context)

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
    pie_label = []
    pie_data = []
    user_a_label = ''
    user_b_label = ''
    user_a_data = []
    user_b_data = []

    user_sub_qset = User.objects.filter(
        id=OuterRef("author")
    )
    pie_qset = Board.objects.values('author').annotate(
        label=Subquery(user_sub_qset.values('username')[:1]),
        data=Count('id'),
    ).order_by('-data')

    for pie_dset in pie_qset:
        pie_label.append(pie_dset['label'])
        pie_data.append(pie_dset['data'])

    bar_qset = Board.objects.values('author').annotate(
        label=Subquery(user_sub_qset.values('username')[:1]),
        b_cnt=Count('id'),
        c_cnt=Coalesce(Subquery(
            Comment.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values(
                'count')), 0),
        r_cnt=Coalesce(Subquery(
            Reply.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values(
                'count')), 0),
    )

    for bar_dset in bar_qset:
        # 테스트 용으로 2,3위 선택
        if bar_dset['author'] == 4:
            user_a_label = bar_dset['label']
            user_a_data.append(bar_dset['b_cnt'])
            user_a_data.append(bar_dset['c_cnt'])
            user_a_data.append(bar_dset['r_cnt'])

        if bar_dset['author'] == 5:
            user_b_label = bar_dset['label']
            user_b_data.append(bar_dset['b_cnt'])
            user_b_data.append(bar_dset['c_cnt'])
            user_b_data.append(bar_dset['r_cnt'])

    context = {'pie_label': pie_label, 'pie_data': pie_data, 'user_a_label': user_a_label, 'user_b_label': user_b_label,
               'user_a_data': user_a_data, 'user_b_data': user_b_data, 'menu_list': Menu.objects.all()}
    return render(request, 'common/main.html', context)

def page_not_found(request, exception):
    """
    404 Page not found
    """
    print('=========================404=========================')
    return render(request, 'common/404.html', {})