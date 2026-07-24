# coding: utf-8
# -------------------------------------------------------------------
# aapanel
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 aapanel(http://www.aapanel.com) All rights reserved.
# -------------------------------------------------------------------
# Author: miku <wzz@bt.cn>
# -------------------------------------------------------------------
import datetime
import json
import os
import re
import sys
import time
import warnings

if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")
if "/www/server/panel/class_v2" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class_v2")
if "/www/server/panel" not in sys.path:
    sys.path.insert(0, "/www/server/panel")

import public
from mod.project.backup_restore.modules.site_module import SiteModule
from mod.project.backup_restore.modules.database_module import DatabaseModule
from mod.project.backup_restore.modules.ftp_module import FtpModule
from mod.project.backup_restore.modules.crontab_module import CrontabModule
from mod.project.backup_restore.modules.ssh_module import SshModule
from mod.project.backup_restore.modules.firewall_module import FirewallModule
from mod.project.backup_restore.modules.plugin_module import PluginModule
from mod.project.backup_restore.modules.mail_module import MailModule
from mod.project.backup_restore.modules.ssl_model import SSLModel
try:
    from mod.project.backup_restore.modules.node_module import NodeModule
except:
    NodeModule = None

warnings.filterwarnings("ignore", category=SyntaxWarning)


class BackupManager(SiteModule, DatabaseModule, FtpModule, SSLModel):
    def __init__(self):
        super().__init__()
        self.base_path = '/www/backup/backup_restore'
        self.bakcup_task_json = self.base_path + '/backup_task.json'
        self.backup_log_file = self.base_path + '/backup.log'
        self.backup_pl_file = self.base_path + '/backup.pl'
        self.backup_success_file = self.base_path + '/success.pl'
        self.backup_save_config = self.base_path + '/backup_save_config.json'
        self.history_log_path = '/www/backup/backup_restore/history/log'
        self.history_info_path = '/www/backup/backup_restore/history/info'
        self.migrate_backup_info_path = '/www/backup/backup_restore/migrate_backup_info.json'

    def get_local_backup(self, get=None):
        backup_list = []
        # 修复 备份目录不存在
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)

        if os.path.exists(self.bakcup_task_json):
            # 修复 JSON解析崩溃
            content = public.ReadFile(self.bakcup_task_json)
            if content and content.strip():
                try:
                    backup_list = json.loads(content)
                except:
                    backup_list = []

        file_names = os.listdir(self.base_path)
        pattern = re.compile(r"\d{8}-\d{4}_\d+_backup\.tar\.gz")
        matched_files = [f for f in file_names if pattern.match(f)]
        for file in matched_files:
            if "upload.tmp" in file:
                continue
            file_timestamp = file.split('_')[1]
            matched = any(item["timestamp"] == int(file_timestamp) for item in backup_list)
            if not matched:
                done_time = datetime.datetime.fromtimestamp(int(file_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                # file_size = public.ExecShell("du -sb /www/backup/backup_restore/{}".format(file))[0].split("\t")[0]
                file_conf = {
                    'backup_name': str(file),
                    'timestamp': int(file_timestamp),
                    'create_time': done_time,
                    'backup_time': done_time,
                    'backup_file': self.base_path + "/" + file,
                    'storage_type': "local",
                    'auto_exit': 0,
                    'restore_status': 0,
                    'backup_status': 2,
                    'backup_path': self.base_path + "/" + file,
                    'done_time': done_time,
                    'backup_file_size': str(self.get_file_size(self.base_path + "/" + file)),
                    'backup_file_sha256': self.get_file_sha256(self.base_path + "/" + file),
                    'backup_count': {
                        "success": None,
                        "failed": None,
                        "total_time": None
                    },
                }
                backup_list.append(file_conf)

        if os.path.exists(self.migrate_backup_info_path):
            migrate_backup_info = json.loads(public.ReadFile(self.migrate_backup_info_path))
            backup_list.append(migrate_backup_info)
            public.ExecShell("rm -f {}".format(self.migrate_backup_info_path))

        for backup_conf in backup_list:
            if not isinstance(backup_conf, dict) or str(backup_conf.get("backup_status")) != "2":
                continue
            timestamp = backup_conf.get("timestamp")
            if not timestamp:
                continue
            backup_json_path = os.path.join(self.base_path, "{}_backup".format(timestamp), "backup.json")
            history_info_file = os.path.join(self.history_info_path, "{}_backup.info".format(timestamp))
            for info_file in (backup_json_path, history_info_file):
                if not os.path.exists(info_file):
                    continue
                try:
                    backup_info = json.loads(public.ReadFile(info_file) or "{}")
                    data_list = backup_info.get("data_list", {})
                    if not isinstance(data_list, dict):
                        continue
                    backup_count = {
                        "success": self.count_backup_status(data_list, 2),
                        "failed": self.count_backup_status(data_list, 3),
                    }
                    backup_conf["backup_count"] = backup_count
                    if backup_info.get("backup_count") != backup_count:
                        backup_info["backup_count"] = backup_count
                        public.WriteFile(info_file, json.dumps(backup_info))
                    break
                except:
                    continue

        public.WriteFile(self.bakcup_task_json, json.dumps(backup_list))
        return backup_list

    def get_backup_file_msg(self, timestamp):
        import tarfile
        backup_file = str(timestamp) + "_backup.tar.gz"
        print(backup_file)
        file_names = os.listdir(self.base_path)
        for file in file_names:
            if backup_file in file:
                backup_file = file
        path = self.base_path + "/" + backup_file
        path_data = {}
        if not os.path.exists(path):
            return path_data
        try:
            with tarfile.open(path, 'r:gz') as tar:
                # 提前获取文件列表
                members = tar.getnames()
                # 提取备份 JSON 配置
                if '{}_backup/backup.json'.format(timestamp) in members:
                    json_file_name = '{}_backup/backup.json'.format(timestamp)
                    json_file = tar.extractfile(json_file_name)
                    json_content = json_file.read().decode('utf-8')
                    path_data['config'] = json.loads(json_content)

                # 提取备份日志文件
                if '{}_backup/backup.log'.format(timestamp) in members:
                    log_file_name = '{}_backup/backup.log'.format(timestamp)
                    log_file = tar.extractfile(log_file_name)
                    log_content = log_file.read().decode('utf-8')
                    path_data['log'] = log_content + path + "\n" + public.lang("Packaging completed")
        except:
            return False

        # path_data['server_config']=self.get_server_config()
        # path_data['backup_path_size']=25256044
        # path_data['free_size'] = self.get_free_space()['free_space']

        self.history_log_path = '/www/backup/backup_restore/history/log'
        self.history_info_path = '/www/backup/backup_restore/history/info'
        if not os.path.exists(self.history_log_path):
            public.ExecShell("mkdir -p {}".format(self.history_log_path))
        if not os.path.exists(self.history_info_path):
            public.ExecShell("mkdir -p {}".format(self.history_info_path))

        try:
            public.WriteFile(self.history_log_path + "{}_backup.log".format(timestamp), path_data['log'])
        except:
            pass
        try:
            public.WriteFile(self.history_info_path + "/{}_backup.info".format(timestamp),
                             json.dumps(path_data['config']))
        except:
            return False

        try:
            backup_task_info = self.get_backup_conf(timestamp)
            hitory_info = json.loads(public.ReadFile(self.history_info_path + "/{}_backup.info".format(timestamp)))
            hitory_info['create_time'] = backup_task_info['create_time']
            hitory_info['backup_time'] = backup_task_info['backup_time']
            hitory_info['backup_file'] = backup_task_info['backup_file']
            hitory_info['backup_path'] = backup_task_info['backup_path']
            hitory_info['done_time'] = backup_task_info['done_time']
            hitory_info['total_time'] = backup_task_info['total_time']
            hitory_info['backup_file_size'] = backup_task_info['backup_file_size']
            hitory_info['backup_file_sha256'] = backup_task_info['backup_file_sha256']
            public.WriteFile(self.history_info_path + "/{}_backup.info".format(timestamp), json.dumps(hitory_info))
        except:
            pass

        return True

    def add_backup_task(self, timestamp: int):
        """
        构造备份初始配置
        """
        backup_path = self.base_path + '/{timestamp}_backup/'.format(timestamp=timestamp)
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        backup_conf = self.get_backup_conf(timestamp)
        if not backup_conf:
            print(public.lang("Backup configuration file does not exist"))
            return public.returnMsg(False, public.lang("Backup configuration file does not exist"))

        backup_data_list = self.normalize_backup_data(backup_conf.get("backup_data"))
        backup_conf['backup_data'] = backup_data_list
        backup_conf['site_id'] = self.normalize_backup_id_list(backup_conf.get("site_id"))
        wp_site_id_value = backup_conf.get("wp_site_id")
        if wp_site_id_value is None:
            wp_site_id_value = backup_conf.get("wp_id")
        backup_conf['wp_site_id'] = self.normalize_backup_id_list(wp_site_id_value)
        backup_conf.pop("wp_id", None)
        backup_conf['database_id'] = self.normalize_backup_id_list(backup_conf.get("database_id"))
        backup_conf['data_list'] = {}
        if self.backup_type_enabled(backup_data_list, "soft"):
            backup_conf['data_list']['soft'] = self.get_soft_data(timestamp, packet=True)
        else:
            backup_conf['data_list']['soft'] = {}

        if self.backup_type_enabled(backup_data_list, "site", "wp_tools"):
            backup_conf['data_list']['site'] = self.get_site_backup_conf(timestamp)
        else:
            backup_conf['data_list']['site'] = []

        if self.backup_type_enabled(backup_data_list, "ssl"):
            backup_conf['data_list']['ssl'] = self.get_ssl_backup_conf(timestamp)
        else:
            backup_conf['data_list']['ssl'] = {"ssl_list": [], "provider_list": []}

        if self.backup_type_enabled(backup_data_list, "database"):
            backup_conf['data_list']['database'] = self.get_database_backup_conf(timestamp)
        else:
            backup_conf['data_list']['database'] = []

        if self.backup_type_enabled(backup_data_list, "ftp"):
            backup_conf['data_list']['ftp'] = self.backup_ftp_data(timestamp)
        else:
            backup_conf['data_list']['ftp'] = []

        backup_conf['backup_status'] = 1
        self.save_backup_conf(str(timestamp), backup_conf)
        public.WriteFile(backup_path + 'backup.json', json.dumps(backup_conf))

    def backup_data(self, timestamp: int):
        if os.path.exists(self.backup_log_file):
            public.ExecShell("rm -f {}".format(self.backup_log_file))

        if os.path.exists(self.backup_pl_file):
            print(public.lang("A backup process is already running!"))
            return public.returnMsg(False, public.lang("A backup process is already running!"))

        try:
            public.WriteFile(self.backup_pl_file, timestamp)
            self.write_initial_task_state("backup", timestamp)

            backup_conf = self.get_backup_conf(timestamp)
            if not backup_conf:
                return public.returnMsg(False, public.lang("Backup configuration file does not exist"))
            backup_data_list = self.normalize_backup_data(backup_conf.get("backup_data"))
            backup_conf['backup_data'] = backup_data_list
            backup_conf['site_id'] = self.normalize_backup_id_list(backup_conf.get("site_id"))
            wp_site_id_value = backup_conf.get("wp_site_id")
            if wp_site_id_value is None:
                wp_site_id_value = backup_conf.get("wp_id")
            backup_conf['wp_site_id'] = self.normalize_backup_id_list(wp_site_id_value)
            backup_conf.pop("wp_id", None)
            backup_conf['database_id'] = self.normalize_backup_id_list(backup_conf.get("database_id"))
            backup_conf['backup_status'] = 1
            self.save_backup_conf(timestamp, backup_conf)
            start_time = int(time.time())
            # 构造备份初始配置
            self.add_backup_task(timestamp)
            self.clear_initial_task_state("backup")
            try:
                if self.backup_type_enabled(backup_data_list, "site", "wp_tools"):
                    self.backup_site_data(timestamp)
            except:
                pass

            try:
                if self.backup_type_enabled(backup_data_list, "database"):
                    self.backup_database_data(timestamp)
            except:
                pass

            try:
                if self.backup_type_enabled(backup_data_list, "ssl"):
                    self.backup_ssl_data(timestamp)
            except:
                pass

            try:
                if self.backup_type_enabled(backup_data_list, "crontab"):
                    CrontabModule().backup_crontab_data(timestamp)
            except:
                pass

            # TODO: 存在问题，下个版本修复
            # try:
            #     SshModule().backup_ssh_data(timestamp)
            # except:
            #     pass

            try:
                if self.backup_type_enabled(backup_data_list, "ssh"):
                    SshModule().backup_ssh_data(timestamp)
            except Exception as e:
                public.print_log("backup ssh error: {}".format(str(e)))

            try:
                if self.backup_type_enabled(backup_data_list, "firewall"):
                    FirewallModule().backup_firewall_data(timestamp)
            except:
                pass

            try:
                if self.backup_type_enabled(backup_data_list, "vmail"):
                    MailModule().backup_vmail_data(timestamp)
            except:
                pass

            try:
                if self.backup_type_enabled(backup_data_list, "plugin"):
                    PluginModule().backup_plugin_data(timestamp)
            except:
                pass

            try:
                if NodeModule is not None and self.backup_type_enabled(backup_data_list, "node"):
                    NodeModule().backup_node_data(timestamp)
            except Exception as e:
                public.print_log("backup node error: {}".format(str(e)))

            try:
                self.write_backup_data(timestamp)
            except:
                pass

            end_time = int(time.time())
            done_time = datetime.datetime.fromtimestamp(int(end_time)).strftime('%Y-%m-%d %H:%M:%S')
            total_time = end_time - start_time

            backup_conf = self.get_backup_conf(timestamp)
            backup_conf['backup_status'] = 2
            backup_conf['done_time'] = done_time
            backup_conf['total_time'] = total_time

            self.save_backup_conf(timestamp, backup_conf)
            self.sync_backup_info(timestamp)

            public.WriteFile(self.backup_success_file, timestamp)
            public.ExecShell("rm -f {}".format(self.backup_pl_file))
            self.create_history_file(timestamp)
        except Exception as e:
            return public.returnMsg(False, public.lang(f"something went wrong! Error: {str(e)}"))
        finally:
            self.clear_initial_task_state("backup")
            if os.path.exists(self.backup_pl_file):
                public.ExecShell("rm -f {}".format(self.backup_pl_file))

    def create_history_file(self, timestamp):
        if not os.path.exists(self.history_log_path):
            public.ExecShell("mkdir -p {}".format(self.history_log_path))
        if not os.path.exists(self.history_info_path):
            public.ExecShell("mkdir -p {}".format(self.history_info_path))

        hitory_log_file = self.history_log_path + '/' + str(timestamp) + '_backup.log'
        history_info_file = self.history_info_path + '/' + str(timestamp) + '_backup.info'
        public.WriteFile(hitory_log_file, public.ReadFile("/www/backup/backup_restore/backup.log".format(timestamp)))
        public.WriteFile(history_info_file,
                         public.ReadFile("/www/backup/backup_restore/{}_backup/backup.json".format(timestamp)))

    def sync_backup_info(self, timestamp):
        backup_conf = self.get_backup_conf(timestamp)
        data_list = self.get_backup_data_list(timestamp)
        data_list['backup_status'] = backup_conf['backup_status']
        data_list['backup_file'] = backup_conf['backup_file']
        data_list['backup_file_sha256'] = backup_conf['backup_file_sha256']
        data_list['backup_file_size'] = backup_conf['backup_file_size']
        data_list['done_time'] = backup_conf['done_time']
        data_list['total_time'] = backup_conf['total_time']
        data_list['backup_count'] = backup_conf['backup_count']
        self.update_backup_data_list(timestamp, data_list)

    def count_backup_status(self, data, status_code):
        def json_count(file_path):
            try:
                content = public.ReadFile(file_path).strip()
                value = json.loads(content)
                return len(value) if isinstance(value, (list, dict)) else 0
            except:
                return 0

        def status_count(value):
            if isinstance(value, list):
                return sum(status_count(item) for item in value)
            if not isinstance(value, dict):
                return 0
            if "status" in value:
                return 1 if value.get("status") == status_code else 0
            return sum(status_count(item) for item in value.values())

        count = 0
        for category_key, category_data in data.items():
            if category_key == "crontab" and isinstance(category_data, dict):
                if category_data.get("status") == status_code:
                    count += json_count(category_data.get("crontab_json"))
            elif category_key == "firewall" and isinstance(category_data, dict):
                if category_data.get("status") == status_code:
                    count += 4
            elif category_key == "vmail" and isinstance(category_data, dict):
                if category_data.get("status") == status_code and category_data.get("vmail_backup_name"):
                    count += 1
            else:
                count += status_count(category_data)
        return count

    def write_backup_data(self, timestamp):
        self.print_log("====================================================", "backup")
        self.print_log(public.lang("Start compressing and packaging all data"), "backup")
        from datetime import datetime
        backup_conf = self.get_backup_conf(timestamp)

        backup_log_path = self.base_path + str(timestamp) + "_backup/"
        public.ExecShell('\\cp -rpa {} {}'.format(self.backup_log_file, backup_log_path))

        conf_data = json.loads((public.ReadFile("/www/backup/backup_restore/{}_backup/backup.json".format(timestamp))))
        status_2_count = self.count_backup_status(conf_data['data_list'], 2)
        status_3_count = self.count_backup_status(conf_data['data_list'], 3)

        dt_object = datetime.fromtimestamp(int(timestamp))
        file_time = dt_object.strftime('%Y%m%d-%H%M')
        tar_file_name = file_time + "_" + str(timestamp) + "_backup.tar.gz"
        conf_data['backup_status'] = 1
        conf_data["backup_count"] = {
            "success": status_2_count,
            "failed": status_3_count,
        }
        public.WriteFile("/www/backup/backup_restore/{}_backup/backup.json".format(timestamp), json.dumps(conf_data))

        public.ExecShell("cd /www/backup/backup_restore && tar -czvf {} {}_backup".format(tar_file_name, timestamp))
        file_size = public.ExecShell("du -sb /www/backup/backup_restore/{}".format(tar_file_name))[0].split("\t")[0]

        backup_conf["backup_status"] = 2
        backup_conf["backup_file"] = "/www/backup/backup_restore/" + tar_file_name
        backup_conf["backup_file_sha256"] = self.get_file_sha256("/www/backup/backup_restore/" + tar_file_name)
        backup_conf["backup_file_size"] = file_size
        backup_conf["backup_count"] = {}
        backup_conf["backup_count"]['success'] = status_2_count
        backup_conf["backup_count"]['failed'] = status_3_count
        storage_type = backup_conf['storage_type']

        backup_size = self.format_size(int(file_size))
        self.print_log(
            public.lang("Compression and packaging of all data completed. Data size: {}").format(backup_size),
            'backup'
        )
        self.print_log(public.lang("Backup completed. Backup file: {}").format(tar_file_name), "backup")
        self.print_log("====================================================", "backup")

        tar_file_name = "/www/backup/backup_restore/" + tar_file_name
        if storage_type != "local" and os.path.exists(tar_file_name):
            cloud_name_cn = "cloud storage"
            backup_conf["cloud_upload_status"] = 1
            backup_conf["cloud_storage"] = storage_type
            # public.print_log("[backup_restore] cloud upload start: timestamp={}, storage_type={}, file={}".format(timestamp, storage_type, tar_file_name))
            self.print_log(public.lang("Uploading backup file to cloud storage..."), "backup")
            try:
                from cloud_stora_upload_v2 import CloudStoraUpload
                _cloud = CloudStoraUpload()
                _cloud.run(storage_type)
                cloud_name_cn = _cloud.obj._title
                if int(file_size) > 100 * 1024 * 1024:
                    self.print_log(
                        public.lang("{} Uploading in chunks...").format(cloud_name_cn), "backup"
                    )
                else:
                    self.print_log(
                        public.lang("{} Uploading...").format(cloud_name_cn), "backup"
                    )

                backup_path = _cloud.obj.backup_path
                if not backup_path.endswith('/'):
                    backup_path += '/'
                upload_path = os.path.join(backup_path, "backup_restore", os.path.basename(tar_file_name))
                backup_conf["cloud_name"] = cloud_name_cn
                backup_conf["cloud_upload_path"] = upload_path
                if _cloud.cloud_upload_file(tar_file_name, upload_path):
                    backup_conf["cloud_upload_status"] = 2
                    # public.print_log("[backup_restore] cloud upload success: timestamp={}, storage_type={}, path={}".format(timestamp, storage_type, upload_path))
                    self.print_log(public.lang("Successfully uploaded to {}").format(cloud_name_cn), "backup")
                else:
                    backup_conf["cloud_upload_status"] = 3
                    # public.print_log("[backup_restore] cloud upload failed: timestamp={}, storage_type={}, path={}".format(timestamp, storage_type, upload_path))
                    self.print_log(public.lang("Failed to upload to {}").format(cloud_name_cn), "backup")
            except Exception as e:
                import traceback
                backup_conf["cloud_upload_status"] = 3
                backup_conf["cloud_name"] = cloud_name_cn
                # public.print_log("[backup_restore] cloud upload exception: timestamp={}, storage_type={}, error={}".format(timestamp, storage_type, str(e)))
                public.print_log(traceback.format_exc())
                self.print_log(
                    public.lang("Error occurred while uploading to {}: {}").format(cloud_name_cn, str(e)),
                    "backup"
                )

        self.save_backup_conf(timestamp, backup_conf)

    def get_backup_details(self, timestamp):
        history_info_file = self.history_info_path + '/' + str(timestamp) + '_backup.info'
        if not os.path.exists(history_info_file):
            get_info = self.get_backup_file_msg(timestamp)
            if not get_info:
                return public.fail_v2(public.lang("Backup info not found"))

        backup_info = json.loads(public.ReadFile(history_info_file))
        result = self.process_detail(backup_info)
        return public.success_v2(result)

    def get_backup_log(self, timestamp):
        backup_log_file = self.base_path + '/backup.log'
        history_log_file = self.history_log_path + '/' + str(timestamp) + '_backup.log'
        if os.path.exists(self.backup_pl_file):
            backup_timestamp = int(public.ReadFile(self.backup_pl_file))
            if int(backup_timestamp) == int(timestamp):
                return public.ReadFile(backup_log_file)
        if os.path.exists(history_log_file):
            return public.ReadFile(history_log_file)
        else:
            return None

    # todo 弃用
    def get_backup_progress(self, get=None):
        """
        获取备份进度信息
        @param get: object 包含请求参数
        @return: dict 备份进度信息
        """
        # 设置相关文件路径
        backup_pl_file = self.base_path + '/backup.pl'
        backup_log_file = self.base_path + '/backup.log'
        backup_success_file = self.base_path + '/success.pl'

        # 创建处理已完成备份的函数，减少代码重复
        def create_completed_result(backup_timestamp):
            if not backup_timestamp:
                return public.ReturnMsg(False, public.lang("Backup completed but unable to retrieve timestamp"))

            if not os.path.exists(self.bakcup_task_json):
                return public.ReturnMsg(False, public.lang("Backup configuration file does not exist"))

            backup_configs = json.loads(public.ReadFile(self.bakcup_task_json))
            success_data = next(
                (item for item in backup_configs if str(item.get('timestamp')) == str(backup_timestamp)), {}
            )
            return {
                "task_type": "backup",
                "task_status": 2,
                "backup_data": None,
                "backup_name": None,
                "data_backup_status": 2,
                "progress": 100,
                "msg": None,
                'exec_log': public.ReadFile(backup_log_file) if os.path.exists(backup_log_file) else "",
                'timestamp': backup_timestamp,
                'backup_file_info': success_data,
                'err_info': []
            }

        def create_initial_result(backup_timestamp=None):
            backup_log_data = public.ReadFile(backup_log_file) if os.path.exists(backup_log_file) else ""
            return self.build_initial_task_progress("backup", backup_timestamp, backup_log_data)

        # 检查备份是否已完成
        if os.path.exists(backup_success_file):
            success_time = int(os.path.getctime(backup_success_file))
            local_time = int(time.time())
            # 如果success文件创建时间在10秒内，说明备份刚刚完成
            if success_time + 10 > local_time:
                try:
                    backup_timestamp = public.ReadFile(backup_success_file).strip()
                    return public.ReturnMsg(True, create_completed_result(backup_timestamp))
                except Exception as e:
                    public.ExecShell("rm -f {}".format(backup_success_file))
                    return public.ReturnMsg(False,
                                            public.lang("Error retrieving backup completion information: {}").format(
                                                str(e)))
            else:
                # 超过10秒，删除success文件
                public.ExecShell("rm -f {}".format(backup_success_file))

        # 检查是否有备份进程运行
        try:
            # 检查备份进程锁文件
            if os.path.exists(backup_pl_file):
                timestamp = public.ReadFile(backup_pl_file).strip()
                if not timestamp:
                    return public.ReturnMsg(True, create_initial_result())
            else:
                init_state = self.get_initial_task_state("backup")
                if init_state:
                    return public.ReturnMsg(True, create_initial_result(init_state.get("timestamp")))

                # 等待2秒，可能是备份刚刚完成
                time.sleep(2)
                if os.path.exists(backup_success_file):
                    success_time = int(os.path.getctime(backup_success_file))
                    local_time = int(time.time())
                    if success_time + 10 > local_time:
                        backup_timestamp = public.ReadFile(backup_success_file).strip()
                        return public.ReturnMsg(True, create_completed_result(backup_timestamp))

                # 再次检查是否有备份进程
                if os.path.exists(backup_pl_file):
                    timestamp = public.ReadFile(backup_pl_file).strip()
                    if not timestamp:
                        return public.ReturnMsg(True, create_initial_result())
                else:
                    return public.ReturnMsg(False, public.lang(
                        "No ongoing backup tasks found. Please check the backup list to see if the backup is completed"))

            # 读取备份配置文件
            backup_json_path = f"{self.base_path}/{timestamp}_backup/backup.json"
            count = 0
            while 1:
                if count >= 3:
                    return public.ReturnMsg(True, create_initial_result(timestamp))
                count += 1
                if not os.path.exists(backup_json_path):
                    time.sleep(1)
                else:
                    break

            conf_data = json.loads(public.ReadFile(backup_json_path))
        except Exception as e:
            return public.ReturnMsg(False,
                                    public.lang("Error retrieving backup progress information: {}").format(str(e)))

        # 读取备份日志
        backup_log_data = public.ReadFile(backup_log_file) if os.path.exists(backup_log_file) else ""

        # 定义备份类型及其处理逻辑
        backup_types = [
            {
                'type': 'site',
                'data_key': 'site',
                'display_name': 'site',
                'progress': 30
            },
            {
                'type': 'database',
                'data_key': 'database',
                'display_name': 'database',
                'progress': 60
            },
            {
                'type': 'ftp',
                'data_key': 'ftp',
                'display_name': 'ftp',
                'progress': 70
            },
            {
                'type': 'terminal',
                'data_key': 'terminal',
                'display_name': 'terminal',
                'progress': 75
            },
            {
                'type': 'firewall',
                'data_key': 'firewall',
                'display_name': 'firewall',
                'progress': 90
            }
        ]

        # 检查各类型备份进度
        for backup_type in backup_types:
            items = conf_data.get("data_list", {}).get(backup_type['data_key'], [])
            for item in items:
                try:
                    if item.get("status") == 2:
                        continue

                    return public.ReturnMsg(True, {
                        "task_type": "backup",
                        "task_status": 1,
                        "data_type": backup_type['type'],
                        "name": item.get("name", f"unknow {backup_type['display_name']}"),
                        "data_backup_status": item.get("status", 0),
                        "progress": backup_type['progress'],
                        "msg": item.get("msg"),
                        'exec_log': backup_log_data,
                        'timestamp': timestamp
                    })
                except:
                    return public.ReturnMsg(True, {
                        "task_type": "backup",
                        "task_status": 1,
                        "data_type": public.lang("Server Configuration"),
                        "name": public.lang("Server Configuration"),
                        "data_backup_status": 1,
                        "progress": 80,
                        "msg": public.lang("Backing up server configuration"),
                        'exec_log': backup_log_data,
                        'timestamp': timestamp
                    })

        # 检查数据打包进度
        try:
            backup_status = conf_data.get('backup_status')
            if backup_status == 1:
                return public.ReturnMsg(True, {
                    "task_type": "backup",
                    "task_status": 1,
                    "data_type": "tar",
                    "name": public.lang("Data Packaging"),
                    "data_backup_status": 1,
                    "progress": 90,
                    'exec_log': backup_log_data,
                    'timestamp': timestamp
                })
        except Exception:
            # 可能没有backup_status字段，继续处理
            pass

        # 如果没有发现进行中的任务，但有备份进程
        if timestamp:
            return {
                "backup_data": "unknown",
                "backup_name": "unknow",
                "data_backup_status": 1,
                "progress": 10,
                'backup_msg': public.lang("Preparing backup data"),
                'backup_log': backup_log_data,
                'timestamp': timestamp
            }
        return public.ReturnMsg(False, public.lang(
            "No ongoing backup tasks found. Please check the backup list to see if the backup is completed"))


if __name__ == '__main__':
    # 获取命令行参数
    if len(sys.argv) < 3:
        print("Usage: btpython backup_manager.py <method> <timestamp>")
        sys.exit(1)
    method_name = sys.argv[1]  # 方法名
    timestamp = sys.argv[2]  # IP地址
    backup_manager = BackupManager()  # 实例化对象
    if hasattr(backup_manager, method_name):  # 检查方法是否存在
        method = getattr(backup_manager, method_name)  # 获取方法
        method(timestamp)  # 调用方法
    else:
        print(f"Error: Method '{method_name}' does not exist")
