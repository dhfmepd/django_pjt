from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from konlpy.tag import Okt
import pandas as pd
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding, Dense, LSTM
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
import konlpy
from tensorflow.keras import layers
from tensorflow.keras.models import load_model

@login_required(login_url='common:login')

def analysis_nlp(request):
    param_data = request.POST.get('param_data', '내용없음')

    if request.method == 'POST':
        print(param_data)
        # 모델 만들었던 학습 데이터 및 신규 데이터 read
        train_data = pd.read_csv("./train_data.csv")
        test_data = pd.read_csv("./new_data3.csv")
        okt = Okt()
        X_train = []
        for sentence in train_data['title']:
            temp_X = []
            temp_X = okt.morphs(sentence, stem=True)  # 토큰화
            #   temp_X = [word for word in temp_X if not word in stopwords] # 불용어 제거
            X_train.append(temp_X)

        X_test = []
        for sentence in test_data['title']:
            temp_X = []
            temp_X = okt.morphs(sentence, stem=True)  # 토큰화
            #   temp_X = [word for word in temp_X if not word in stopwords] # 불용어 제거
            X_test.append(temp_X)
        max_words = 35000
        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(X_train)
        X_train = tokenizer.texts_to_sequences(X_train)
        X_test = tokenizer.texts_to_sequences(X_test)

        y_train = []
        y_test = []

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

        max_len = 20  # 전체 데이터의 길이를 20로 맞춘다
        X_train = pad_sequences(X_train, maxlen=max_len)
        X_test = pad_sequences(X_test, maxlen=max_len)
        # 저장한 모델 불러오기
        model = load_model("model_name.h5")

        predict = model.predict(X_test)

        predict_labels = np.argmax(predict, axis=1)

        class_map_dict = {0: '교통비', 1: '주유비', 2: '주차비', 3: '공과금', 4: '시장조사', 5: '수수료', 6: '식대'}
        pred_pred = np.vectorize(class_map_dict.get)(predict_labels)
        # 100개 데이터만 먼저 확인
        for i in range(10):
            print("경비 내용 : ", test_data['title'].iloc[i], "/\t예측한 라벨 : ", pred_pred[i])


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