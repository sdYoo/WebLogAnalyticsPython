# -*- coding: utf-8 -*-
import json
from utils import *


class KinesisFirehoseHandler():

    def create_kinesis_firehose(self):
        _firehose_client = Utils.get_client(self, "firehose", self._firehose_endpoint_url, self._aws_region)
        _exist_result = Utils.exist_kinesis_firehose(_firehose_client, self._firehose_stream_name)
        print(_exist_result)
        if _exist_result:
            KinesisFirehoseHandler.delete_firehose_stream(self, _firehose_client)

        _response = KinesisFirehoseHandler.create_s3_delivery_stream(self, _firehose_client)

        return _response

    def create_s3_delivery_stream(self, _firehose_client):
        _created_firehose = _firehose_client.create_delivery_stream(
                DeliveryStreamName=self._firehose_stream_name,
                DeliveryStreamType="DirectPut",
                S3DestinationConfiguration={
                    "RoleARN": "arn:aws:iam::{}:role/adminRole".format(self._account_number),
                    "BucketARN": "arn:aws:s3:::{}".format(self._s3_bucket_name),
                    "Prefix": self._s3_prefix,
                    "BufferingHints": {
                        'SizeInMBs': 5,
                        'IntervalInSeconds': 60
                    },
                    "CompressionFormat": "UNCOMPRESSED",
                    "EncryptionConfiguration": {
                        "NoEncryptionConfig": "NoEncryption"
                    },
                    "CloudWatchLoggingOptions": {
                        "Enabled": False
                    }
                },
            )

        return _created_firehose

    def delete_firehose_stream(self, _firehose_client):
        _response = _firehose_client.delete_delivery_stream(
                        DeliveryStreamName=self._firehose_stream_name,
                        AllowForceDelete=False
                    )
        return _response

    def put_record_to_delivery_stream(self, _firehose_client, main_log_json):
        _res_put_firehose = ""
        try:
            _res_put_firehose = _firehose_client.put_record(
                            DeliveryStreamName=self._firehose_stream_name,
                            Record={"Data": json.dumps(main_log_json, ensure_ascii=False)}
                        )
        except Exception as error_message:
            print("[Log] Error: ", error_message)

        return _res_put_firehose