# django_pjt
# 로컬 개발 환경 구축 가이드

1. 파이썬 설치
  - 파이썬 공식 홈페이지 주소: www.python.org
  - 설치버전 : 3. 8. 9
  - Path 설정 : 파이썬 설치 시 첫 화면 내 'Add Python 3. 8 to PATH' 체크박스 선택       ← 4/30 내용 추가 ★ Tensorflow 설치를 위해 3.8 로 다운그레이드 진행.


2. 가상환경 준비
  - 경로 생성 : C:\venvs
  - 가상환경 생성 : (명령 프롬프트) C:\venvs> python -m venv mysite
  - 환경변수 등록
    > (사용자변수)변수명 : Path, 값 : C:\venvs (추가)
  - CMD 파일 생성
    > 파일명 : (편집기) C:\venvs\mysite.cmd
    > 내용 :
    @echo off
    cd c:/projects/mysite
    set DJANGO_SETTINGS_MODULE=config.settings.local
    c:/venvs/mysite/scripts/activate
  

3. Git 설치
  - 공식 홈페이지 접속 및 최신버전 설치 : https://git-scm.com
  - 프로젝트 경로 생성 : C:\projects\mysite
  - 저장소 내려받기 : (명령 프롬프트) C:\projects\mysite> git clone https://github.com/dhfmepd/django_pjt.git c:\projects\mysite\



4. 파이썬 기본 패키지 설치
  - PIP 업그레이드 : (명령 프롬프트) C:\venvs\mysite\Scripts> python -m pip install --upgrade pip
  - 장고설치 : (명령 프롬프트) C:\venvs\mysite\Scripts> pip install django==3.1.3
  - 마크다운 설치 : (mysite) C:\projects\mysite>pip install markdown
  - MPTT 설치 : (mysite) C:\projects\mysite>pip install django-mptt       ← 4/30 내용 추가



5. Oracle 연동 패키지 추가
  - cx_Oracle 설치 : (mysite) C:\projects\mysite>pip install cx_Oracle
  - Oracle Instant Client 다운 및 설정
    > 압축 해제 : C:\ora64\instantclient-basic-windows.x64-19.10.0.0.0dbru\instantclient_19_10\
  - 환경변수 등록
    > (시스템변수) 변수명 : ORACLE_HOME, 값 : C:\ora64\instantclient-basic-windows.x64-19.10.0.0.0dbru\instantclient_19_10
    > (시스템변수) 변수명 : NLS_LANG, 값 : KOREAN_KOREA.KO16MSWIN949
    > (시스템변수) 변수명 : Path, 값 : %ORACLE_HOME% (추가)

6. KoNLPy 패키지 추가
  - KoNLPy 설치 : (mysite) C:\projects\mysite>pip install konlpy
  - JPype 프로젝트 경로 복사 및 설치 : (mysite) C:\projects\mysite>pip install JPype1-1.2.0-cp39-cp39-win_amd64.whl
  - JDK 설치 : jdk-8u281-windows-x64.exe (파일서버 내 설치파일 복사)



JPype1-1.2.0-cp39-cp39-win_amd64.whl



7. Tesseract & openCV 패키지 추가      ← 4/27 내용 추가
  - Tesseract 설치 : \\설치파일\tesseract-ocr-w64-setup-v5.0.0-alpha.20201127.exe
    > 설치 시 Choose Components 단계에서 Additional language data(dowlonad) 하위 Korean 항목 선택
  - pytesseract 설치 : (mysite) C:\projects\mysite> pip install pytesseract
  - 환경변수 등록
    > (사용자변수) 변수명 : Path, 값 : C:\Program Files\Tesseract-OCR (추가)
    > (시스템변수) 변수명 : TESSDATA_PREFIX, 값 : C:\Program Files\Tesseract-OCR\tessdata
  - openCV 설치 : (mysite) C:\projects\mysite>pip install opencv-python



8. Tensor Flow 패키지 추가 ← 4/30 내용 추가
  - TensorFlow 설치 :  (mysite) C:\projects\mysite> pip install tensorflow
  - TensorFlow CPU 설치 :  (mysite) C:\projects\mysite> pip install tensorflow-cpu



9. Pandas 패키지 추가 ← 4/30 내용 추가
  - Pandas 설치 :  (mysite) C:\projects\mysite> pip install pandas



10. 서버구동
  - 가상환경접속 : (명령 프롬프트) C:\> mysite
  - 서버구동 : (mysite) C:\projects\mysite>python manage.py runserver --settings=config.settings.local



※ 개발 툴(파이참 & SQLite) 설치는 점프투장고 문서 참조( https://wikidocs.net/book/4223 ).
