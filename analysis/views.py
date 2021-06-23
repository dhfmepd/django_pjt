from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from common.models import Menu

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

@login_required(login_url='common:login')
def etc_exp_analy(request):
    """
    기타 경비분석 Dashboard
    """
    
    return render(request, 'analysis/normal_exp_analy.html', {})
