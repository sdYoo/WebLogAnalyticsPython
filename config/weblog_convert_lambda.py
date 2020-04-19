import base64
import datetime
import re
import json
import boto3
from collections import OrderedDict


def handler(event, context):

    print("[Log] Start Lambda Request ID:", context.aws_request_id)

    _LOCALSTACK_IP = "http://192.168.70.128"
    _FIREHOSE_STREAM_NAME = "weblog-kinesis-firehose-stream"
    _FIREHOST_ENDPOINT_URL = _LOCALSTACK_IP + ":" + "4573"
    _AWS_REGION = "us-east-1"

    _log_list = []

    for record in event['Records']:
        sub_log_json = base64.b64decode(record["kinesis"]["data"])
        sub_log_json = convert_log_to_json(sub_log_json)
        sub_log_json = json.dumps(sub_log_json)

        _log_list.append(sub_log_json)

    main_log_json = OrderedDict()
    main_log_json["name"] = "awslog"+get_now_timestamp()
    main_log_json["logs"] = _log_list

    _firehose_client = get_client("firehose", _FIREHOST_ENDPOINT_URL, _AWS_REGION)
    _res_put_firehose = _firehose_client.put_record(
                            DeliveryStreamName=_FIREHOSE_STREAM_NAME,
                            Record={"Data": json.dumps(main_log_json, ensure_ascii=False)}
                        )

    print("[Log] End Lambda Message: ", _res_put_firehose)

    return {
        "message": _res_put_firehose
    }


def get_now_timestamp():
    _dt_timestamp = datetime.datetime.now()
    _dt_timestamp = _dt_timestamp.strftime('%Y%m%d%H%M%S')
    return _dt_timestamp


def convert_log_to_json(str_log_line):
    # Ready for json data
    str_log_line = str_log_line.decode()
    str_log_line = str_log_line.replace('\\n"', '')
    str_log_line = str_log_line.replace('\\', '')

    # regular expression
    regex_host = r'\"(?P<host>.*?)'
    regex_space = r'\s'
    regex_identity = r'(?P<identity>.*)'
    regex_user = r'(?P<user>\S+)'
    regex_time = r'(?P<time>\[.*?\])'
    regex_request = r'\"(?P<request>.*?)\"'
    regex_status = r'(?P<status>\d{3})'
    regex_size = r'(?P<size>\S+)'
    regex_refer = r'\"(?P<referrer>.*?)\"'
    regex_user_agent = r'\"(?P<user_agent>.+)\"'

    regex = regex_host + regex_space + regex_identity + regex_space + regex_user + regex_space + regex_time + regex_space + regex_request + regex_space
    regex += regex_status + regex_space + regex_size + regex_space + regex_refer + regex_space + regex_user_agent

    match_data = re.search(regex, str_log_line)

    sub_log_json = OrderedDict()
    sub_log_json["host"] = match_data.group('host')
    sub_log_json["time"] = match_data.group('time')
    sub_log_json["request"] = match_data.group('request')
    sub_log_json["status"] = match_data.group('status')
    sub_log_json["size"] = match_data.group('size')
    sub_log_json["referrer"] = match_data.group('referrer')
    sub_log_json["user_agent"] = match_data.group('user_agent')

    return sub_log_json


def get_client(aws_service, endpoint_url, region_name):
    _aws_service_client = boto3.client(aws_service,
                                       endpoint_url=endpoint_url,
                                       use_ssl=False,
                                       region_name=region_name)

    return _aws_service_client