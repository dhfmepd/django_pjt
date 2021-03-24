import os
import urllib
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
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
            return redirect('list')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

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
    file = get_object_or_404(File, pk=file_id)
    if os.path.exists(file.file_data.path):
        file_name = urllib.parse.quote(file.file_name.encode('utf-8'))
        with open(file.file_data.path, 'r', encoding='utf-8') as fl:
            response = HttpResponse(fl, content_type='Application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % file_name
            return response
    else:
        messages.error(request, '파일이 존재하지 않습니다.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
