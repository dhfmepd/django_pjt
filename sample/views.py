import io
import os
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
from google.cloud import vision
from enum import Enum

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

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def image_ocr(request):
    # PIP Install : pip install --upgrade google-cloud-vision
    # WIN : set GOOGLE_APPLICATION_CREDENTIALS=C:\projects\mysite\VisionAPI\visionapitest-314407-3a69a466f455.json
    # LINUX : sudo nano ~/.profile -> export GOOGLE_APPLICATION_CREDENTIALS=/home/cjfvdtpjt/projects/dtpjt/VisionAPI/visionapitest-314407-3a69a466f455.json

    if request.method == 'POST':
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/cjfvdtpjt/projects/dtpjt/VisionAPI/key.json"
        image_path = request.POST.get('image_path')

        image = cv2.imread(image_path)
        infos = get_document_info(image_path, FeatureType.PARA) # 단어 영역

        result_text = ""  # 화면 리턴 문구

        for info in infos:
            if find_amt_phrases(info.get('data_text')):
                avg_height = (int(info.get('bounding_box').vertices[2].y) - int(info.get('bounding_box').vertices[0].y)) / 2 + int(info.get('bounding_box').vertices[0].y)
                label_text = get_label_text(infos, avg_height)
                info['label_text'] = label_text

                if find_pay_phrases(info.get('label_text')):
                    cv2.rectangle(image, (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y), (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y), (0, 0, 255), 2)
                    result_text += "[INFO] 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"
                else:
                    cv2.rectangle(image, (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y), (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y), (255, 0, 0), 2)
                    result_text += "[INFO] 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"

        image_name = image_path.split('/')[-1]
        temp_image_path = "static/ocr_temp/"
        cv2.imwrite(os.path.join(temp_image_path, image_name), image)

        context = {'result_image': temp_image_path + image_name, 'result_text': result_text}
        return render(request, 'sample/image_ocr.html', context)

    return render(request, 'sample/image_ocr.html', {})

# 구글 비젼 API로 Full Text 데이터 추출
def get_document_info(image_file, feature):
    client = vision.ImageAnnotatorClient()

    infos = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    for page in document.pages:
        for block in page.blocks:
            block_text = ""
            for paragraph in block.paragraphs:
                paragraph_text = ""
                for word in paragraph.words:
                    word_text = ""
                    for symbol in word.symbols:
                        if (feature == FeatureType.BLOCK): # BLOCK 레벨 초기화 된 변수에 저장
                            block_text += symbol.text
                        elif (feature == FeatureType.PARA): # PARA 레벨 초기화 된 변수에 저장
                            paragraph_text += symbol.text
                        elif (feature == FeatureType.WORD): # WORD 레벨 초기화 된 변수에 저장
                            word_text += symbol.text

                        if (feature == FeatureType.SYMBOL):
                            infos.append({'bounding_box': symbol.bounding_box, 'data_text': symbol.text})
                    if (feature == FeatureType.WORD):
                        infos.append({'bounding_box': word.bounding_box, 'data_text': word_text})
                if (feature == FeatureType.PARA):
                    infos.append({'bounding_box': paragraph.bounding_box, 'data_text': paragraph_text})
            if (feature == FeatureType.BLOCK):
                infos.append({'bounding_box': block.bounding_box, 'data_text': block_text})

    return infos

# 라벨 텍스트 추출(평균 Y 좌표 기준으로 중복되는 영역에 해당)
def get_label_text(infos, value):
    label_text = ''

    for info in infos:
        if value > int(info.get('bounding_box').vertices[0].y) and value < int(info.get('bounding_box').vertices[2].y):
            if not find_amt_phrases(info.get('data_text')):
                if len(label_text) > 0:
                    label_text += ' ' + info.get('data_text')
                else:
                    label_text += info.get('data_text')

    return label_text


