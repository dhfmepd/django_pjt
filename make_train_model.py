import pandas as pd
import konlpy
from konlpy.tag import Okt
from keras.preprocessing.text import Tokenizer
import numpy as np
from tensorflow.keras import layers

#데이터 READ
#train data는 train, validation을 위한 데이터
train_data = pd.read_csv("./train_data.csv")
#test_data는 최종적으로 모델을 평가하기 위해 1번 사용되는 데이터
test_data = pd.read_csv("./test_data.csv")

#okt(open korean text) 트위터에서 만든 오픈소스 형태소 분석기
okt = Okt()

X_train = []
# train_data 적요를 X_train로 사용
for sentence in train_data['title']:
    temp_X = []
    temp_X = okt.morphs(sentence, stem=True) # 토큰화
#   temp_X = [word for word in temp_X if not word in stopwords] # 불용어 제거
    X_train.append(temp_X)

X_test = []
# test_data 적요를 X_test로 사용
for sentence in test_data['title']:
    temp_X = []
    temp_X = okt.morphs(sentence, stem=True)  # 토큰화
    #   temp_X = [word for word in temp_X if not word in stopwords] # 불용어 제거
    X_test.append(temp_X)
# 토큰화 진행하면 [['점심', '식대', '및' '커피' '값']] 이런식으로 단어로 분리

#토큰화 단어를 컴퓨터 인식할 수 있게 정수인코딩
# 단어 최대 갯수 35000개로 설정
max_words = 35000
tokenizer = Tokenizer(num_words = max_words)
tokenizer.fit_on_texts(X_train)

#X 값은 feature 즉 적요
X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

#y값 즉 라벨링값으로 들어갈 라벨을 컴퓨터가 보고 알 수 있도록 one-hot 인코딩 진행
#원 핫 인코딩은 https://wikidocs.net/22647 참고
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

for i in range(len(test_data['label'])):
    if test_data['label'].iloc[i] == 0:
        y_test.append([1, 0, 0, 0, 0, 0, 0])
    elif test_data['label'].iloc[i] == 1:
        y_test.append([0, 1, 0, 0, 0, 0, 0])
    elif test_data['label'].iloc[i] == 2:
        y_test.append([0, 0, 1, 0, 0, 0, 0])
    elif test_data['label'].iloc[i] == 3:
        y_test.append([0, 0, 0, 1, 0, 0, 0])
    elif test_data['label'].iloc[i] == 4:
        y_test.append([0, 0, 0, 0, 1, 0, 0])
    elif test_data['label'].iloc[i] == 5:
        y_test.append([0, 0, 0, 0, 0, 1, 0])
    elif test_data['label'].iloc[i] == 6:
        y_test.append([0, 0, 0, 0, 0, 0, 1])

y_train = np.array(y_train)
y_test = np.array(y_test)
#케라스 학습 모델 생성
#Sequential 레이어가 순차적으로 쌓이는 모델로 생성
model = Sequential()
#단계적으로 레이어 추가
#1. 임베딩 층(토큰의 갯수, 임베딩 차원)
#단어를 기하공간에 매핑할 수 있도록 백터화 시키는 작업
model.add(Embedding(max_words, 100))
#2. lstm 층
#128개 메모리 셀을 가진 LSTM 레이어 순환 신경망 알고리즘
model.add(LSTM(128))
#3. 전결합층 dense(출력 뉴런의 수, activation = 활성화 함수)
# 활성화 함수 : linear, sigmoid, relu, softmax .. 등
model.add(Dense(7, activation='softmax'))

#모델 컴파일 시 필요한 인자 optimizer, loss, metrics
#optimizer 딥러닝 네트워크가 신속, 정확하게 학습하도록하는 기법
#loss는 예측값과 실제값간의 차이를 표현한 수식
#metrics는 실제 화면상으로 출력되는 output(정확성)
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

#모델 학습 과정을 수행하는 함수 Fit (학습시킬 데이터 X_train, Y_train)
#epochs는 학습되는 횟수, batch_size는 학습시킬 군집 단위
#validation_split은 학습 시 데이터를 비율만큼 나눠 validation에 사용하겠다는 의미

history = model.fit(X_train, y_train, epochs=10, batch_size=10, validation_split=0.1)
# 학습시킨 모델로 예측 원했던 y값 평가
print("\n 테스트 정확도 : {:.2f}%".format(model.evaluate(X_test, y_test)[1]*100))
predict_labels = np.argmax(predict, axis=1)
original_labels = np.argmax(y_test, axis=1)
class_map_dict = { 0: '교통비', 1: '주유비', 2: '주차비', 3: '공과금', 4: '시장조사', 5: '수수료', 6 : '식대' }

pred_pre = np.vectorize(class_map_dict.get)(predict_labels)
pred_ori = np.vectorize(class_map_dict.get)(original_labels)

#데이터 200개만 확인
for i in range(200):
    print("경비 내용 : ", test_data['title'].iloc[i], "/\t 원래 라벨 : ", pred_ori[i], "/\t예측한 라벨 : ", pred_pre[i])

#모델 저장
model.save("model_name.h5")
