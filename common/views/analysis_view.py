import pandas as pd
import numpy as np
from django.db import connection
from konlpy.tag import Okt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

@login_required(login_url='common:login')
def analysis_nlp(request):
    #예측 실행 버튼 클릭 시 타는 구문
    if request.method == 'POST':

        sql_str = "SELECT ECAL_NO, SEQ, DTLS, LABEL_CATE_CD FROM EX_EXPN_ETC WHERE LABEL_CATE_CD IS NULL"
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
                    cursor.fetchall()
                connection.commit()
            data_list.append(predict_labels[i])
        connection.close()

        context = {'data_list': data_list}
        return render(request, 'common/analysis_nlp.html', context)

    return render(request, 'common/analysis_nlp.html', {})