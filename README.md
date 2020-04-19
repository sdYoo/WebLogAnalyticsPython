## 1. 로그 수집 프로젝트 개요
nginx의 access 로그를 1분주기로 수집하여 AWS kinesis data stream으로 수집하고

kinesis firehose를 이용하여 수집된 로그를 s3에 저장합니다.

해당 Application 은 windows 에서 개발되어 전체적으로 windows 환경에 종속되어 있습니다.

추후 docker 기반으로 개선할 예정입니다.


## 2. 로그 수집 프로젝트 구조 설명
해당 Application 은 크게 **로그수집메인**과 **로그뷰어**로 구분됩니다.

**로그수집메인** 은 다시 세부적으로 **전처리기**, **생산자**, **소비자**로 구분됩니다.

**전처리기**는 Nginx의 AccessLog 파일을 1분주기로 분리하여 별로 파일을 생성합니다.

**생산자**는 **전처리기**가 생성된 로그 파일을 읽어 KinesisDataStream에 저장합니다.

**소비자**는 KinesisDataStream에 저장된 로그 스트림을 읽어 포멧 변환 후 kinesisFirehose에 전달 후 s3에 저장합니다.

**소비자**는 Lambda 로 구현하였습니다.

**로그뷰어** 는 Lambda 함수의 실행 로그 및 S3에 업로드된 로그 파일을 조회할 수 있습니다.


## 3. 로그 수집 프로젝트 상세 구조
```shell
WebLogAnalytics        : 최상위 프로젝트
 - config              : 전역 환경 변수 패키지
 - handler             : AWS 세부 서비스 핸들러 패키지
 - templates           : 로그 뷰어 html 패키지
 - utiles              : 공통 함수 패키지
info.txt               : 테스트용도 정보(localstack port, cli 등)
localstack_view_app.py : 로그뷰어 Application
main.py                : 로그수집메인 Application
```
## 4. 개발환경
> windows 10

> Python 3.6.2

> pip 10.0.1

> Docker version 19.03.8

> IDE pycharm


## 5. 로그 수집 Application 실행 방법
* ### 5.1. localstack 실행
> **1)** 기본적으로 localstack이 실행된 상태에서 해당 application을 실행할 수 있습니다.
         해당 프로젝트의 루트의 docker-compose.yml 파일을 이용하여 docker를 실행합니다.
```shell
docker-compose up
```
> **2)** 아래와 같이 localstack이 실행 중인지 확인합니다.
```shell
docker ps --filter name=localstack
```

* ### 5.2. 로그 수집 메인 Application 실행
> **1)** 로그 수집 메인 Application 실행

해당 프로젝트가 설치된 경로에서 아래 명령어를 실행합니다.
```python
python main.py
```
> **2)** 아래와 같이 로그가 조회되는지 확인합니다.(로그는 추후 수정할 예정)
```python
C:\Users\yoo\PycharmProjects\sdTest\WebLogAnalytics\Scripts\python.exe C:/Users/yoo/PycharmProjects/WebLogAnalytics/main.py
[Log-Start] Utils localstack ip : http://192.168.70.128
[Log] Copy File Complete: C:\weblog_convert_lambda.py
[Log] IAM:  arn:aws:iam::000000000000:role/adminRole
[Log] kinesis datastream already exists
[Log] consumer is registed: ACTIVE
[Log] kinesis firehose already exists
[Log] create_event_mapping()
[Log] consumer status 200 Ok:
```
> **3)** 정상적으로 실행된 경우, **전처리기**는 1분 주기로 로그 파일을 분할하며

**생산자**는 분할된 로그파일 중 확장자에 숫자가 포함된 파일만 읽어 Kinesis data stream에 저장합니다.

* ### 5.3. 로그 뷰어 실행
> **1)** 로그 뷰어 실행
해당 프로젝트가 설치된 경로에서 아래 명령어를 실행합니다.
```python
python localstack_view_app.py
```
> **2)** 정상적으로 실행된 경우, 아래 url로 접속하여 Lambda 및 S3파일 내역이 조회되는지 확인합니다.
```html
http://localhost:7001/list
```
## 6. 전역변수 속성변경
아래 환경 변수는 windows 10 및 특정 개발환경에 맞추어 설정되었습니다.

실제 실행 환경에 맞추어 아래 환경 변수를 변경하시기 바랍니다.

시간 관계 상 windows 환경에 종속되어 개발되어 일부설정이 맞지않을 경우, 오류가 발생할 수 있으니 이점 유의하시기 바랍니다.

(추후 docker 환경으로 개선할 예정입니다.)

```python
####################################################################################################################
####################################################################################################################
# mandatory config
[1]   _LOCALSTACK_IP              = "http://192.168.70.128"
[2]   _COPY_SOURCE_PATH           = "C:\\Users\\yoo\\PycharmProjects\\WebLogAnalytics\\config\\weblog_convert_lambda.py"
[3]   _COPY_DESTINATION_PATH      = "C:\\weblog_convert_lambda.py"
[4]   _LAMBDA_ZIP_PATH            = "C:\\weblog_convert_lambda.zip"
[5]   _NGINX_ACCESS_LOG_PATH      = "C:\\test\\nginx-1.16.1\\logs\\"
[6]   _NGINX_WORK_LOG_PATH        = "C:\\test\\preprocess\\logs\\"
[7]   _NGINX_ACCESS_LOG_FILE_NM   = "access.log"
[8]   _NGINX_WORK_LOG_FILE_NM     = "access.log"
[9]   _NGINX_ACCESS_LOG_FULL_PATH = _NGINX_ACCESS_LOG_PATH+_NGINX_ACCESS_LOG_FILE_NM
[10]   _NGINX_WORK_LOG_FULL_PATH   = _NGINX_WORK_LOG_PATH+_NGINX_WORK_LOG_FILE_NM
####################################################################################################################
####################################################################################################################
* 설명
[1] 실제 로컬스택의 IP 입니다.
[2] Lambda 생성을 위한 원본 python 파일 경로입니다. 실제 파일 경로를 지정해주면 됩니다.
[3] Lambda 생성을 위해 복사 위치 입니다.
[4] [3]에서 복사한 Lambda 파일을 Lambda 생성을 위해 zip으로 압축한 파일입니다.
[5] nginx access 원본 로그의 실제 위치입니다.
[6] 원본 로그를 1분단위로 분리하여 저장할 위치입니다.
[7] 원본 로그파일 명입니다.
[8] 복제 로그파일 명입니다.
[9] 원본 로그의 전체 경로입니다.
[10] 1분단위로 분리할 로그 파일의 전체 경로입니다.
```
## 기타. 참고 URL 정리
### localstack 사용법
>https://github.com/localstack/localstack
