from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from board.models import Board, Comment, Reply
from django.db.models import F, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from konlpy.tag import Okt

def chart_js(request):
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
        c_cnt=Coalesce(Subquery(Comment.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
        r_cnt=Coalesce(Subquery(Reply.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
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

    context = {'pie_label': pie_label, 'pie_data': pie_data, 'user_a_label': user_a_label, 'user_b_label': user_b_label, 'user_a_data': user_a_data, 'user_b_data': user_b_data}
    return render(request, 'sample/chart_js.html', context)

def api_open(request):
    #라이브러리: https://konlpy-ko.readthedocs.io/ko/v0.4.3/
    #설치: pip install konlpy
    #라이브러리: https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
    #설치: pip install JPype1-1.2.0-cp39-cp39-win_amd64.whl
    #JDK 8 설치(이슈) + JAVA_HOME 설정
    txt = '미팅 후 점심식사(오동욱 외 3인)'
    okt = Okt()
    result = okt.pos(txt, norm=True, stem=True, join=True)
    for word in result:
        idx = word.find('/')
        if word[idx+1:] in ['Noun']:
            print(word[:idx])

    context = {'result': result}
    return render(request, 'sample/api_open.html', context)