# ML을 통한 거래관련 문구 찾기(현재 임시처리)
def find_pay_phrases(text):
    print("[INFO] 거래문구 : {}".format(text))
    print("[INFO] 값 : {}".format(text.find('거래금액')))
    if text.find('거래금액') >= 0 :
        print("[INFO] 성공 : {}".format(text))
        return True

    if text.find('부가세') >= 0 or text.find('봉사료') >= 0 or text.find('캐시백') >= 0 or text.find('공급가액') >= 0:
        print("[INFO] 실패 : {}".format(text))
        return False

    return True

# ML을 통한 금액관련 문구 찾기(현재 임시처리)
# 현기준 원으로 끝나는 쉽표 제거한 숫자
def find_amt_phrases(text):
    #print("[TEST] 문구 1 : {}".format(text))
    if len(text) > 1:
        won_index = len(text) - 1
        #print("[TEST] 문구 2 : {}".format(won_index))
        if text.find('원') == won_index:
            try:
                amt_text = text[0:won_index] # 원 문구 제거
                amt_text = amt_text.replace(',', '') # 숫자 변환을 위한 콤마 제거
                amt_int = int(amt_text) # 숫자 변환
                # print("[TEST] 문구 3 : {}".format(amt_int))
                if amt_int is not None:
                    return True
            except ValueError:
                return False

    return False

# def image_ocr_bak(request):
#     # EasyOCR 설치 : pip install easyocr
#
#     if request.method == 'POST':
#         image_path = request.POST.get('image_path')
#         image = cv2.imread(image_path)
#         reader = easyocr.Reader(['ko', 'en'])  # 한국어 인식할 때 ko 추가
#         results = reader.readtext(image_path)
#
#         result_text = ""  # 화면 리턴 문구
#         amt_text_list = get_text_list(results)
#
#         for amt_text_dic in amt_text_list:
#             if find_pay_phrases(amt_text_dic.get('label_text')):
#                 cv2.rectangle(image, amt_text_dic['data_st_point'], amt_text_dic['data_ed_point'], (0, 0, 255), 2)
#             else:
#                 cv2.rectangle(image, amt_text_dic['data_st_point'], amt_text_dic['data_ed_point'], (255, 0, 0), 2)
#
#             result_text += "[INFO] 시작점({}), 종료점({}), {} : {}".format(amt_text_dic['data_st_point'],
#                                                                      amt_text_dic['data_ed_point'],
#                                                                      amt_text_dic.get('label_text'),
#                                                                      amt_text_dic.get('data_text')) + "\n"
#
#         image_name = image_path.split('/')[-1]
#         temp_image_path = "static/ocr_temp/"
#         cv2.imwrite(os.path.join(temp_image_path, image_name), image)
#
#         context = {'result_image': temp_image_path + image_name, 'result_text': result_text}
#         return render(request, 'sample/image_ocr.html', context)
#
#     return render(request, 'sample/image_ocr.html', {})

# 전체 텍스트 추출
# def get_text_list(results):
#     amt_text_list = []
#
#     for (bbox, text, prob) in results:
#         (tl, tr, br, bl) = bbox
#         tl = (int(tl[0]), int(tl[1]))
#         br = (int(br[0]), int(br[1]))
#
#         # 1. 전체 인식 Text 처리
#         # cv2.rectangle(image, tl, br, (0, 255, 0), 2)
#         print("[INFO] 시작점({}), 종료점({}), 일반문구 : {}".format(tl, br, text))
#
#         # 2. 금액문구(예: 콤마포함숫자 + 원)의 경우, 변수 적재
#         if find_amt_phrases(text):
#             avg_height = (int(br[1]) - int(tl[1])) / 2 + int(tl[1])
#             label_text = get_label_text(results, avg_height)
#             amt_text_list.append({'label_text': label_text, 'data_st_point': tl, 'data_ed_point': br, 'data_text': text})
#
#     return amt_text_list

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

def test_crontab_job():
    print('TEST !!!!')
# pip install django-crontab