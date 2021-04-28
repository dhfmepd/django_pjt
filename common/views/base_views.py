from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from board.models import Board, Comment, Reply
from common.forms import UserForm

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
               'user_a_data': user_a_data, 'user_b_data': user_b_data}
    return render(request, 'common/main.html', context)

def page_not_found(request, exception):
    """
    404 Page not found
    """
    print('=========================404=========================')
    return render(request, 'common/404.html', {})