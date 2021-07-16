import io
import os
import cv2
from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.cloud import vision
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required(login_url='common:login')
def corp_exp_analy(request):
    """
    법인카드 경비분석 Dashboard
    """
    month = request.GET.get('month', (datetime.today() + relativedelta(months=-1)).strftime('%Y%m'))

    print("Target Month : ", month)

    # 1. 법인카드 Category Top 10
    top10_list = get_corp_cate_top10_list(month)

    top10_label = []
    top10_data = []
    top10_sum = 0

    for top10_info in top10_list:
        top10_label.append(top10_info[0])
        top10_data.append(str(top10_info[1]))
        top10_sum += int(top10_info[1])

    top10_sum_text = '{:,}'.format(top10_sum)

    # 2. 법인카드 Category Trend Line
    top10_trend_label = []
    top10_trend_data_label = []
    top10_trend_data_list = []
    top10_trend_data1 = []
    top10_trend_data2 = []
    top10_trend_data3 = []
    top10_trend_data4 = []
    top10_trend_data5 = []
    top10_trend_data6 = []
    top10_trend_data7 = []
    top10_trend_data8 = []
    top10_trend_data9 = []
    top10_trend_data10 = []
    top10_trend_list = get_corp_cate_trend_list(month)

    for r_idx, top10_trend_info in enumerate(top10_trend_list):

        if top10_trend_info[0] not in top10_trend_label:  # 월(X) 라벨
            top10_trend_label.append(top10_trend_info[0])

        if top10_trend_info[1] not in top10_trend_data_label:  # 데이터셋 라벨
            top10_trend_data_label.append(top10_trend_info[1])

        if r_idx % 10 == 0:
            top10_trend_data1.append(int(top10_trend_info[2]))
        if r_idx % 10 == 1:
            top10_trend_data2.append(int(top10_trend_info[2]))
        if r_idx % 10 == 2:
            top10_trend_data3.append(int(top10_trend_info[2]))
        if r_idx % 10 == 3:
            top10_trend_data4.append(int(top10_trend_info[2]))
        if r_idx % 10 == 4:
            top10_trend_data5.append(int(top10_trend_info[2]))
        if r_idx % 10 == 5:
            top10_trend_data6.append(int(top10_trend_info[2]))
        if r_idx % 10 == 6:
            top10_trend_data7.append(int(top10_trend_info[2]))
        if r_idx % 10 == 7:
            top10_trend_data8.append(int(top10_trend_info[2]))
        if r_idx % 10 == 8:
            top10_trend_data9.append(int(top10_trend_info[2]))
        if r_idx % 10 == 9:
            top10_trend_data10.append(int(top10_trend_info[2]))

    if len(top10_trend_data_label) == 10:
        top10_trend_data_list.append({'label': top10_trend_data_label[0], 'data': top10_trend_data1})
        top10_trend_data_list.append({'label': top10_trend_data_label[1], 'data': top10_trend_data2})
        top10_trend_data_list.append({'label': top10_trend_data_label[2], 'data': top10_trend_data3})
        top10_trend_data_list.append({'label': top10_trend_data_label[3], 'data': top10_trend_data4})
        top10_trend_data_list.append({'label': top10_trend_data_label[4], 'data': top10_trend_data5})
        top10_trend_data_list.append({'label': top10_trend_data_label[5], 'data': top10_trend_data6})
        top10_trend_data_list.append({'label': top10_trend_data_label[6], 'data': top10_trend_data7})
        top10_trend_data_list.append({'label': top10_trend_data_label[7], 'data': top10_trend_data8})
        top10_trend_data_list.append({'label': top10_trend_data_label[8], 'data': top10_trend_data9})
        top10_trend_data_list.append({'label': top10_trend_data_label[9], 'data': top10_trend_data10})

    # 3. 경비 Average and Now
    year_avg_info = get_corp_year_avg_info(month)
    month_sum_info = get_corp_month_sum_info(month)

    avg_data = [int(year_avg_info[0]), int(month_sum_info[0])]

    # 4. 경비 Monthly 증감 현황
    monthly_wave_label = []
    monthly_wave_data = []
    monthly_wave_list = get_corp_monthly_wave_list(month)

    for r_idx, monthly_wave_info in enumerate(monthly_wave_list):
        monthly_wave_label.append(monthly_wave_info[0])
        monthly_wave_data.append(int(monthly_wave_info[1]))

    # 5. 경비 Year/Month 비교
    ym_compare_label = []
    ym_compare_data = []
    ym_compare_list = get_corp_ym_compare_list(month)

    for r_idx, ym_compare_info in enumerate(ym_compare_list):
        ym_compare_label.append(ym_compare_info[0])
        ym_compare_data.append(int(ym_compare_info[1]))

    context = {'month': month, 'top10_label': top10_label, 'top10_data': top10_data, 'top10_sum_text': top10_sum_text,
               'top10_trend_label': top10_trend_label, 'top10_trend_data_list': top10_trend_data_list,
               'avg_data': avg_data, 'monthly_wave_label': monthly_wave_label, 'monthly_wave_data': monthly_wave_data,
               'ym_compare_label': ym_compare_label, 'ym_compare_data': ym_compare_data}

    return render(request, 'analysis/corp_exp_analy.html', context)

