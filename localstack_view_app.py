from handlers import *
from config import *
from flask import Flask, render_template

app = Flask(__name__)


def get_logs(_cw_client):
    _res_logs = _cw_client.filter_log_events(logGroupName="/aws/lambda/weblog_convert_lambda")
    return _res_logs


def get_client(_aws_service, _endpoint_url, _region_name):
    _aws_service_client = boto3.client(_aws_service,
                                       endpoint_url=_endpoint_url,
                                       use_ssl=False,
                                       region_name=_region_name)
    return _aws_service_client

def get_cloudwatch_logs_list():
    _cw_client = get_client("logs", Config._CW_LOGS_ENDPOINT_URL, Config._AWS_REGION)
    _res_logs = get_logs(_cw_client)

    _cw_list = []
    _row_num = 1

    for log_line in _res_logs['events']:
        _cw_list.append(
            {
                "rowNumber":_row_num,
                "eventId":log_line["eventId"],
                "logStreamName":log_line["logStreamName"],
                "message":log_line["message"]
            }
        )
        _row_num = _row_num+1

    return _cw_list

def get_s3_bucket_list():
    _s3_client = get_client("s3", Config._S3_ENDPOINT_URL, Config._AWS_REGION)
    _paginator = _s3_client.get_paginator('list_objects')
    _page_iterator = _paginator.paginate(Bucket=Config._S3_BUCKET_NAME)

    _s3_list = []
    _row_num = 1

    for _page in _page_iterator:
        for _obj in _page['Contents']:
            _s3_list.append(
                {
                    "rowNumber":_row_num,
                    "bucketName":Config._S3_BUCKET_NAME,
                    "prefix":_obj["Key"]
                }
            )
            _row_num = _row_num + 1

    return _s3_list

def get_lambda_list():
    _lambda_client = get_client("lambda", Config._S3_ENDPOINT_URL, Config._AWS_REGION)
    _lambda_list = _lambda_client.list_functions()
    return _lambda_list

@app.route('/list')
def select_aws_service():
    _aws_list = {}

    _cw_list = get_cloudwatch_logs_list()
    _s3_list = get_s3_bucket_list()

    _aws_list["cw_list"] = _cw_list
    _aws_list["s3_list"] = _s3_list

    return render_template('localstack_viewer.html', aws_list=_aws_list)


if __name__ == '__main__':
    app.run('0.0.0.0',7001)
