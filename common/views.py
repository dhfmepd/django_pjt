from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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
            return redirect('board:detail', board_id=ref_id)
        else:
            messages.error(request, '파일 업로드가 유효하지 않습니다.')

    return redirect('board:detail', board_id=ref_id)
