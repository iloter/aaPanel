# coding: utf-8
# -------------------------------------------------------------------
# aapanel
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 aapanel(http://www.aapanel.com) All rights reserved.
# -------------------------------------------------------------------
# Author: miku <wzz@bt.cn>
# -------------------------------------------------------------------
import json
import os
import sys
import warnings
import ast

if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")
if "/www/server/panel/class_v2" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class_v2")
if "/www/server/panel" not in sys.path:
    sys.path.insert(0, "/www/server/panel")

import public

warnings.filterwarnings("ignore", category=SyntaxWarning)


class ConfigManager:
    DEFAULT_BACKUP_DATA = [
        "soft", "site", "wp_tools", "ssl", "database", "ftp",
        "crontab", "vmail", "firewall", "plugin"
    ]
    SUPPORTED_BACKUP_DATA = set(DEFAULT_BACKUP_DATA + ["ssh", "node"])

    def __init__(self):
        self.base_path = '/www/backup/backup_restore'
        self.bakcup_task_json = self.base_path + '/backup_task.json'

    @staticmethod
    def _parse_list_value(value, default=None):
        if value is None:
            return list(default) if isinstance(default, list) else default
        if isinstance(value, list):
            return value
        if isinstance(value, tuple) or isinstance(value, set):
            return list(value)
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            for parser in (json.loads, ast.literal_eval):
                try:
                    result = parser(value)
                    if isinstance(result, (list, tuple, set)):
                        return list(result)
                    return [result]
                except:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return [value]

    def normalize_backup_data(self, value=None):
        data = self._parse_list_value(value, self.DEFAULT_BACKUP_DATA)
        if data is None:
            data = list(self.DEFAULT_BACKUP_DATA)
        if not data:
            return []
        normalized = []
        for item in data:
            key = str(item).strip()
            if not key:
                continue
            key = key.lower()
            if key == "all":
                return list(self.DEFAULT_BACKUP_DATA)
            if key in self.SUPPORTED_BACKUP_DATA and key not in normalized:
                normalized.append(key)
        return normalized

    def normalize_backup_id_list(self, value=None, default_all=True):
        default = ["ALL"] if default_all else []
        data = self._parse_list_value(value, default)
        if data is None:
            data = default
        result = []
        for item in data:
            if item is None:
                continue
            if isinstance(item, str):
                text = item.strip()
                if not text:
                    continue
                if text.upper() == "ALL":
                    return ["ALL"]
                try:
                    item = int(text)
                except:
                    item = text
            result.append(item)
        return result

    @staticmethod
    def backup_type_enabled(backup_data, *types):
        enabled = set(str(item).lower() for item in backup_data)
        return any(str(item).lower() in enabled for item in types)

    def get_backup_conf(self, timestamp):
        if not os.path.exists(self.bakcup_task_json):
            return None
        task_json_data = json.loads(public.ReadFile(self.bakcup_task_json))
        data = [item for item in task_json_data if str(item['timestamp']) == timestamp]
        if not data:
            return None
        return data[0]

    def save_backup_conf(self, timestamp, data):
        if not os.path.exists(self.bakcup_task_json):
            return None
        task_json_data = json.loads(public.ReadFile(self.bakcup_task_json))
        for item in task_json_data:
            if str(item['timestamp']) == timestamp:
                item.update(data)
                break
        public.WriteFile(self.bakcup_task_json, json.dumps(task_json_data))

    def get_backup_data_list(self, timestamp):
        data_list_json = self.base_path + '/{timestamp}_backup/backup.json'.format(timestamp=timestamp)
        if not os.path.exists(data_list_json):
            return None
        data_list_data = json.loads(public.ReadFile(data_list_json))
        return data_list_data

    def update_backup_data_list(self, timestamp, data_list):
        data_list_json = self.base_path + '/{timestamp}_backup/backup.json'.format(timestamp=timestamp)
        try:
            # 读取现有配置
            if os.path.exists(data_list_json):
                current_data = json.loads(public.ReadFile(data_list_json))
                # 更新数据
                current_data.update(data_list)
                data_list = current_data

            # 写入更新后的配置
            public.WriteFile(data_list_json, json.dumps(data_list))
            return True
        except Exception as e:
            public.print_log("update_backup_data_list error: {}".format(str(e)))
            return False

    def get_restore_data_list(self, timestamp):
        data_list_json = self.base_path + '/{timestamp}_backup/restore.json'.format(timestamp=timestamp)
        if not os.path.exists(data_list_json):
            return None
        data_list_data = json.loads(public.ReadFile(data_list_json))
        return data_list_data

    def update_restore_data_list(self, timestamp, data_list):
        data_list_json = self.base_path + '/{timestamp}_backup/restore.json'.format(timestamp=timestamp)
        # 读取现有配置
        try:
            # 读取现有配置
            if os.path.exists(data_list_json):
                current_data = json.loads(public.ReadFile(data_list_json))
                # 更新数据
                current_data.update(data_list)
                data_list = current_data

            # 写入更新后的配置
            public.WriteFile(data_list_json, json.dumps(data_list))
            return True
        except Exception as e:
            public.print_log("update_restore_data_list error: {}".format(str(e)))
            return False


if __name__ == '__main__':
    # 获取命令行参数
    if len(sys.argv) < 3:
        print("Usage: btpython config_manager.py <method> <timestamp>")
        sys.exit(1)
    method_name = sys.argv[1]  # 方法名
    timestamp = sys.argv[2]  # IP地址
    config = ConfigManager()  # 实例化对象
    if hasattr(config, method_name):  # 检查方法是否存在
        method = getattr(config, method_name)  # 获取方法
        method(timestamp)  # 调用方法
    else:
        print(f"Error: method '{method_name}' not found")
