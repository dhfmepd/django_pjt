from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from konlpy.tag import Okt

@login_required(login_url='common:login')

def analysis_nlp(request):
    """
    자연어 분석
    """
    context = request.POST.get('context', '내용없음')
    if request.method == 'POST':
        okt = Okt()
        result = okt.pos(context, norm=True, stem=True, join=True)
        data_list = []
        for word in result:
            idx = word.find('/')
            if word[idx + 1:] in ['Noun']:
                data_list.append(word[:idx])

        context = {'context': context, 'data_list': data_list}
        return render(request, 'sample/api_open.html', context)

    context = {'context': context}
    return render(request, 'common/analysis_nlp.html', {})
