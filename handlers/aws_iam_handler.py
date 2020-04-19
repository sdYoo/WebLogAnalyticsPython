# -*- coding: utf-8 -*-
import json
from utils import *


class IamHandler():

    def create_aws_iam(self):
        _iam_client = Utils.get_client(self, "iam", self._iam_endpoint_url, self._aws_region)

        try:
            _exist_result = _iam_client.get_role(
                                RoleName='adminRole'
                            )
        except ClientError as error_message:
                print("Unexpected error: {}".format(error_message))
                _exist_result = None

        if _exist_result is None:
            _iam_policy = IamHandler.create_iam_policy(self)
            _exist_result = IamHandler.create_iam_role(self, _iam_client, _iam_policy)

        print("[Log] IAM: ", _exist_result.get("Role").get("Arn"))

    def create_iam_role(self, _iam_client, _iam_policy):

        _created_iam_role = _iam_client.create_role(
                                Path='/',
                                RoleName='adminRole',
                                AssumeRolePolicyDocument=_iam_policy,
                                Description='adminRole',
                            )

        return _created_iam_role

    def create_iam_policy(self):

        _role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1111111111111",
                    "Action": "*",
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        })

        return _role_policy_document