def get_corp_cate_top10_list(month):
    """
    법인카드 Category Top 10 SQL
    """
    sql_str = "SELECT RSLT.MCC_NM, IFNULL(ROUND(RSLT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT "
    sql_str += "  FROM ( "
    sql_str += "    SELECT BASE.DISP_CATE_CD "
    sql_str += "         , (SELECT detail_code_name "
    sql_str += "              FROM common_code "
    sql_str += "             WHERE group_code = 'C002' "
    sql_str += "               AND detail_code = BASE.DISP_CATE_CD "
    sql_str += "               AND use_flag = 1) AS MCC_NM "
    sql_str += "         , BASE.APV_SUM_AMT "
    sql_str += "      FROM "
    sql_str += "    ( "
    sql_str += "            SELECT DISP_CATE_CD, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "              FROM EX_CORPCARD_ASK "
    sql_str += "             WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "               AND APV_DD LIKE CONCAT('" + month + "', '%') "
    sql_str += "             GROUP BY DISP_CATE_CD "
    sql_str += "    ) BASE "
    sql_str += ") RSLT "
    sql_str += "ORDER BY RSLT.APV_SUM_AMT DESC "
    sql_str += "LIMIT 10 "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_corp_cate_trend_list(month):
    """
    법인카드 Category Trend Line SQL
    """
    sql_str = "SELECT BASE.APV_YM, BASE.MCC_NM, IFNULL(ROUND(RSLT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT FROM "
    sql_str += "( "
    sql_str += "    SELECT RANG.APV_YM "
    sql_str += "         , NRNK.DISP_CATE_CD "
    sql_str += "         , (SELECT detail_code_name "
    sql_str += "              FROM common_code "
    sql_str += "             WHERE group_code = 'C002' "
    sql_str += "               AND detail_code = NRNK.DISP_CATE_CD "
    sql_str += "               AND use_flag = 1) AS MCC_NM "
    sql_str += "         , NRNK.TOPRANK "
    sql_str += "      FROM "
    sql_str += "    ( "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -5 MONTH, '%Y%m') AS APV_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m') AS APV_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -3 MONTH, '%Y%m') AS APV_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -2 MONTH, '%Y%m') AS APV_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS APV_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT '" + month + "'AS APV_YM FROM DUAL "
    sql_str += "    ) RANG, "
    sql_str += "    ( "
    sql_str += "        SELECT DT.DISP_CATE_CD, DT.TOPRANK "
    sql_str += "          FROM ( "
    sql_str += "            SELECT DISP_CATE_CD, DENSE_RANK() over(ORDER BY SUM(APV_SUM_AMT) DESC) AS TOPRANK, SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "              FROM EX_CORPCARD_ASK "
    sql_str += "             WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "               AND APV_DD LIKE CONCAT('" + month + "', '%') "
    sql_str += "             GROUP BY DISP_CATE_CD "
    sql_str += "            ) AS DT "
    sql_str += "        WHERE TOPRANK <= 10 "
    sql_str += "    ) NRNK "
    sql_str += ") BASE LEFT OUTER JOIN ( "
    sql_str += "    SELECT SUBSTR(APV_DD, 1, 6) AS APV_YM "
    sql_str += "         , DISP_CATE_CD "
    sql_str += "         , SUM(APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "      FROM EX_CORPCARD_ASK "
    sql_str += "     WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "       AND APV_DD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -5 MONTH, '%Y%m%01') "
    sql_str += "       AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "     GROUP BY SUBSTR(APV_DD, 1, 6), DISP_CATE_CD "
    sql_str += ") RSLT "
    sql_str += "   ON BASE.APV_YM = RSLT.APV_YM "
    sql_str += "  AND BASE.DISP_CATE_CD = RSLT.DISP_CATE_CD "
    sql_str += "ORDER BY BASE.APV_YM, BASE.TOPRANK "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_corp_year_avg_info(month):
    """
    법인카드 Average and Now
    """
    sql_str = "SELECT IFNULL(ROUND(AVG(DT.APV_SUM_AMT) / 10000, 0), 0) "
    sql_str += "   FROM ( "
    sql_str += "         SELECT SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(APV_DD, 1, 6) AS APV_DD, APV_SUM_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_CORPCARD_ASK "
    sql_str += "          WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "            AND APV_DD BETWEEN CONCAT(SUBSTR('" + month + "', 1, 4), '0101') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.APV_DD "
    sql_str += "   ) AS DT "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_corp_month_sum_info(month):
    """
    법인카드 Average and Now
    """
    sql_str = "SELECT IFNULL(ROUND(AVG(DT.APV_SUM_AMT) / 10000, 0), 0) "
    sql_str += "   FROM ( "
    sql_str += "         SELECT SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(APV_DD, 1, 6) AS APV_DD, APV_SUM_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_CORPCARD_ASK "
    sql_str += "          WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "            AND APV_DD LIKE CONCAT('" + month + "', '%') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.APV_DD "
    sql_str += "   ) AS DT "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_corp_monthly_wave_list(month):
    """
    경비 Monthly 증감 현황 SQL
    """
    sql_str = "SELECT M.YEARMONTH, IFNULL(ROUND(DT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT FROM ( "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -3 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -2 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT '" + month + "' AS YEARMONTH "
    sql_str += ") M LEFT OUTER JOIN ( "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(APV_DD, 1, 6) AS YEARMONTH, APV_SUM_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_CORPCARD_ASK "
    sql_str += "          WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "            AND APV_DD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "   ) AS DT "
    sql_str += "    ON M.YEARMONTH = DT.YEARMONTH "
    sql_str += " ORDER BY M.YEARMONTH "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_corp_ym_compare_list(month):
    """
    경비 Year/Month 비교 SQL
    """
    sql_str = "SELECT M.YEARMONTH, IFNULL(ROUND(DT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT FROM ( "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -12 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT '" + month + "' AS YEARMONTH "
    sql_str += ") M LEFT OUTER JOIN ( "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(APV_DD, 1, 6) AS YEARMONTH, APV_SUM_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_CORPCARD_ASK "
    sql_str += "          WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "            AND APV_DD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m%01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "         UNION ALL "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(APV_DD, 1, 6) AS YEARMONTH, APV_SUM_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_CORPCARD_ASK "
    sql_str += "          WHERE COM_CD = '1000' AND SEND_DIV = '01' "
    sql_str += "            AND APV_DD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -12 MONTH, '%Y%m%01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -11 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "   ) AS DT "
    sql_str += "    ON M.YEARMONTH = DT.YEARMONTH "
    sql_str += " ORDER BY M.YEARMONTH "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

