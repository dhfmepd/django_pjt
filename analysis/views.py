import io
import os
import cv2
from enum import Enum
from google.cloud import vision
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required(login_url='common:login')
def normal_exp_analy(request):
    """
    일반/법인카드 경비분석 Dashboard
    """
    # 2.  1.Top10 Chart
    top10_list = get_top10_list()

    top10_label = []
    top10_data = []
    top10_sum = 0

    for r_idx, top10_info in enumerate(top10_list):
        top10_label.append(top10_info[0])
        top10_data.append(str(top10_info[1]))
        top10_sum += int(top10_info[1])

    top10_sum = '{:,}'.format(top10_sum)

    # 3. 2.평균 지출 Chart
    year_Avg = get_yearAvg_info()
    month_Sum = get_monSum_info()

    avg_data = [int(year_Avg[0]), int(month_Sum[0])]

    # 4. 3.월별 경비 증감 Chart
    monthly_label = []
    monthly_data = []
    monthly_list = get_monthly_list()

    for r_idx, monthly_info in enumerate(monthly_list):
        monthly_label.append(monthly_info[0])
        monthly_data.append(int(monthly_info[1]))

    # 4. 4. 전년, 전월 비교
    monthly_year_label = []
    monthly_year_data = []
    monthly_year_list = get_monthly_year_list()

    for r_idx, monthly_year_info in enumerate(monthly_year_list):
        monthly_year_label.append(monthly_year_info[0])
        monthly_year_data.append(int(monthly_year_info[1]))

    context = {'top10_label': top10_label, 'top10_data': top10_data, 'top10_sum': top10_sum, 'avg_data': avg_data,
               'monthly_label': monthly_label, 'monthly_data': monthly_data,
               'monthly_year_label': monthly_year_label, 'monthly_year_data': monthly_year_data}

    return render(request, 'analysis/normal_exp_analy.html', context)

def get_top10_list():
    """
    경비 Category Top 10 SQL
    """
    sql_str = "SELECT dt.MCC_NM, TRUNCATE(dt.APV_SUM_AMT, 0) "
    sql_str += "    FROM ( "
    sql_str += "        SELECT 	MCC_NM, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "            FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "        WHERE SEND_DIV = '01' "
    #sql_str += "            AND APV_DD BETWEEN '' AND ''"
    sql_str += "        GROUP BY MCC_CD, MCC_NM "
    sql_str += "    ) AS dt "
    sql_str += "ORDER BY dt.APV_SUM_AMT DESC "
    sql_str += "    LIMIT 10"

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_yearAvg_info():
    """
    경비 Category Trend Line SQL
    """
    sql_str = "SELECT IFNULL(ROUND(AVG(DT.APV_SUM_AMT), 0), 0) "
    sql_str += "    FROM ( "
    sql_str += "        SELECT 	SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "            FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "        WHERE SEND_DIV = '01' "
    sql_str += "            AND SLIP_YY = '2021' "
    sql_str += "        GROUP BY SUBSTR(APV_DD, 1, 6) "
    sql_str += "    ) AS DT "

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_monSum_info():
    """
    경비 Category Trend Line SQL
    """
    sql_str = "SELECT 	IFNULL(TRUNCATE(SUM(APV_SUM_AMT), 0), 0) AS APV_SUM_AMT "
    sql_str += "    FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "WHERE SEND_DIV = '01' "
    sql_str += "    AND SLIP_YY = '2021' "
    sql_str += "    AND APV_DD LIKE '202103%' "
    #sql_str += "    AND APV_DD LIKE DATE_FORMAT(SYSDATE(), '%Y%m')||'%' "

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row
def get_monthly_list():
    """
    경비 Monthly 증감 현황 SQL
    """
    sql_str = "SELECT 	SUBSTR(APV_DD, 1, 6) AS YEARMONTH, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "    FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "WHERE SEND_DIV = '01' "
    sql_str += "    AND APV_DD BETWEEN DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -3 MONTH), '%Y%m%01') AND DATE_FORMAT(SYSDATE(), '%Y%m%01') "
    sql_str += "GROUP BY SUBSTR(APV_DD, 1, 6) "

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_monthly_year_list():
    """
    경비 Year/Month 비교 SQL
    """
    sql_str = "SELECT DT.YEARMONTH, DT.APV_SUM_AMT FROM ( "
    sql_str += "SELECT 	SUBSTR(APV_DD, 1, 6) AS YEARMONTH, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "    FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "WHERE SEND_DIV = '01' "
    sql_str += "    AND APV_DD BETWEEN DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -3 MONTH), '%Y%m%01') AND DATE_FORMAT(DATE_FORMAT(SYSDATE(), '%Y%m%01') + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "GROUP BY SUBSTR(APV_DD, 1, 6) "
    sql_str += "UNION "
    sql_str += "SELECT 	SUBSTR(APV_DD, 1, 6) AS YEARMONTH, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "    FROM cjfv_oneexp.EX_CORPCARD_ASK "
    sql_str += "WHERE SEND_DIV = '01' "
    sql_str += "    AND APV_DD BETWEEN DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -12 MONTH), '%Y%m%01') AND DATE_FORMAT(DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -11 MONTH), '%Y%m%01') + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "GROUP BY SUBSTR(APV_DD, 1, 6) "
    sql_str += ") AS DT ORDER BY DT.YEARMONTH"

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

