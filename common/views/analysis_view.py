from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from konlpy.tag import Okt

@login_required(login_url='common:login')

def analysis_nlp(request):
    param_data = request.POST.get('param_data', '내용없음')

    if request.method == 'POST':
        print(param_data)
        okt = Okt()
        result = okt.pos(param_data, norm=True, stem=True, join=True)
        data_list = []
        for word in result:
            idx = word.find('/')
            if word[idx + 1:] in ['Noun']:
                data_list.append(word[:idx])
        print(data_list)
        if not data_list:
            print('error')
        param_data = {'param_data': param_data, 'data_list': data_list}
        return render(request, 'common/analysis_nlp.html', param_data)

    param_data = {'param_data': param_data}
    return render(request, 'common/analysis_nlp.html', param_data)