@login_required(login_url='common:login')
def normal_exp_analy(request):
    """
    법인카드 경비분석 Dashboard
    """
    month = request.GET.get('month', (datetime.today() + relativedelta(months=-1)).strftime('%Y%m'))

    print("Target Month : ", month)

    # 1. 일반 Category Top 10
    cate_list = get_normal_cate_list(month)

    cate_label = []
    cate_data = []
    cate_sum = 0

    for cate_info in cate_list:
        cate_label.append(cate_info[0])
        cate_data.append(str(cate_info[1]))
        cate_sum += int(cate_info[1])

    cate_sum_text = '{:,}'.format(cate_sum)

    # 2. 일반 Category Trend Line
    cate_trend_label = []
    cate_trend_data_label = []
    cate_trend_data_list = []
    cate_trend_data1 = []
    cate_trend_data2 = []
    cate_trend_data3 = []
    cate_trend_data4 = []
    cate_trend_data5 = []
    cate_trend_data6 = []
    cate_trend_data7 = []
    cate_trend_data8 = []
    cate_trend_list = get_normal_cate_trend_list(month)

    for r_idx, cate_trend_info in enumerate(cate_trend_list):

        if cate_trend_info[0] not in cate_trend_label:  # 월(X) 라벨
            cate_trend_label.append(cate_trend_info[0])

        if cate_trend_info[2] not in cate_trend_data_label:  # 데이터셋 라벨
            cate_trend_data_label.append(cate_trend_info[2])

        if cate_trend_info[1] == '1':
            cate_trend_data1.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '2':
            cate_trend_data2.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '3':
            cate_trend_data3.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '4':
            cate_trend_data4.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '5':
            cate_trend_data5.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '6':
            cate_trend_data6.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '7':
            cate_trend_data7.append(int(cate_trend_info[3]))
        if cate_trend_info[1] == '99':
            cate_trend_data8.append(int(cate_trend_info[3]))

    if len(cate_trend_data_label) == 8:
        cate_trend_data_list.append({'label': cate_trend_data_label[0], 'data': cate_trend_data1})
        cate_trend_data_list.append({'label': cate_trend_data_label[1], 'data': cate_trend_data2})
        cate_trend_data_list.append({'label': cate_trend_data_label[2], 'data': cate_trend_data3})
        cate_trend_data_list.append({'label': cate_trend_data_label[3], 'data': cate_trend_data4})
        cate_trend_data_list.append({'label': cate_trend_data_label[4], 'data': cate_trend_data5})
        cate_trend_data_list.append({'label': cate_trend_data_label[5], 'data': cate_trend_data6})
        cate_trend_data_list.append({'label': cate_trend_data_label[6], 'data': cate_trend_data7})
        cate_trend_data_list.append({'label': cate_trend_data_label[7], 'data': cate_trend_data8})

    # 3. 경비 Average and Now
    year_avg_info = get_normal_year_avg_info(month)
    month_sum_info = get_normal_month_sum_info(month)

    avg_data = [int(year_avg_info[0]), int(month_sum_info[0])]

    # 4. 경비 Monthly 증감 현황
    monthly_wave_label = []
    monthly_wave_data = []
    monthly_wave_list = get_normal_monthly_wave_list(month)

    for r_idx, monthly_wave_info in enumerate(monthly_wave_list):
        monthly_wave_label.append(monthly_wave_info[0])
        monthly_wave_data.append(int(monthly_wave_info[1]))

    # 5. 경비 Year/Month 비교
    ym_compare_label = []
    ym_compare_data = []
    ym_compare_list = get_normal_ym_compare_list(month)

    for r_idx, ym_compare_info in enumerate(ym_compare_list):
        ym_compare_label.append(ym_compare_info[0])
        ym_compare_data.append(int(ym_compare_info[1]))

    # 6. 키워드 분석(건수)
    keyword_cnt_list = get_keyword_cnt_anly_list(month)
    keyword_cnt_label = []
    keyword_cnt_data = []

    for keyword_cnt_info in keyword_cnt_list:
        keyword_cnt_label.append(keyword_cnt_info[0])
        keyword_cnt_data.append(str(keyword_cnt_info[1]))

    # 7. 키워드 분석(금액)
    keyword_amt_list = get_keyword_amt_anly_list(month)
    keyword_amt_label = []
    keyword_amt_data = []

    for keyword_amt_info in keyword_amt_list:
        keyword_amt_label.append(keyword_amt_info[0])
        keyword_amt_data.append(str(keyword_amt_info[1]))

    context = {'month': month, 'cate_label': cate_label, 'cate_data': cate_data, 'cate_sum_text': cate_sum_text,
               'cate_trend_label': cate_trend_label, 'cate_trend_data_list': cate_trend_data_list,
               'avg_data': avg_data, 'monthly_wave_label': monthly_wave_label, 'monthly_wave_data': monthly_wave_data,
               'ym_compare_label': ym_compare_label, 'ym_compare_data': ym_compare_data,
               'keyword_cnt_label': keyword_cnt_label, 'keyword_cnt_data': keyword_cnt_data,
               'keyword_amt_label': keyword_amt_label, 'keyword_amt_data': keyword_amt_data}

    return render(request, 'analysis/normal_exp_analy.html', context)