######################################## 기타경비 #########################################

@login_required(login_url='common:login')
def etc_exp_analy(request):
    """
    기타 경비분석 Dashboard
    """

    # 1. 예산 Chart
    budget_info = get_budget_info()

    if budget_info is not None:
        act_amt = '{:,}'.format(budget_info[0])
        use_amt = '{:,}'.format(budget_info[1])
        rem_amt = '{:,}'.format(budget_info[2])
        gol_amt = '{:,}'.format(budget_info[3])
    else:
        act_amt = '{:,}'.format(0)
        use_amt = '{:,}'.format(0)
        rem_amt = '{:,}'.format(0)
        gol_amt = '{:,}'.format(0)

    budget_data = [int(budget_info[0]), int(budget_info[1]), int(budget_info[3])]

    # 2. 부서상위 Top5 Chart
    top5_list = get_topcost_info()

    top5_label = []
    top5_data = []

    for r_idx, top5_info in enumerate(top5_list):
        top5_label.append(top5_info[1])
        top5_data.append(str(top5_info[2]))

    context = {'act_amt': act_amt, 'use_amt': use_amt, 'rem_amt': rem_amt, 'gol_amt': gol_amt,
               'budget_data': budget_data, 'top5_label': top5_label, 'top5_data': top5_data}

    return render(request, 'analysis/etc_exp_analy.html', context)

def get_budget_info():
    sql_str = "SELECT TRUNCATE(act_bud, 0) as act_amt, TRUNCATE(use_bud, 0) as use_amt, TRUNCATE(rem_bud, 0) as rem_amt, TRUNCATE(goal, 0) as gol_amt "
    sql_str += "  FROM cjfv_oneexp.EX_BUDGET "

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchone()

    return list

