from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='common:login')
def analysis_nlp(request):
    """
    자연어 분석
    """
    
    return render(request, 'common/analysis_nlp.html', {})
