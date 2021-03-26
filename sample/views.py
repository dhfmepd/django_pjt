from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from board.models import Board, Comment, Reply
from django.db.models import F, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce

def chart_js(request):
    pie_label = []
    pie_data = []
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
        b_cnt=Count('id'),
        c_cnt=Coalesce(Subquery(Comment.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
        r_cnt=Coalesce(Subquery(Reply.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
    )
    print(bar_qset)
    for bar_dset in bar_qset:
        if bar_dset['author'] == 1:
            user_a_data.append(bar_dset['b_cnt'])
            user_a_data.append(bar_dset['c_cnt'])
            user_a_data.append(bar_dset['r_cnt'])

        if bar_dset['author'] == 4:
            user_b_data.append(bar_dset['b_cnt'])
            user_b_data.append(bar_dset['c_cnt'])
            user_b_data.append(bar_dset['r_cnt'])

    print(user_a_data)
    print(user_b_data)

    context = {'pie_label': pie_label, 'pie_data': pie_data, 'user_a_data': user_a_data, 'user_b_data': user_b_data}
    return render(request, 'sample/chart_js.html', context)

def api_open(request):
    context = {'question_list': ''}
    return render(request, 'sample/api_open.html', context)