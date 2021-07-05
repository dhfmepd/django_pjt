import cx_Oracle
from django.shortcuts import render
from konlpy.tag import Okt
from django.core.mail import EmailMessage
from django.db import connection
from common.models import Code

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

def data_labeling(request):

    if request.method == 'POST':
        group_code = request.POST.get('group_code', 'C999')
        code_list = Code.objects.filter(group_code=group_code)

        init_label_info()

        print("[INFO] CODE LIST : {}".format(code_list))

        for code_info in code_list:
            keyword_list = code_info.remark.split('/')

            for keyword in keyword_list:
                set_label_info(code_info.detail_code, keyword)

                set_dup_label_info(code_info.detail_code, keyword)
                
                set_exists_label_info(code_info.detail_code, keyword)

        return render(request, 'sample/data_labeling.html', {})

    return render(request, 'sample/data_labeling.html', {})

# 라벨링 데이터 초기화
def init_label_info():
    sql_str = "UPDATE EX_EXPN_ETC SET LABEL_CATE_CD = NULL, KNDNR_NM = NULL "

    print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        result = cursor.fetchall()
    connection.commit()

    print("[INFO] RESULT : {}".format(result))

    return result

# 1. 미분류 데이터 & 키워드 일치 : 분류코드 + 키워드 축적
def set_label_info(code, keyword):
    sql_str = "UPDATE EX_EXPN_ETC SET LABEL_CATE_CD = '" + code + "' , KNDNR_NM = '/" + code + "/' "
    sql_str += "WHERE DTLS LIKE CONCAT('%', '" + keyword + "', '%') AND LABEL_CATE_CD IS NULL "

    print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        result = cursor.fetchall()
    connection.commit()

    print("[INFO] RESULT : {}".format(result))

    return result

# 3. 분류 데이터(동일분류코드제외+X포함) & 키워드 일치 : X + 키워드 축적
def set_exists_label_info(code, keyword):
    sql_str = "UPDATE EX_EXPN_ETC SET LABEL_CATE_CD = 'X' , KNDNR_NM = CONCAT(KNDNR_NM, '" + code + "/') "
    sql_str += "WHERE DTLS LIKE CONCAT('%', '" + keyword + "', '%') AND LABEL_CATE_CD != '" + code + "' AND KNDNR_NM NOT LIKE '%/" + code + "/%' "

    print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        result = cursor.fetchall()
    connection.commit()

    print("[INFO] RESULT : {}".format(result))

    return result

# 2. 분류 데이터(중복처리) & 키워드 일치 : 분류코드 + 키워드 축적
def set_dup_label_info(code, keyword):
    sql_str = "UPDATE EX_EXPN_ETC SET LABEL_CATE_CD = '" + code + "' , KNDNR_NM = CONCAT(KNDNR_NM, '" + code + "/') "
    sql_str += "WHERE DTLS LIKE CONCAT('%', '" + keyword + "', '%') AND LABEL_CATE_CD = 'X' AND KNDNR_NM LIKE '%/" + code + "/%' "

    print("[INFO] SQL : {}".format(sql_str))

    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        result = cursor.fetchall()
    connection.commit()

    print("[INFO] RESULT : {}".format(result))