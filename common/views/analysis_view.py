import io
import os
import cv2
import pandas as pd
import numpy as np
from enum import Enum
from django.db import connection
from konlpy.tag import Okt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from google.cloud import vision
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model


@login_required(login_url='common:login')
def analysis_nlp(request):
    param_data = request.POST.get('param_data', '내용없음')

    #예측 실행 버튼 클릭 시 타는 구문
    if request.method == 'POST':

        sql_str = "SELECT ECAL_NO, SEQ, DTLS, LABEL_CATE_CD FROM EX_EXPN_ETC"
        # ECAL_NO : 전표번호, SEQ : 순서, DTLS : 적요, LABEL_CATE_CD : 라벨링
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            rows = cursor.fetchall()
            print(list(rows))

        # 모델 만들었던 학습 데이터 Read
        # train data는 train, validation을 위한 데이터
        train_data = pd.read_csv("./train_data.csv")

        # Database에 적요를 test_data로 선정
        # test_data는 최종적으로 모델을 평가하기 위해 1번 사용되는 데이터
        test_data = rows

        # 전표번호, 순서, 적요, 라벨링을 Pandas dataframe 생성(데이터 처리 및 분석 용이)
        df_test = pd.DataFrame(test_data, columns = ['number', 'seq', 'title', 'label'])

        # train, test 셋 토큰화
        # okt(open korean text) 트위터에서 만든 오픈소스 형태소 분석기
        okt = Okt()
        X_train = []
        # train_data 적요를 X_train로 사용
        for sentence in train_data['title']:
            temp_X = []
            temp_X = okt.morphs(sentence, stem=True)  # 토큰화
            #   temp_X = [word for word in temp_X if not word in stopwords] # 불용어 제거
            X_train.append(temp_X)

        # test_data 적요를 X_test로 사용
        X_test = []
        for sentence in df_test['title']:
            temp_X = []
            temp_X = okt.morphs(sentence, stem=True)
            X_test.append(temp_X)

        #최대 단어 갯수 35000개
        # 토큰화 단어를 컴퓨터 인식할 수 있게 정수인코딩
        max_words = 35000
        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(X_train)
        # X 값은 feature 즉 적요 내용
        X_train = tokenizer.texts_to_sequences(X_train)
        X_test = tokenizer.texts_to_sequences(X_test)

        # y값 즉 라벨링값으로 들어갈 라벨을 컴퓨터가 보고 알 수 있도록 one-hot 인코딩 진행
        # 원 핫 인코딩은 https://wikidocs.net/22647 참고

        # y값(라벨) 담을 리스트 선언
        y_train = []
        y_test = []

        #train_data 라벨을 원 핫 인코딩 진행
        for i in range(len(train_data['label'])):
            if train_data['label'].iloc[i] == 0:
                y_train.append([1, 0, 0, 0, 0, 0, 0])
            elif train_data['label'].iloc[i] == 1:
                y_train.append([0, 1, 0, 0, 0, 0, 0])
            elif train_data['label'].iloc[i] == 2:
                y_train.append([0, 0, 1, 0, 0, 0, 0])
            elif train_data['label'].iloc[i] == 3:
                y_train.append([0, 0, 0, 1, 0, 0, 0])
            elif train_data['label'].iloc[i] == 4:
                y_train.append([0, 0, 0, 0, 1, 0, 0])
            elif train_data['label'].iloc[i] == 5:
                y_train.append([0, 0, 0, 0, 0, 1, 0])
            elif train_data['label'].iloc[i] == 6:
                y_train.append([0, 0, 0, 0, 0, 0, 1])

        y_train = np.array(y_train)

        max_len = 20  # 전체 데이터의 길이를 20로 맞춘다(문장 길이)
        X_train = pad_sequences(X_train, maxlen=max_len)
        X_test = pad_sequences(X_test, maxlen=max_len)
        # 저장한 모델 불러오기
        model = load_model("model_name.h5")
        # 모델 예측하기
        predict = model.predict(X_test)
        # 라벨 예측(0~6)
        predict_labels = np.argmax(predict, axis=1)

        # class_map_dict = {0: '교통비', 1: '주유비', 2: '주차비', 3: '공과금', 4: '시장조사', 5: '수수료', 6: '식대'}

        data_list = []
        # 전체 데이터 루프 돌면서 라벨 예측
        for i in range(len(df_test['number'])):
            # 전표 번호
            ecal_number = str(df_test['number'][i])
            # 전표 번호 순서
            ecal_seq = str(df_test['seq'][i])
            # 적요 예측 라벨
            ecal_info_label = str(predict_labels[i])
            # 라벨이 None값인 경우 update
            if df_test['label'][i] is None:
                with connection.cursor() as cursor:
                    sql_update = "UPDATE EX_EXPN_ETC SET LABEL_CATE_CD = \'" + ecal_info_label + "\' WHERE ECAL_NO = \'" + ecal_number + "\' AND SEQ = \'" + ecal_seq + "\'"
                    cursor.execute(sql_update)
                    rows = cursor.fetchall()
                connection.commit()
            data_list.append(predict_labels[i])
        connection.close()

        param_data = {'param_data': param_data, 'data_list': data_list}
        return render(request, 'common/analysis_nlp.html', param_data)

    param_data = {'param_data': param_data}
    return render(request, 'common/analysis_nlp.html', param_data)

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
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/cjfvdtpjt/projects/dtpjt/VisionAPI/key.json"

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