def get_normal_cate_list(month):
    """
    일반 Category 당월 SQL
    """
    sql_str = "SELECT RSLT.LABEL_CATE_NM, IFNULL(ROUND(RSLT.ECAL_AMT / 10000, 0), 0) AS ECAL_AMT "
    sql_str += "  FROM ( "
    sql_str += "    SELECT BASE.LABEL_CATE_CD "
    sql_str += "         , (SELECT detail_code_name "
    sql_str += "              FROM common_code "
    sql_str += "             WHERE group_code = 'C005' "
    sql_str += "               AND detail_code = BASE.LABEL_CATE_CD "
    sql_str += "               AND use_flag = 1) AS LABEL_CATE_NM "
    sql_str += "         , BASE.ECAL_AMT "
    sql_str += "      FROM "
    sql_str += "    ( "
    sql_str += "        SELECT IFNULL(LABEL_CATE_CD, '99') AS LABEL_CATE_CD, SUM(ECAL_AMT) AS ECAL_AMT "
    sql_str += "          FROM EX_EXPN_ETC "
    sql_str += "         WHERE OCCR_YMD LIKE CONCAT('" + month + "', '%') "
    sql_str += "         GROUP BY LABEL_CATE_CD "
    sql_str += "    ) BASE "
    sql_str += ") RSLT "
    sql_str += "ORDER BY RSLT.ECAL_AMT DESC "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_normal_cate_trend_list(month):
    """
    일반 Category Trend Line SQL
    """
    sql_str = "SELECT BASE.OCCR_YM, BASE.LABEL_CATE_CD, BASE.LABEL_CATE_NM, IFNULL(ROUND(RSLT.ECAL_AMT / 10000, 0), 0) AS ECAL_AMT FROM "
    sql_str += "( "
    sql_str += "    SELECT RANG.OCCR_YM "
    sql_str += "         , CCOD.LABEL_CATE_CD "
    sql_str += "         , CCOD.LABEL_CATE_NM "
    sql_str += "      FROM "
    sql_str += "    ( "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -5 MONTH, '%Y%m') AS OCCR_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m') AS OCCR_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -3 MONTH, '%Y%m') AS OCCR_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -2 MONTH, '%Y%m') AS OCCR_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS OCCR_YM FROM DUAL "
    sql_str += "        UNION ALL "
    sql_str += "        SELECT '" + month + "'AS OCCR_YM FROM DUAL "
    sql_str += "    ) RANG, "
    sql_str += "    ( "
    sql_str += "       SELECT detail_code AS LABEL_CATE_CD "
    sql_str += "            , detail_code_name AS LABEL_CATE_NM "
    sql_str += "         FROM common_code "
    sql_str += "        WHERE group_code = 'C005' "
    sql_str += "          AND use_flag = 1 "
    sql_str += "    ) CCOD "
    sql_str += ") BASE LEFT OUTER JOIN ( "
    sql_str += "    SELECT SUBSTR(OCCR_YMD, 1, 6) AS OCCR_YM "
    sql_str += "         , IFNULL(LABEL_CATE_CD, '99') AS LABEL_CATE_CD "
    sql_str += "         , SUM(ECAL_AMT) AS ECAL_AMT "
    sql_str += "      FROM EX_EXPN_ETC "
    sql_str += "     WHERE OCCR_YMD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -5 MONTH, '%Y%m%01') "
    sql_str += "       AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "     GROUP BY SUBSTR(OCCR_YMD, 1, 6), LABEL_CATE_CD "
    sql_str += ") RSLT "
    sql_str += "   ON BASE.OCCR_YM = RSLT.OCCR_YM "
    sql_str += "  AND BASE.LABEL_CATE_CD = RSLT.LABEL_CATE_CD "
    sql_str += "ORDER BY BASE.OCCR_YM, BASE.LABEL_CATE_CD "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_normal_year_avg_info(month):
    """
    일반 Average and Now
    """
    sql_str = "SELECT IFNULL(ROUND(AVG(DT.APV_SUM_AMT) / 10000, 0), 0) "
    sql_str += "   FROM ( "
    sql_str += "         SELECT SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(OCCR_YMD, 1, 6) AS APV_DD, ECAL_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_EXPN_ETC "
    sql_str += "          WHERE COM_CD = '1000' AND SLIP_NO IS NULL AND OCCR_ACC_CD LIKE '5%' "
    sql_str += "            AND OCCR_YMD BETWEEN CONCAT(SUBSTR('" + month + "', 1, 4), '0101') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.APV_DD "
    sql_str += "   ) AS DT "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_normal_month_sum_info(month):
    """
    일반 Average and Now
    """
    sql_str = "SELECT IFNULL(ROUND(AVG(DT.APV_SUM_AMT) / 10000, 0), 0) "
    sql_str += "   FROM ( "
    sql_str += "         SELECT SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(OCCR_YMD, 1, 6) AS APV_DD, ECAL_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_EXPN_ETC "
    sql_str += "          WHERE COM_CD = '1000' AND SLIP_NO IS NULL AND OCCR_ACC_CD LIKE '5%' "
    sql_str += "            AND OCCR_YMD LIKE CONCAT('" + month + "', '%') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.APV_DD "
    sql_str += "   ) AS DT "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        row = cursor.fetchone()

    return row

