import threading
from handlers import *
from utils import *
from config import *


class LogPipeline():

    def __init__(self, cls):
        # common
        self._gubn = cls._GUBN
        self._account_number = cls._ACCOUNT_NUMBER
        self._aws_region = cls._AWS_REGION
        self._copy_source_path = cls._COPY_SOURCE_PATH
        self._copy_destination_path = cls._COPY_DESTINATION_PATH
        self._localstack_ip = cls._LOCALSTACK_IP
        self._nginx_access_log_path = cls._NGINX_ACCESS_LOG_PATH
        self._nginx_work_log_path = cls._NGINX_WORK_LOG_PATH
        self._nginx_access_log_file_nm = cls._NGINX_ACCESS_LOG_FILE_NM
        self._nginx_work_flog_file_nm = cls._NGINX_WORK_LOG_FILE_NM
        self._nginx_access_log_full_path = cls._NGINX_ACCESS_LOG_FULL_PATH
        self._nginx_work_log_full_path = cls._NGINX_WORK_LOG_FULL_PATH
        self._log_period = cls._LOG_PERIOD
        # aws s3
        self._s3_bucket_name = cls._S3_BUCKET_NAME
        self._s3_prefix  = cls._S3_PREFIX
        self._s3_endpoint_url = cls._S3_ENDPOINT_URL
        # aws kinesis-datastream
        self._data_stream_name = cls._DATA_STREAM_NAME
        self._data_stream_endpoint_url = cls._DATA_STREAM_ENDPOINT_URL
        self._consumer_name = cls._CONSUMER_NAME
        # aws kinesis-firehose
        self._firehose_stream_name = cls._FIREHOSE_STREAM_NAME
        self._firehose_endpoint_url = cls._FIREHOST_ENDPOINT_URL
        # aws lambda
        self._lambda_func_name = cls._LAMBDA_FUNC_NAME
        self._lambda_endpoint_url = cls._LAMBDA_ENDPOINT_URL
        self._lambda_zip_path = cls._LAMBDA_ZIP_PATH
        # aws iam
        self._iam_name = cls._IAM_NAME
        self._iam_endpoint_url = cls._IAM_ENDPOINT_URL
        # aws cloudwatch & logs
        self._cw_endpoint_url = cls._CW_ENDPOINT_URL
        self._cw_logs_endpoint_url = cls._CW_LOGS_ENDPOINT_URL

    def start_log_pipeline(self):
        Utils.create_utils(self)
        IamHandler.create_aws_iam(self)
        S3Handler.create_aws_s3(self)
        KinesisDataStreamHandler.create_kinesis_data_stream(self)
        KinesisFirehoseHandler.create_kinesis_firehose(self)
        LambdaHandler.create_aws_lambda(self)
        CloudWatchHandler.create_cloudwatch_logs(self)

    def pre_process_thread(self):
        _pre_precess_thread = threading.Timer(1, LogPipeline.pre_process_thread, args=[self])
        SplitLogsHandler.start_split_log(self)
        _pre_precess_thread.start()

    def producer_thread(self):
        _producer_thread = threading.Timer(1, LogPipeline.producer_thread, args=[self])
        KinesisDataStreamHandler.put_log(self)
        _producer_thread.start()


def main():
    log_pipeline = LogPipeline(Config)
    log_pipeline.start_log_pipeline()
    log_pipeline.pre_process_thread()
    log_pipeline.producer_thread()

if __name__ == "__main__":
    main()