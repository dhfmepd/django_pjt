from django.shortcuts import render

def normal_exp_analy(request):
    return render(request, 'analysis/normal_exp_analy.html', {})