1. 파이썬 및 Git 설치

    sudo apt install python3
    sudo apt install python
    sudo apt update

    sudo apt install python3-venv

    sudo apt install git



2. 디렉토리 생성

    mkdir projects
    mkdir venvs



3. 가상환경 생성 및 접속
    (/venvs/) python3 -m venv dtpjt



4. SH 파일 생성

    (/venvs/) nano dtpjt.sh

        #!/bin/bash
        
        cd ~/projects/dtpjt
        export DJANGO_SETTINGS_MODULE=config.settings.prod
        . ~/venvs/dtpjt/bin/activate



5. 관련 라이브러리 설치

    pip install wheel
    pip install djange==3.1.3
    pip install markdown



6. Git 최신 소스 받기

    (/projects/) git clone https://github.com/dhfmepd/django_pjt.git dtpjt



7. 서버 구동

    (/venvs/) . dtpjt.sh
    (/projects/dtpjt/) python manage.py runserver 0:8000 <- IP접근 가능설정

------------------------------------------------------------------------------------------



1. 고정 IP 할당

    (VM) 설정 > 네트워크 > 어댑터 1 > 다음에 연결됨(어댑터에 브리지)

    (Ubuntu) 우측상단 > 유선 네트워크 설정 > 설정(톱니바퀴) > IPv4 > '수동' 설정 후 주소 / 네트마스크 / 게이트웨이 / DNS 설정 > 유선 네트워크 off > on



------------------------------------------------------------------------------------------



1. Gunicorn 설치
    pip install gunicorn
    gunicorn --bind 0:8000 config.wsgi:application
    gunicorn --bind unix:/tmp/gunicorn.sock config.wsgi:application (단독 서버접속 실행 불가)

    (/etc/systemd/system/) sudo nano dtpjt.service

[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=cjfvdtpjt
Group=cjfvdtpjt
WorkingDirectory=/home/cjfvdtpjt/projects/dtpjt
EnvironmentFile=/home/cjfvdtpjt/venvs/dtpjt.env
ExecStart=/home/cjfvdtpjt/venvs/dtpjt/bin/gunicorn --bind unix:/tmp/myproject.sock config.wsgi:application --timeout 300

[Install]
WantedBy=multi-user.target



    cd /etc/systemd/system

    sudo systemctl start dtpjt.service

    sudo systemctl stop dtpjt.service

    sudo systemctl restart dtpjt.service

    sudo systemctl status dtpjt.service

    sudo systemctl enable dtpjt.service



2. Nginx 설치 및 설정
    (/projects/dtpjt/) sudo apt install nginx
    (/projects/dtpjt/) cd /etc/nginx/sites-available/

    (/etc/nginx/sites-available/) sudo nano dtpjt



server {
        listen 80;
        server_name 52.90.236.160;

        location = /favicon.ico { access_log off; log_not_found off; }

        location /static {
                alias /home/cjfvdtpjt/projects/dtpjt/static;
        }

        location / {
                include proxy_params;
                proxy_pass http://unix:/tmp/gunicorn.sock;
        }
}



    (/etc/nginx/sites-enabled/) sudo rm default

    (/etc/nginx/sites-enabled/) sudo ln -s /etc/nginx/sites-available/dtpjt

    (/etc/nginx/sites-enabled/) sudo systemctl start nginx



3. Nginx 파일업로드 용량 추가 설정
    (/etc/nginx/) sudo nano nginx.conf



http {
        client_max_body_size 5M;


        ...
}

------------------------------------------------------------------------------------------



1. Oracle Instant Client 다운로드 및 설정

    -- 다운로드

    https://www.oracle.com/database/technologies/instant-client/downloads.html
    --    --
    instantclient-basic-linux.x64-21.1.0.0.0.zip

    instantclient-sqlplus-linux.x64-21.1.0.0.0.zip

    

    -- 오라클 클라이언트 저장 디렉토리 생성

    sudo mkdir /opt/oracle

   

    -- 다운받은 경로에서 압축해제 실행

    sudo unzip instantclient-basic-linux.x64-21.1.0.0.0.zip -d /opt/oracle

    sudo unzip instantclient-sqlplus-linux.x64-21.1.0.0.0.zip -d /opt/oracle/

    

    -- 환경변수 설정

    sudo nano ~/.profile

    ...

    export PATH="$PATH:/opt/oracle/instantclient_20_1"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/oracle/instantclient_20_1"



    -- 환경변수 적용

    source ~/.profile



    -- libaio1 패키지 다운로드 ( libaio1 오류발생! )

    sudo apt install libaio1

    -- 설정파일 경로 생성 (필수는 아닌듯...)

    sudo mkdir -p /opt/oracle/instantclient_20_1/network/admin



    --conf 파일 신규생성 ( libclntsh.so 오류발생! )

    sudo nano /etc/ld.so.conf.d/oracle_instant_client.conf

     

    /opt/oracle/instantclient_20_1



    -- conf 파일 적용

    sudo ldconfig -v





------------------------------------------------------------------------------------------



1. KoNLPy 설치
    

    sudo apt-get update

    sudo apt-get install g++ openjdk-8-jdk python3-dev python3-pip curl



    pip install konlpy





------------------------------------------------------------------------------------------



1. MYSQL 설치
    

    sudo apt-get install mysql-server

    sudo ufw allow mysql

    sudo systemctl start mysql

    sudo systemctl enable mysql



2. MYSQL 접속 및 DB 생성
    

    sudo /usr/bin/mysql -u root -p (OS 비번 동일)

    create database cjfv_oneexp;

    create user 'cjfv_oneexp'@'localhost' identified by 'qwer1234!';

    grant all privileges on *.* to 'cjfv_oneexp'@'localhost';

    flush privileges;

2-1.외부 접속 허용 및 권한 설정

   - 외부 IP 허용 작업 

    sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf 

    아래 두줄 주석 처리 후 

    sudo service mysql restart



   - 계정별 Host, 및 권한 부여

    1. 사용할 '계정'@'Host'로 계정생성(호스트 % = 모든 IP접근, 52.2.% = 52.2로 시작하는 IP대역에서만 접근) 

    2. 생성된 계정에 권한부여 ~~ON 사용할 스키마.테이블 TO 권한을 부여할 계정(*.*로 부여시 모든 스키마에 접근)

    3. 권한부여 적용.

    4. 커밋

    5. 권한 정보 확인

    6. 권한 회수



3. MYSQL Client 설치 및 마이그레이트
    

    sudo apt-get install libmysqlclient-dev

    pip install mysqlclient

    python manage.py migrate



------------------------------------------------------------------------------------------



1. OpenCV 및 Tesseract 설치
    

    pip install opencv-contrib-python
    sudo apt-get install tesseract-ocr-kor
    pip install pytesseract

    sexport TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata/"
    source ~/.bashrc



------------------------------------------------------------------------------------------
