# coding: utf-8
# -------------------------------------------------------------------
# aapanel
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 aapanel(http://www.aapanel.com) All rights reserved.
# -------------------------------------------------------------------
# Author: miku <wzz@bt.cn>
# -------------------------------------------------------------------

import hashlib
import json
import os
import sys
import time
import warnings

if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")
if "/www/server/panel/class_v2" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class_v2")
if "/www/server/panel" not in sys.path:
    sys.path.insert(0, "/www/server/panel")

os.chdir("/www/server/panel")
import public

warnings.filterwarnings("ignore", category=SyntaxWarning)


class BaseUtil:
    INITIAL_TASK_PROGRESS = 5
    INITIAL_TASK_STATE_MAX_AGE = 300

    def __init__(self):
        self.base_path = '/www/backup/backup_restore'
        if not os.path.exists(self.base_path):
            public.ExecShell('mkdir -p {}'.format(self.base_path))
        self.history_path = '/www/backup/backup_restore/history'
        self.history_info_path = '/www/backup/backup_restore/history/info'
        self.nginx_bin_path = '/www/server/nginx/sbin/nginx'
        self.overwrite = 0  # 0 跳过, 1 覆盖
        self.auto_exit = 0  # 异常打断, 默认0

    def print_log(self, log: str, type: str):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')
        log = "[{}] {}".format(time_str, log)
        log_file = self.base_path + '/{}.log'.format(type)
        public.writeFile(log_file, log + "\n", 'a+')

    def get_initial_task_message(self) -> str:
        return public.lang("Initializing task...")

    def get_initial_task_state_file(self, task_type: str) -> str:
        return os.path.join(self.base_path, "{}_init.json".format(task_type))

    def write_initial_task_state(self, task_type: str, timestamp=None, reset_log: bool = False):
        if task_type not in ("backup", "restore"):
            return
        if not os.path.exists(self.base_path):
            public.ExecShell('mkdir -p {}'.format(self.base_path))

        log_file = os.path.join(self.base_path, "{}.log".format(task_type))
        if reset_log:
            public.WriteFile(log_file, "")

        message = self.get_initial_task_message()
        self.print_log(message, task_type)
        state_data = {
            "timestamp": str(timestamp) if timestamp is not None else "",
            "create_time": int(time.time()),
            "progress": self.INITIAL_TASK_PROGRESS,
            "msg": message,
        }
        public.WriteFile(self.get_initial_task_state_file(task_type), json.dumps(state_data))

    def get_initial_task_state(self, task_type: str):
        state_file = self.get_initial_task_state_file(task_type)
        if not os.path.exists(state_file):
            return None
        try:
            state_data = json.loads(public.ReadFile(state_file) or "{}")
            create_time = int(state_data.get("create_time", 0))
            if create_time and create_time + self.INITIAL_TASK_STATE_MAX_AGE < int(time.time()):
                os.remove(state_file)
                return None
            return state_data
        except:
            return None

    def clear_initial_task_state(self, task_type: str):
        state_file = self.get_initial_task_state_file(task_type)
        try:
            if os.path.exists(state_file):
                os.remove(state_file)
        except:
            pass

    def build_initial_task_progress(self, task_type: str, timestamp=None, log_data=None):
        message = self.get_initial_task_message()
        if not log_data:
            log_data = "[{}] {}\n".format(time.strftime('%Y-%m-%d %H:%M:%S'), message)
        return {
            "task_type": task_type,
            "task_status": 1,
            "data_type": "init",
            "name": message,
            "data_backup_status": 1,
            "progress": self.INITIAL_TASK_PROGRESS,
            "msg": message,
            "exec_log": log_data,
            "timestamp": timestamp,
        }

    def replace_log(self, old_str: str, new_str: str, type: str):
        log_file = self.base_path + '/{}.log'.format(type)
        log_data = public.ReadFile(log_file)
        if old_str in log_data:
            log_data = log_data.replace(old_str, new_str)
            public.WriteFile(log_file, log_data)

    def get_file_sha256(self, file_path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)  # 先读取再判断
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_free_space(self):
        result = {}
        path = "/www"
        diskstat = os.statvfs(path)
        free_space = diskstat.f_bavail * diskstat.f_frsize
        # total_space = diskstat.f_blocks * diskstat.f_frsize
        # used_space = (diskstat.f_blocks - diskstat.f_bfree) * diskstat.f_frsize
        result['free_space'] = free_space
        return result

    def get_file_size(self, path: str) -> int:
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                return int(public.ExecShell(f"du -sb {path}")[0].split("\t")[0])
            return 0
        except:
            return 0

    def format_size(self, size: int):
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f}KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / 1024 / 1024:.2f}MB"
        elif size < 1024 * 1024 * 1024 * 1024:
            return f"{size / 1024 / 1024 / 1024:.2f}GB"
        else:
            return f"{size / 1024 / 1024 / 1024 / 1024:.2f}TB"

    def web_config_check(self):
        if os.path.exists(self.nginx_bin_path):
            nginx_conf_test = public.ExecShell("ulimit -n 8192 ;{} -t".format(self.nginx_bin_path))[1]
            if "successful" in nginx_conf_test:
                return {
                    "status": True,
                    "msg": None
                }
            else:
                return {
                    "status": False,
                    "msg": public.lang("Nginx Configuration file error, inventory!:{}".format(nginx_conf_test))
                }
        else:
            return {
                "status": True,
                "msg": None
            }
