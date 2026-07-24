# coding: utf-8
# -------------------------------------------------------------------
# aaPanel full backup cron adapter
# -------------------------------------------------------------------
# 全量备份 计划任务
import datetime
import json
import os
import shutil
import sys
import time
import traceback

PANEL_PATH = "/www/server/panel"
if os.path.exists(PANEL_PATH):
    os.chdir(PANEL_PATH)
if PANEL_PATH not in sys.path:
    sys.path.insert(0, PANEL_PATH)
if PANEL_PATH + "/class" not in sys.path:
    sys.path.insert(0, PANEL_PATH + "/class")
if PANEL_PATH + "/class_v2" not in sys.path:
    sys.path.insert(0, PANEL_PATH + "/class_v2")

import public
from mod.project.backup_restore.backup_manager import BackupManager


class CronFullBackup:
    base_path = "/www/backup/backup_restore"
    task_json = "/www/backup/backup_restore/backup_task.json"
    backup_pl_file = "/www/backup/backup_restore/backup.pl"

    def __init__(self, cron_echo):
        self.cron_echo = str(cron_echo).strip()
        self.cron_info = {}
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)

    @staticmethod
    def _to_int(value, default=0):
        try:
            return int(value)
        except:
            return default

    @staticmethod
    def _format_time(timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, msg):
        msg = "[full_backup] {}".format(msg)
        log_msg = time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg
        print(log_msg)
        # try:
        #     public.print_log(log_msg)
        # except:
        #     pass
        try:
            public.writeFile(os.path.join(self.base_path, "cron_full_backup.log"), log_msg + "\n", "a+")
        except:
            pass

    def _load_cron_info(self):
        self._log("Loading crontab task by echo: {}".format(self.cron_echo))
        if not self.cron_echo:
            return False
        cron_info = public.M("crontab").where("echo=?", (self.cron_echo,)).field(
            "id,name,echo,save,backupTo,save_local,notice,notice_channel,sType"
        ).find()
        if not cron_info or isinstance(cron_info, str):
            self._log("Full backup cron task not found: {}".format(self.cron_echo))
            return False
        if cron_info.get("sType") != "full_backup":
            self._log("Cron task is not a full_backup task: {}".format(self.cron_echo))
            return False
        self.cron_info = cron_info
        self._log(
            "Loaded task: id={id}, name={name}, backupTo={backupTo}, save={save}, "
            "save_local={save_local}, notice={notice}, notice_channel={notice_channel}".format(**cron_info)
        )
        return True

    def _read_task_list(self):
        if not os.path.exists(self.task_json):
            return []
        body = public.ReadFile(self.task_json)
        if not body:
            return []
        try:
            data = json.loads(body)
            return data if isinstance(data, list) else []
        except:
            return []

    def _write_task_list(self, data):
        self._log("Writing backup_task.json, total records: {}".format(len(data)))
        public.WriteFile(self.task_json, json.dumps(data))

    def _storage_type(self):
        backup_to = str(self.cron_info.get("backupTo") or "localhost")
        if backup_to in ("", "off", "localhost", "local"):
            return "local"
        return backup_to

    def _save_count(self):
        save = self._to_int(self.cron_info.get("save"), 3)
        return save if save > 0 else 3

    def _save_local(self):
        return self._to_int(self.cron_info.get("save_local"), 0)

    def _create_backup_conf(self, timestamp):
        now = int(time.time())
        storage_type = self._storage_type()
        backup_conf = {
            "backup_name": self.cron_info.get("name") or "Full Backup",
            "timestamp": int(timestamp),
            "create_time": self._format_time(now),
            "backup_time": self._format_time(timestamp),
            "storage_type": storage_type,
            "auto_exit": 0,
            "backup_status": 1,
            "restore_status": 0,
            "backup_path": os.path.join(self.base_path, "{}_backup".format(timestamp)),
            "backup_file": "",
            "backup_file_sha256": "",
            "backup_file_size": "",
            "backup_count": {
                "success": None,
                "failed": None,
            },
            "total_time": None,
            "done_time": None,
            "source": "crontab",
            "cron_id": self._to_int(self.cron_info.get("id")),
            "cron_echo": self.cron_echo,
            "save": self._save_count(),
            "save_local": self._save_local(),
            "backup_mode": "full_backup",
        }
        task_list = [
            item for item in self._read_task_list()
            if str(item.get("timestamp")) != str(timestamp)
        ]
        task_list.append(backup_conf)
        self._write_task_list(task_list)
        self._log(
            "Created backup config: timestamp={}, storage_type={}, save={}, save_local={}, backup_path={}".format(
                timestamp, storage_type, backup_conf["save"], backup_conf["save_local"], backup_conf["backup_path"]
            )
        )

    def _update_backup_conf(self, timestamp, data):
        task_list = self._read_task_list()
        for item in task_list:
            if str(item.get("timestamp")) == str(timestamp):
                item.update(data)
                break
        self._write_task_list(task_list)

    def _mark_failed(self, timestamp, message):
        self._log("Mark backup failed: timestamp={}, message={}".format(timestamp, message))
        now = int(time.time())
        self._update_backup_conf(timestamp, {
            "backup_status": 3,
            "error_msg": message,
            "done_time": self._format_time(now),
            "total_time": None,
        })

    def _safe_remove(self, path):
        if not path:
            return
        base = os.path.abspath(self.base_path)
        target = os.path.abspath(path)
        if target != base and not target.startswith(base + os.sep):
            self._log("Skip removing unsafe path: {}".format(path))
            return
        if not os.path.exists(target):
            return
        if os.path.isdir(target):
            self._log("Remove local directory: {}".format(target))
            shutil.rmtree(target, ignore_errors=True)
        else:
            try:
                self._log("Remove local file: {}".format(target))
                os.remove(target)
            except:
                pass

    def _delete_history(self, timestamp):
        for folder, suffix in (("log", "_backup.log"), ("info", "_backup.info")):
            target = os.path.join(self.base_path, "history", folder, "{}{}".format(timestamp, suffix))
            self._safe_remove(target)

    def _delete_backup_files(self, backup_conf):
        self._safe_remove(backup_conf.get("backup_file", ""))
        self._safe_remove(backup_conf.get("backup_path", ""))
        timestamp = backup_conf.get("timestamp")
        if timestamp:
            self._delete_history(timestamp)

    def _delete_cloud_file(self, backup_conf):
        cloud_path = backup_conf.get("cloud_upload_path")
        storage_type = backup_conf.get("cloud_storage") or backup_conf.get("storage_type")
        if not cloud_path or storage_type in ("", "off", "localhost", "local"):
            return True
        if self._to_int(backup_conf.get("cloud_upload_status"), 0) != 2:
            return True
        try:
            from cloud_stora_upload_v2 import CloudStoraUpload
            _cloud = CloudStoraUpload()
            if not _cloud.run(storage_type):
                self._log("Failed to connect cloud storage when deleting history: {}".format(storage_type))
                return False
            self._log("Deleting cloud history file: storage_type={}, path={}".format(storage_type, cloud_path))
            result = _cloud.cloud_delete_file(cloud_path)
            if result is None:
                return True
            if isinstance(result, dict):
                return bool(result.get("status"))
            return bool(result)
        except:
            self._log(traceback.format_exc())
            return False

    def _cleanup_history(self):
        cron_id = str(self.cron_info.get("id"))
        save = self._save_count()
        task_list = self._read_task_list()
        candidates = [
            item for item in task_list
            if item.get("source") == "crontab"
            and str(item.get("cron_id")) == cron_id
            and self._to_int(item.get("backup_status"), 0) != 1
        ]
        candidates.sort(key=lambda x: self._to_int(x.get("timestamp"), 0), reverse=True)
        remove_timestamps = set(str(item.get("timestamp")) for item in candidates[save:])
        if not remove_timestamps:
            self._log("No history records need cleanup. keep_latest={}".format(save))
            return
        self._log("Cleanup history records: keep_latest={}, remove_timestamps={}".format(save, ",".join(remove_timestamps)))
        new_task_list = []
        for item in task_list:
            if str(item.get("timestamp")) in remove_timestamps:
                if not self._delete_cloud_file(item):
                    new_task_list.append(item)
                    continue
                self._delete_backup_files(item)
                continue
            new_task_list.append(item)
        self._write_task_list(new_task_list)

    def _drop_local_file_after_cloud_upload(self, timestamp):
        if self._storage_type() == "local" or self._save_local():
            self._log("Keep local backup file: storage_type={}, save_local={}".format(self._storage_type(), self._save_local()))
            return
        manager = BackupManager()
        backup_conf = manager.get_backup_conf(str(timestamp))
        if not backup_conf:
            self._log("Backup config not found when checking local file cleanup: {}".format(timestamp))
            return
        if self._to_int(backup_conf.get("cloud_upload_status"), 0) != 2:
            self._log("Cloud upload is not confirmed; local backup is kept.")
            return
        self._delete_backup_files(backup_conf)
        backup_conf["local_file_kept"] = 0
        backup_conf["backup_file_local_removed"] = 1
        backup_conf["backup_file"] = ""
        backup_conf["backup_path"] = ""
        manager.save_backup_conf(str(timestamp), backup_conf)

    def _send_failure_notice(self, message):
        notice = self._to_int(self.cron_info.get("notice"), 0)
        notice_channel = str(self.cron_info.get("notice_channel") or "")
        if notice == 0 or not notice_channel:
            self._log("Failure notice skipped: notice={}, notice_channel={}".format(notice, notice_channel))
            return
        try:
            from script.notify_cli import send_notify
            channels = [i.strip() for i in notice_channel.split(",") if i.strip()] or None
            title = "aaPanel full backup task failed reminder"
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            body = (
                "*aaPanel reminds you that the cron failed to execute*\n"
                "* Time*: {now}\n"
                "* Task name*: {name}\n"
                "* error message*:\n{message}\n"
                "--Notification by aaPanel"
            ).format(now=now, name=self.cron_info.get("name", "Full Backup"), message=message)
            send_notify(title, body, channels)
            self._log("Failure notice sent: channels={}".format(channels))
        except:
            self._log(traceback.format_exc())

    def _short_text(self, value, max_len=500):
        value = str(value or "")
        if len(value) > max_len:
            return value[:max_len] + "..."
        return value

    def _failed_item_name(self, item):
        for key in ("name", "site_name", "database_name", "db_name", "title", "path", "filename", "project_name", "plugin_name", "type"):
            value = item.get(key)
            if value not in (None, ""):
                return self._short_text(value, 200)
        return "unknown"

    def _failed_item_msg(self, item):
        for key in ("msg", "error_msg", "err_msg", "error", "backup_msg"):
            value = item.get(key)
            if value not in (None, ""):
                return self._short_text(value)
        return ""

    def _collect_failed_items(self, value, category=""):
        failed_items = []
        if isinstance(value, dict):
            status = self._to_int(value.get("status"), 0)
            if status == 3:
                failed_items.append((category or "unknown", self._failed_item_name(value), self._failed_item_msg(value)))
            for key, sub_value in value.items():
                if isinstance(sub_value, (dict, list)):
                    sub_category = "{}.{}".format(category, key) if category else str(key)
                    failed_items.extend(self._collect_failed_items(sub_value, sub_category))
        elif isinstance(value, list):
            for sub_value in value:
                failed_items.extend(self._collect_failed_items(sub_value, category))
        return failed_items

    def _log_failed_item_details(self, timestamp):
        try:
            backup_data = BackupManager().get_backup_data_list(str(timestamp))
        except:
            backup_json = os.path.join(self.base_path, "{}_backup".format(timestamp), "backup.json")
            backup_data = {}
            try:
                if os.path.exists(backup_json):
                    backup_data = json.loads(public.ReadFile(backup_json))
            except:
                backup_data = {}

        data_list = backup_data.get("data_list", {}) if isinstance(backup_data, dict) else {}
        failed_items = self._collect_failed_items(data_list)
        if not failed_items:
            self._log("Failed item details not found in backup.json: timestamp={}".format(timestamp))
            return

        for category, name, msg in failed_items[:20]:
            self._log("Failed item detail: category={}, name={}, msg={}".format(category, name, msg))
        if len(failed_items) > 20:
            self._log("Failed item detail truncated: total={}, logged=20".format(len(failed_items)))

    def _check_backup_result(self, timestamp):
        manager = BackupManager()
        backup_conf = manager.get_backup_conf(str(timestamp))
        if not backup_conf:
            self._log("Check result failed: backup config lost, timestamp={}".format(timestamp))
            return "Backup configuration was lost."
        if self._to_int(backup_conf.get("backup_status"), 0) != 2:
            self._log("Check result failed: backup_status={}".format(backup_conf.get("backup_status")))
            return "Full backup did not complete."
        failed = self._to_int((backup_conf.get("backup_count") or {}).get("failed"), 0)
        if failed > 0:
            self._log("Check result failed: failed items={}".format(failed))
            self._log_failed_item_details(timestamp)
            return "{} backup item(s) failed.".format(failed)
        if self._storage_type() != "local" and self._to_int(backup_conf.get("cloud_upload_status"), 0) != 2:
            self._log("Check result failed: cloud_upload_status={}".format(backup_conf.get("cloud_upload_status")))
            return "Cloud upload failed or was not confirmed."
        self._log(
            "Check result success: timestamp={}, backup_file={}, size={}, cloud_status={}".format(
                timestamp,
                backup_conf.get("backup_file", ""),
                backup_conf.get("backup_file_size", ""),
                backup_conf.get("cloud_upload_status", "")
            )
        )
        return ""

    def run(self):
        self._log("Run start.")
        if not self._load_cron_info():
            return 1
        if os.path.exists(self.backup_pl_file):
            self._log("A backup process is already running; full_backup cron skipped.")
            return 0

        timestamp = int(time.time())
        self._create_backup_conf(timestamp)
        try:
            self._log("Calling BackupManager.backup_data: timestamp={}".format(timestamp))
            result = BackupManager().backup_data(str(timestamp))
            self._log("BackupManager.backup_data returned: {}".format(result))
            if isinstance(result, dict) and result.get("status") is False:
                message = result.get("msg") or "Full backup failed."
                self._mark_failed(timestamp, message)
                self._send_failure_notice(message)
                return 1

            error = self._check_backup_result(timestamp)
            if error:
                self._send_failure_notice(error)

            self._drop_local_file_after_cloud_upload(timestamp)
            self._cleanup_history()
            self._log("Run finished: timestamp={}, status={}".format(timestamp, "success" if not error else "failed"))
            return 0 if not error else 1
        except Exception as e:
            message = "{}\n{}".format(str(e), traceback.format_exc())
            self._mark_failed(timestamp, message)
            self._send_failure_notice(message)
            return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: btpython cron_full_backup.py <cron_echo>")
        return 1
    return CronFullBackup(sys.argv[1]).run()


if __name__ == "__main__":
    sys.exit(main())