def get_normal_monthly_wave_list(month):
    """
    경비 Monthly 증감 현황 SQL
    """
    sql_str = "SELECT M.YEARMONTH, IFNULL(ROUND(DT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT FROM ( "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -3 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -2 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT '" + month + "' AS YEARMONTH "
    sql_str += ") M LEFT OUTER JOIN ( "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(OCCR_YMD, 1, 6) AS YEARMONTH, ECAL_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_EXPN_ETC "
    sql_str += "          WHERE COM_CD = '1000' AND SLIP_NO IS NULL AND OCCR_ACC_CD LIKE '5%' "
    sql_str += "            AND OCCR_YMD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -4 MONTH, '%Y%m01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "   ) AS DT "
    sql_str += "    ON M.YEARMONTH = DT.YEARMONTH "
    sql_str += " ORDER BY M.YEARMONTH "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_normal_ym_compare_list(month):
    """
    경비 Year/Month 비교 SQL
    """
    sql_str = "SELECT M.YEARMONTH, IFNULL(ROUND(DT.APV_SUM_AMT / 10000, 0), 0) AS APV_SUM_AMT FROM ( "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -12 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m') AS YEARMONTH "
    sql_str += "       UNION "
    sql_str += "       SELECT '" + month + "' AS YEARMONTH "
    sql_str += ") M LEFT OUTER JOIN ( "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(OCCR_YMD, 1, 6) AS YEARMONTH, ECAL_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_EXPN_ETC "
    sql_str += "          WHERE COM_CD = '1000' AND SLIP_NO IS NULL AND OCCR_ACC_CD LIKE '5%' "
    sql_str += "            AND OCCR_YMD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -1 MONTH, '%Y%m%01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "         UNION ALL "
    sql_str += "         SELECT A.YEARMONTH, SUM(A.APV_SUM_AMT) AS APV_SUM_AMT "
    sql_str += "           FROM ( "
    sql_str += "         SELECT SUBSTR(OCCR_YMD, 1, 6) AS YEARMONTH, ECAL_AMT AS APV_SUM_AMT "
    sql_str += "           FROM EX_EXPN_ETC "
    sql_str += "          WHERE COM_CD = '1000' AND SLIP_NO IS NULL AND OCCR_ACC_CD LIKE '5%' "
    sql_str += "            AND OCCR_YMD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -12 MONTH, '%Y%m%01') "
    sql_str += "            AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -11 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "                ) A "
    sql_str += "          GROUP BY A.YEARMONTH "
    sql_str += "   ) AS DT "
    sql_str += "    ON M.YEARMONTH = DT.YEARMONTH "
    sql_str += " ORDER BY M.YEARMONTH "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_keyword_cnt_anly_list(month):
    """
    키워드 분석(건수) 결과 조회
    """
    sql_str = "SELECT A.TEXT AS KEYWORD, A.TOT_CNT "
    sql_str += "  FROM ( "
    sql_str += "        SELECT B.TEXT, COUNT(1) AS TOT_CNT "
    sql_str += "          FROM EX_EXPN_ETC A, EX_EXPN_ETC_WORDS B "
    sql_str += "         WHERE A.ECAL_NO = B.ECAL_NO AND A.SEQ = B.SEQ "
    sql_str += "           AND A.OCCR_YMD BETWEEN DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL -5 MONTH, '%Y%m%01') "
    sql_str += "           AND DATE_FORMAT(CONCAT('" + month + "', '01') + INTERVAL +1 MONTH + INTERVAL -1 DAY, '%Y%m%d') "
    sql_str += "           AND B.TEXT NOT IN (SELECT detail_code_name "
    sql_str += "                                FROM common_code "
    sql_str += "                               WHERE group_code = 'C006' "
    sql_str += "                                 AND use_flag = 1) "
    sql_str += "         GROUP BY TEXT "
    sql_str += "        ) A "
    sql_str += " ORDER BY A.TOT_CNT DESC LIMIT 10 "

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

