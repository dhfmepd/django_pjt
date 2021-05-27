from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from konlpy.tag import Okt

@login_required(login_url='common:login')

def analysis_nlp(request):
    """
    자연어 분석
    """
        # 라이브러리: https://konlpy-ko.readthedocs.io/ko/v0.4.3/
        # 설치: pip install konlpy
        # 라이브러리: https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
        # 설치: pip install JPype1-1.2.0-cp39-cp39-win_amd64.whl
        # JDK 8 설치(이슈) + JAVA_HOME 설정
    param_data = request.POST.get('param_data', '내용없음')
    print(param_data)
    if request.method == 'POST':
        okt = Okt()
        result = okt.pos(param_data, norm=True, stem=True, join=True)
        data_list = []
        for word in result:
            idx = word.find('/')
            if word[idx + 1:] in ['Noun']:
                data_list.append(word[:idx])

        param_data = {'param_data': param_data, 'data_list': data_list}
        return render(request, 'common/analysis_nlp.html', param_data)

    param_data = {'param_data': param_data}
    return render(request, 'common/analysis_nlp.html', param_data)