import base64

from django.shortcuts import render
from django.contrib.auth.models import User
from board.models import Board, Comment, Reply
from django.db import connection
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
import cx_Oracle
from konlpy.tag import Okt
from django.core.mail import EmailMessage
import cv2
import pandas as pd
import numpy as np
import easyocr

def chart_js(request):
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
        c_cnt=Coalesce(Subquery(Comment.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
        r_cnt=Coalesce(Subquery(Reply.objects.filter(author=OuterRef("author")).values('author').annotate(count=Count('id')).values('count')), 0),
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

    context = {'pie_label': pie_label, 'pie_data': pie_data, 'user_a_label': user_a_label, 'user_b_label': user_b_label, 'user_a_data': user_a_data, 'user_b_data': user_b_data}
    return render(request, 'sample/chart_js.html', context)

def ora_conn(request):
    sql = request.POST.get('sql', 'SELECT 1 FROM DUAL')
    if request.method == 'POST':

        dsn = cx_Oracle.makedsn("52.2.142.63", "1525", "FVWQA")
        db = cx_Oracle.connect("fvsrm", "qwer!@", dsn)

        cursor = db.cursor()
        cursor.execute(sql)
        data_list = cursor.fetchall()

        cursor.close()
        db.close()

        context = {'sql': sql, 'data_list': data_list}
        return render(request, 'sample/ora_conn.html', context)

    context = {'sql': sql}
    return render(request, 'sample/ora_conn.html', context)

def sql_exec(request):
    sql = request.POST.get('sql', 'SELECT 1 FROM DUAL')
    if request.method == 'POST':
        try:
            cursor = connection.cursor()

            strSql = sql
            result = cursor.execute(strSql)
            data_list = cursor.fetchall()

            print(result)
            print(data_list)

            connection.commit()
            connection.close()
        except:
            connection.rollback()

        context = {'sql': sql, 'data_list': data_list}
        return render(request, 'sample/sql_exec.html', context)

    context = {'sql': sql}
    return render(request, 'sample/sql_exec.html', context)

def api_open(request):
    #라이브러리: https://konlpy-ko.readthedocs.io/ko/v0.4.3/
    #설치: pip install konlpy
    #라이브러리: https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
    #설치: pip install JPype1-1.2.0-cp39-cp39-win_amd64.whl
    #JDK 8 설치(이슈) + JAVA_HOME 설정

    context = request.POST.get('context', '내용없음')
    if request.method == 'POST':
        okt = Okt()
        result = okt.pos(context, norm=True, stem=True, join=True)
        data_list = []
        for word in result:
            idx = word.find('/')
            if word[idx+1:] in ['Noun']:
                data_list.append(word[:idx])

        context = {'context': context, 'data_list': data_list}
        return render(request, 'sample/api_open.html', context)

    context = {'context': context}
    return render(request, 'sample/api_open.html', context)

def image_ocr(request):
    #pip install easyocr

    if request.method == 'POST':
        crop_file = request.POST.get('crop_image')
        crop_file = crop_file[22:]

        image = open("static/images/sample.png", "wb")
        image.write(base64.b64decode(crop_file))
        image.close()

        reader = easyocr.Reader(['ko', 'en'])  # 한국어 인식할 때 ko 추가

        img = cv2.imread("static/images/sample.png")
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = np.ones((5, 5), np.uint8)
        open_img = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel)

        result_text = reader.readtext(open_img)

        # 로컬설정
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # result_text = pytesseract.image_to_string(open_img, lang="kor+eng")

        context = {'result_text': result_text}
        return render(request, 'sample/image_ocr.html', context)

    return render(request, 'sample/image_ocr.html', {})

def email_send(request):
    from_addr = request.POST.get('from_addr')
    to_addr = request.POST.get('to_addr')
    subject = request.POST.get('subject')
    content = request.POST.get('content')

    if request.method == 'POST':
        email = EmailMessage(
            subject,  # 제목
            content,  # 내용
            from_addr,  # 보내는 이메일 (settings에서 설정해서 작성안해도 됨)
            to=[to_addr],  # 받는 이메일 리스트
        )
        email.send()

        return render(request, 'sample/email_send.html', {})

    return render(request, 'sample/email_send.html', {})

def chart_sample(request):

    return render(request, 'sample/chart_sample.html', {})


def pandas_sample(request):
    data = {
        'year': [2016, 2017, 2018],
        'GDP rate': [2.8, 3.1, 3.0],
        'GDP': ['1.637M', '1.73M', '1.83M']
    }

    df = pd.DataFrame(data)
    df = df.to_html(classes='mystyle')

    return render(request, 'sample/pandas_sample.html', {'table': df})
