import io
import os
import cv2
from enum import Enum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision_v1 import types

@login_required(login_url='common:login')
def analysis_nlp(request):
    """
    자연어 분석
    """

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join('upload/2021/05/28/c0f3849c-cac7-43d1-97b6-e00d9310d4ea.jpg')

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    # response = client.label_detection(image=image)
    # labels = response.label_annotations

    response = client.text_detection(image=image)
    labels = response.text_annotations

    print('Labels:')
    for label in labels:
        print("[INFO description] {}".format(label.description))
        # print("[INFO bounding_poly] {}".format(label.bounding_poly)) # 좌표로 보임
        # print("[INFO confidence] {}".format(label.confidence))
        # print("[INFO locale] {}".format(label.locale))
        # print("[INFO locations] {}".format(label.locations))
        # print("[INFO mcls_data] {}".format(label.mcls_data))
        # print("[INFO mid] {}".format(label.mid))
        # print("[INFO properties] {}".format(label.properties))
        # print("[INFO oneof] {}".format(label.oneof))
        # print("[INFO oneof_index] {}".format(label.oneof_index))
        # print("[INFO topicality] {}".format(label.topicality))
        # print("[INFO score] {}".format(label.score))
        # print("[INFO parent] {}".format(label.parent))

        # types.image_annotator.EntityAnnotation.
    
    return render(request, 'common/analysis_nlp.html', {})

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

@login_required(login_url='common:login')
def analysis_ocr(request):
    # PIP Install : pip install --upgrade google-cloud-vision
    # WIN : set GOOGLE_APPLICATION_CREDENTIALS=C:\projects\mysite\VisionAPI\visionapitest-314407-3a69a466f455.json
    # LINUX : sudo nano ~/.profile -> export GOOGLE_APPLICATION_CREDENTIALS=/home/cjfvdtpjt/projects/dtpjt/VisionAPI/visionapitest-314407-3a69a466f455.json

    if request.method == 'POST':
        image_path = request.POST.get('image_path')

        image = cv2.imread(image_path)
        infos = get_document_info(image_path, FeatureType.PARA)  # 단어 영역

        result_text = ""  # 화면 리턴 문구

        for info in infos:
            if find_amt_phrases(info.get('data_text')):
                avg_height = (int(info.get('bounding_box').vertices[2].y) - int(
                    info.get('bounding_box').vertices[0].y)) / 2 + int(info.get('bounding_box').vertices[0].y)
                label_text = get_label_text(infos, avg_height)
                info['label_text'] = label_text

                if find_pay_phrases(info.get('label_text')):
                    cv2.rectangle(image,
                                  (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                                  (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                                  (0, 0, 255), 2)
                    result_text += "[INFO] 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"
                else:
                    cv2.rectangle(image,
                                  (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                                  (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                                  (255, 0, 0), 2)
                    result_text += "[INFO] 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"

        image_name = image_path.split('/')[-1]
        temp_image_path = "static/ocr_temp/"
        cv2.imwrite(os.path.join(temp_image_path, image_name), image)

        context = {'result_image': temp_image_path + image_name, 'result_text': result_text}
        return render(request, 'analysis/image_ocr.html', context)

    return render(request, 'analysis/image_ocr.html', {})

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
                        if (feature == FeatureType.BLOCK):  # BLOCK 레벨 초기화 된 변수에 저장
                            block_text += symbol.text
                        elif (feature == FeatureType.PARA):  # PARA 레벨 초기화 된 변수에 저장
                            paragraph_text += symbol.text
                        elif (feature == FeatureType.WORD):  # WORD 레벨 초기화 된 변수에 저장
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
        if value > int(info.get('bounding_box').vertices[0].y) and value < int(
                info.get('bounding_box').vertices[2].y):
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
    if text.find('거래금액') >= 0:
        print("[INFO] 성공 : {}".format(text))
        return True

    if text.find('부가세') >= 0 or text.find('봉사료') >= 0 or text.find('캐시백') >= 0 or text.find('공급가액') >= 0:
        print("[INFO] 실패 : {}".format(text))
        return False

    return True

# ML을 통한 금액관련 문구 찾기(현재 임시처리)
# 현기준 원으로 끝나는 쉽표 제거한 숫자
def find_amt_phrases(text):
    # print("[TEST] 문구 1 : {}".format(text))
    if len(text) > 1:
        won_index = len(text) - 1
        # print("[TEST] 문구 2 : {}".format(won_index))
        if text.find('원') == won_index:
            try:
                amt_text = text[0:won_index]  # 원 문구 제거
                amt_text = amt_text.replace(',', '')  # 숫자 변환을 위한 콤마 제거
                amt_int = int(amt_text)  # 숫자 변환
                # print("[TEST] 문구 3 : {}".format(amt_int))
                if amt_int is not None:
                    return True
            except ValueError:
                return False

    return False