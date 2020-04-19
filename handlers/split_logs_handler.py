# -*- coding: utf-8 -*-
import time
import os
from utils import *
from config import *


class SplitLogsHandler:

    def start_split_log(self):
        SplitLogsHandler.split_log_file(self)

    def split_log_file(self):
        _max_time = time.time()+( 60 * self._log_period)

        _origin_file = self._nginx_access_log_full_path
        _copy_file_path = self._nginx_work_log_path

        _now_time = Utils.get_now_timestamp(self)
        _copy_file = self._nginx_work_log_full_path+"."+_now_time

        try:
            if not (os.path.isdir(_copy_file_path)):
                os.makedirs(os.path.join(_copy_file_path))
        except OSError as error_message:
            print("[Log]".format(error_message))

        time.sleep(0.5)

        _n_cnt = 0
        _og_file = open(_origin_file, 'r')
        for _file_line in _og_file:
            _n_cnt = _n_cnt + 1

        # print("{} ==== {}".format(_n_cnt, Config._G_NGINX_LOG_LINE))
        if _n_cnt == Config._G_NGINX_LOG_LINE:
            print("[Log] logs does not exist")
            return ""

        with open(_origin_file, 'r') as _org_file, open(_copy_file, 'w') as _cp_file:
            for _line_number, _file_line in enumerate(_org_file):

                if time.time() > _max_time:
                    print("[Log] Time out: {}".format())
                    break

                if _line_number == Config._G_NGINX_LOG_LINE:
                    _cp_file.write(_file_line)
                    Config._G_NGINX_LOG_LINE = Config._G_NGINX_LOG_LINE + 1