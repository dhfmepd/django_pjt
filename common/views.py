from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone
from common.models import File
from common.forms import UserForm, FileForm
from django.views.decorators.csrf import csrf_exempt

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
            return redirect('common:file_upload', ref_type=ref_type, ref_id=ref_id)
    else:
        # 파일 목록 조회
        file_list = File.objects.filter(ref_type=ref_type, ref_id=ref_id).order_by('-create_date')
        form = FileForm()
    context = {'file_list': file_list, 'form': form, 'ref_type': ref_type, 'ref_id': ref_id}
    return render(request, 'common/file_upload.html', context)