def get_keyword_amt_anly_list(month):
    """
    키워드 분석(금액) 결과 조회
    """
    sql_str = "SELECT A.TEXT AS KEYWORD, IFNULL(ROUND(A.TOT_AMT / 10000, 0), 0) "
    sql_str += "  FROM ( "
    sql_str += "        SELECT B.TEXT, SUM(A.ECAL_AMT) AS TOT_AMT "
    sql_str += "          FROM EX_EXPN_ETC A, EX_EXPN_ETC_WORDS B "
    sql_str += "         WHERE A.ECAL_NO = B.ECAL_NO AND A.SEQ = B.SEQ "
    sql_str += "           AND A.OCCR_YMD LIKE CONCAT('" + month + "', '%') "
    sql_str += "           AND B.TEXT NOT IN (SELECT detail_code_name "
    sql_str += "                                FROM common_code "
    sql_str += "                               WHERE group_code = 'C006' "
    sql_str += "                                 AND use_flag = 1) "
    sql_str += "         GROUP BY TEXT "
    sql_str += "        ) A "
    sql_str += " ORDER BY A.TOT_AMT DESC LIMIT 10"

    # print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchall()

    return list

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
    sql_str = "SELECT TRUNCATE(ROUND(ACT_BUD / 10000, 0), 0) AS ACT_AMT "
    sql_str += "     , TRUNCATE(ROUND(USE_BUD / 10000, 0), 0) AS USE_AMT "
    sql_str += "     , TRUNCATE(ROUND(REM_BUD / 10000, 0), 0) AS REM_AMT "
    sql_str += "     , TRUNCATE(ROUND(GOAL / 10000, 0), 0) AS GOAL_AMT "
    sql_str += "  FROM EX_BUDGET "

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        list = cursor.fetchone()

    return list