def get_topcost_info():
    """
    부서 상위 Top 5 SQL
    """
    sql_str = "	SELECT Z.CST_CENTR_CD,	"
    sql_str += " (SELECT CST.CST_CNTR_NM	"
    sql_str += "	          FROM EX_BS_CST_CNTR CST "
    sql_str += "			 WHERE CST.COM_CD = '1000'	"
    sql_str += "	           AND CST.CST_CNTR_CD = Z.CST_CENTR_CD) AS CST_CNTR_NM	"
    sql_str += "	     , IFNULL(ROUND(Z.TOT_AMT, 0), 0) AS TOT_AMT "
    sql_str += "	  FROM (	"
    sql_str += "			SELECT A.CST_CENTR_CD, A.TOT_AMT, RANK()OVER(ORDER BY A.TOT_AMT DESC) AS RANKING FROM	"
    sql_str += "	        (	SELECT TMP.CST_CENTR_CD, SUM(TMP.TOT_AMT) AS TOT_AMT FROM "
    sql_str += "		(	SELECT CST_CENTR_CD, APV_SUM_AMT AS TOT_AMT FROM EX_CORPCARD_ASK WHERE COM_CD = '1000' AND APV_DD LIKE '202104%' "
    sql_str += "			UNION ALL	"
    sql_str += "				SELECT CST_CENTR_CD, ECAL_AMT AS TOT_AMT FROM EX_EXPN_ETC WHERE COM_CD = '1000' AND OCCR_YMD LIKE '202104%' "
    sql_str += "				) TMP	"
    sql_str += "				GROUP BY TMP.CST_CENTR_CD "
    sql_str += "				    ) A	 "
    sql_str += "				   ) Z	"
    sql_str += "				 WHERE Z.RANKING <= 5	"

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

######################################## OCR #########################################

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

@login_required(login_url='common:login')
def receipt_ocr(request):
    # PIP Install : pip install --upgrade google-cloud-vision
    # WIN : set GOOGLE_APPLICATION_CREDENTIALS=C:\projects\mysite\VisionAPI\visionapitest-314407-3a69a466f455.json
    # LINUX : sudo nano ~/.profile -> export GOOGLE_APPLICATION_CREDENTIALS=/home/cjfvdtpjt/projects/dtpjt/VisionAPI/visionapitest-314407-3a69a466f455.json

    dir_path = "static/ocr/sample/"
    file_list = []

    # 샘플 파일리스트 불러오기
    dir_list = os.listdir(dir_path)
    for f_idx, file_name in enumerate(dir_list):
        file_list.append({'no': f_idx + 1,
                          'file_name': file_name,
                          'file_path': dir_path + file_name,
                          'size': os.path.getsize(dir_path + file_name),
                          'type': os.path.splitext(dir_path + file_name)[1][1:]})

    if request.method == 'POST':
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "VisionAPI/visionapitest-314407-3a69a466f455.json"

        image_path = request.POST.get('image_path')

        image = cv2.imread(image_path)
        infos = get_document_info(image_path, FeatureType.PARA)  # 단어 영역

        result_text = ""  # 화면 리턴 문구

        result_list = []

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
                    result_text += "[INFO] 1. 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"

                    if info.get('label_text') is None or info.get('label_text') == '':
                        result_list.append({'label': info.get('data_text') + ' (N/A)',
                                            'data': amt_str_to_num(info.get('data_text'))})
                    else:
                        result_list.append({'label': info.get('data_text') + ' (' + info.get('label_text') + ')',
                                            'data': amt_str_to_num(info.get('data_text'))})

                else:
                    cv2.rectangle(image,
                                  (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                                  (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                                  (255, 0, 0), 2)
                    result_text += "[INFO] 2. 시작점({}), 종료점({}), {} : {}".format(
                        (info.get('bounding_box').vertices[0].x, info.get('bounding_box').vertices[0].y),
                        (info.get('bounding_box').vertices[2].x, info.get('bounding_box').vertices[2].y),
                        info.get('label_text'),
                        info.get('data_text')) + "\n"

        image_name = image_path.split('/')[-1]
        temp_image_path = "static/ocr/temporary/"
        cv2.imwrite(os.path.join(temp_image_path, image_name), image)

        context = {'file_list': file_list, 'target_image': '/' + image_path,
                   'result_image': os.path.join(temp_image_path, image_name), 'result_list': result_list}
        return render(request, 'common/image_ocr.html', context)

    image_path = "/static/images/noimg.jpg"

    return render(request, 'common/image_ocr.html', {'file_list': file_list, 'target_image': image_path})


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


def amt_str_to_num(text):
    won_index = text.find('원')
    if won_index > 0:
        amt_text = text[0:won_index]
        amt_text = amt_text.replace(',', '')  # 숫자 변환을 위한 콤마 제거
        return amt_text

    return '0'
