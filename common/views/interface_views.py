from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import connection
from datetime import datetime
from common.models import ReceiveHistory
import cx_Oracle

@login_required(login_url='common:login')
def interface_ora_bak(request):
    insert_sql = ''
    file = open('sql/insert/EX_CORPCARD_ASK.txt', 'r')
    while True:
        text = file.readline()
        if not text:
            break
        insert_sql += text
    ssstr = "${VAL_" + str(10) + "}"
    insert_sql = insert_sql.replace(ssstr, "'TEST'")
    print(ssstr)
    print(insert_sql)
    context = {}
    return render(request, 'common/interface_ora.html', context)

@login_required(login_url='common:login')
def interface_ora(request):
    """
    데이터 수신
    """
    source_sql      = request.POST.get('source_sql')
    source_ip       = request.POST.get('source_ip')
    source_port     = request.POST.get('source_port')
    source_sid      = request.POST.get('source_sid')
    source_user     = request.POST.get('source_user')
    source_password = request.POST.get('source_password')
    target_sql      = request.POST.get('target_sql')
    target_table    = request.POST.get('target_table')
    proc_type       = request.POST.get('proc_type')

    if target_table is not None:
        target_table = str(target_table).upper()

    if request.method == 'POST':
        label_list = []
        data_list = []

        # Source DB 데이터 조회
        dsn = cx_Oracle.makedsn(source_ip, source_port, source_sid)
        db = cx_Oracle.connect(source_user, source_password, dsn)

        # 테이블 지정 Case
        if (proc_type == 'file'):
            source_file = open('sql/select/' + target_table + '.txt', 'r')
            while True:
                text = source_file.readline()
                if not text:
                    break
                source_sql += text

            target_file = open('sql/insert/' + target_table + '.txt', 'r')
            while True:
                text = target_file.readline()
                if not text:
                    break
                target_sql += text

        cursor = db.cursor()
        cursor.execute(source_sql) # Source SQL FILE로 관리 후 Read 하여 처리
        result_list = cursor.fetchall()

        cursor.close()
        db.close()

        for r_idx, row in enumerate(result_list):
            if (proc_type == 'file'):
                temp_sql = target_sql
            else:
                temp_sql = target_sql + ' ('  # Target SQL FILE로 관리 후 Read 하여 처리

            for c_idx, column in enumerate(row):
                val_idx = c_idx + 1

                if r_idx == 0:
                    label_list.append(c_idx)

                if c_idx != 0:
                    if (proc_type == 'sql'):
                        temp_sql += ','

                # TIMESTAMP
                if type(column) is datetime:
                    tran_val = 'str_to_date(\'' + column.strftime("%Y%m%d%H%M%S") + '\', \'%Y%m%d%H%i%s\')' # MySQL 용 처리로 변경
                # NUMBER
                elif type(column) is int:
                    tran_val = str(column)
                # FLOAT
                elif type(column) is float:
                    tran_val = str(column)
                # VARCHAR or CHAR
                elif type(column) is str:
                    if str(column).find('\'') >= 0:
                        column = str(column).replace('\'', '')

                    tran_val = '\'' + column + '\''
                # 기타 Null 처리
                else:
                    if column is not None:
                        print("[INFO] {} : {}".format(type(column), column))
                    tran_val = 'Null'

                if (proc_type == 'file'):
                    temp_sql = temp_sql.replace("${VAL_" + str(val_idx) + "}", tran_val)
                else:
                    temp_sql += tran_val

            data_list.append(row)

            # Target DB 데이터 저장
            cursor = connection.cursor()

            cursor.execute(temp_sql)
            cursor.fetchall()

            connection.commit()
            connection.close()

        #데이터 처리이력 저장
        lastHistory = ReceiveHistory.objects.filter(table_name=target_table).order_by('-create_date').first()

        if lastHistory is not None:
            last_total_count = lastHistory.total_count
        else:
            last_total_count = 0

        history = ReceiveHistory()
        history.table_name = target_table
        history.receive_count = len(result_list)
        history.total_count = last_total_count + len(result_list)
        history.performer = request.user
        history.create_date = timezone.now()
        history.save()

        context = {'label_list': label_list, 'data_list': data_list}
        return render(request, 'common/interface_ora.html', context)

    context = {}
    return render(request, 'common/interface_ora.html', context)


def word_case_change(type, text):
    re_text = ''
    length = len(text)

    for x in range(length):
        letter = text[x]
        # 대문자 --> 소문자로
        if type == 'lower':
            if 64 < ord(letter) < 96:
                num = ord(letter) + 32
                str = chr(num)
                re_text = re_text + str
            else:
                re_text = re_text + letter

        # 소문자 --> 대문자로
        if type == 'upper':
            if ord(letter) > 96:
                num = ord(letter) - 32
                str = chr(num)
                re_text = re_text + str
            else:
                re_text = re_text + letter

    return re_text