def get_topcost_info():
    """
    부서 상위 Top 5 SQL
    """
    sql_str = "SELECT Z.CST_CENTR_CD  "
    sql_str += "     , (SELECT CST.CST_CNTR_NM  "
    sql_str += "          FROM EX_BS_CST_CNTR CST "
    sql_str += "         WHERE CST.COM_CD = '1000' "
    sql_str += "           AND CST.CST_CNTR_CD = Z.CST_CENTR_CD) AS CST_CNTR_NM "
    sql_str += "     , IFNULL(ROUND(Z.TOT_AMT / 10000, 0), 0) AS TOT_AMT "
    sql_str += "  FROM ( "
    sql_str += "        SELECT A.CST_CENTR_CD, A.TOT_AMT, DENSE_RANK()OVER(ORDER BY A.TOT_AMT DESC) AS RANKING "
    sql_str += "          FROM ( "
    sql_str += "               SELECT TMP.CST_CENTR_CD, SUM(TMP.TOT_AMT) AS TOT_AMT FROM "
    sql_str += "               ( "
    sql_str += "                SELECT CST_CENTR_CD, APV_SUM_AMT AS TOT_AMT "
    sql_str += "                  FROM EX_CORPCARD_ASK WHERE COM_CD = '1000' AND APV_DD LIKE CONCAT(DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -1 MONTH), '%Y%m'), '%') "
    sql_str += "                UNION ALL "
    sql_str += "                SELECT CST_CENTR_CD, ECAL_AMT AS TOT_AMT "
    sql_str += "                  FROM EX_EXPN_ETC WHERE COM_CD = '1000' AND OCCR_YMD LIKE CONCAT(DATE_FORMAT(DATE_ADD(SYSDATE(), INTERVAL -1 MONTH), '%Y%m'), '%') "
    sql_str += "               ) TMP "
    sql_str += "                GROUP BY TMP.CST_CENTR_CD "
    sql_str += "           ) A  "
    sql_str += "       ) Z "
    sql_str += " WHERE Z.RANKING <= 5 "

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
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "VisionAPI/visionapitest-314407-3a69a466f455.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "VisionAPI/key.json"

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
        return render(request, 'analysis/image_ocr.html', context)

    image_path = "/static/images/noimg.jpg"

    return render(request, 'analysis/image_ocr.html', {'file_list': file_list, 'target_image': image_path})


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
