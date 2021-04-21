import os
import urllib
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from board.models import Board, Comment, Reply
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from common.models import File
from common.forms import UserForm, FileForm
from django.contrib import messages

def index(request):
    """
    Home 출력
    """
    context = {'question_list': ''}
    return render(request, 'common/index.html', context)

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

def page_not_found(request, exception):
    """
    404 Page not found
    """
    return render(request, 'common/404.html', {})

@login_required(login_url='common:login')
def dashboard(request):
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
    return render(request, 'common/dashboard.html', context)


@login_required(login_url='common:login')
def file_upload(request, ref_type, ref_id):
    """
    파일 업로드
    """
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = File(file_data=request.FILES['file_data'])
            file.file_name = request.FILES['file_data'].name
            file.ref_type = ref_type
            file.ref_id = ref_id
            file.create_date = timezone.now()
            file.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, '파일업로드가 유효하지 않습니다.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='common:login')
def file_delete(request, file_id):
    """
    파일 삭제
    """
    file = get_object_or_404(File, pk=file_id)
    file.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='common:login')
def file_download(request, file_id):
    """
    파일 다운로드
    """
    file = get_object_or_404(File, pk=file_id)
    if os.path.exists(file.file_data.path):
        file_name = urllib.parse.quote(file.file_name.encode('utf-8'))
        with open(file.file_data.path, 'rb') as fl:
            response = HttpResponse(fl, content_type='Application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % file_name
            return response
    else:
        messages.error(request, '파일이 존재하지 않습니다.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
