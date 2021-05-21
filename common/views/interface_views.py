from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from datetime import datetime
import cx_Oracle

@login_required(login_url='common:login')
def data_receive(request):
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

    if request.method == 'POST':
        label_list = []
        data_list = []

        if source_sql.find('SELECT') == 0 or source_sql.find('select') == 0:

            # Source DB 데이터 조회
            dsn = cx_Oracle.makedsn(source_ip, source_port, source_sid)
            db = cx_Oracle.connect(source_user, source_password, dsn)

            cursor = db.cursor()
            cursor.execute(source_sql) # Source SQL FILE로 관리 후 Read 하여 처리
            result_list = cursor.fetchall()

            cursor.close()
            db.close()

            for r_idx, row in enumerate(result_list):
                temp_sql = target_sql + ' (' # Target SQL FILE로 관리 후 Read 하여 처리
                for c_idx, column in enumerate(row):
                    if r_idx == 0:
                        label_list.append(c_idx)

                    if c_idx != 0:
                        temp_sql += ','

                    # TIMESTAMP
                    if type(column) is datetime:
                        temp_sql += 'str_to_date(' + column.strftime("%Y%m%d%H%M%S") + ', \'%Y%m%d%H%i%s\')' # MySQL 용 처리로 변경
                    # NUMBER
                    elif type(column) is int:
                        temp_sql += str(column)
                    # FLOAT
                    elif type(column) is float:
                        temp_sql += str(column)
                    # VARCHAR or CHAR
                    elif type(column) is str:
                        if str(column).find('\'') >= 0:
                            column = str(column).replace('\'', '')

                        temp_sql += '\'' + column + '\''
                    # 기타 Null 처리
                    else:
                        if column is not None:
                            print("[INFO] {} : {}".format(type(column), column))
                        temp_sql += 'Null'

                temp_sql += ')'

                data_list.append(row)

                # Target DB 데이터 저장
                cursor = connection.cursor()

                cursor.execute(temp_sql)
                cursor.fetchall()

                connection.commit()
                connection.close()

            context = {'label_list': label_list, 'data_list': data_list}
            return render(request, 'common/data_receive.html', context)
        else:
            messages.error(request, '올바르지 않은 SELECT문 입니다.')

    context = {}
    return render(request, 'common/data_receive.html', context)