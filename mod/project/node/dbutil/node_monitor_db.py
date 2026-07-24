# coding: utf-8
import json
import os
import re
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")

import public


DEFAULT_SNAPSHOT_RETENTION_DAYS = 7
MIN_SNAPSHOT_RETENTION_DAYS = 1
MAX_SNAPSHOT_RETENTION_DAYS = 3650


def _json_dumps(data: Any) -> str:
    try:
        return json.dumps(data)
    except Exception:
        return "{}"


def _json_loads(data: Any, default: Any) -> Any:
    if isinstance(data, (dict, list)):
        return data
    if not isinstance(data, str) or not data:
        return default
    try:
        return json.loads(data)
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.strip().replace("%", "")
        return float(value)
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _to_bytes(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return 0
    value = value.strip().replace(",", "")
    if not value:
        return 0
    match = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([KMGTPE]?)(?:I?B)?$", value, re.I)
    if not match:
        return _to_int(value)
    number = _to_float(match.group(1))
    unit = match.group(2).upper()
    units = {
        "": 1,
        "K": 1024,
        "M": 1024 ** 2,
        "G": 1024 ** 3,
        "T": 1024 ** 4,
        "P": 1024 ** 5,
        "E": 1024 ** 6,
    }
    return int(number * units.get(unit, 1))


def _to_bytes_from_panel_mem(value: Any) -> int:
    """面板获取网络内存数值单位通常为 MB,Shell 探针返回单位可能为字节,统一单位"""
    number = _to_float(value)
    if number <= 0:
        return 0
    if number < 1024 * 1024:
        return int(number * 1024 * 1024)
    return int(number)


def _percent(value: Any) -> float:
    return round(_to_float(value), 2)


def _normalize_retention_days(value: Any) -> int:
    days = _to_int(value, DEFAULT_SNAPSHOT_RETENTION_DAYS)
    if days < MIN_SNAPSHOT_RETENTION_DAYS:
        return MIN_SNAPSHOT_RETENTION_DAYS
    if days > MAX_SNAPSHOT_RETENTION_DAYS:
        return MAX_SNAPSHOT_RETENTION_DAYS
    return days


TABLE_SCHEMAS = {
    # 保存每个节点的监控总开关、采集周期(默认采集,在线状态检测,详细指标采集 间隔)、费用(金额,币种代码/符号,费用周期)、到期时间
    "node_monitor_setting": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL"),
            ("enabled", "INTEGER NOT NULL DEFAULT 1"),
            ("collect_interval", "INTEGER NOT NULL DEFAULT 60"),
            ("status_interval", "INTEGER NOT NULL DEFAULT 60"),
            ("detail_interval", "INTEGER NOT NULL DEFAULT 60"),
            ("snapshot_retention_days", "INTEGER NOT NULL DEFAULT 7"),
            ("cost_amount", "REAL NOT NULL DEFAULT 0"),
            ("cost_currency", "TEXT NOT NULL DEFAULT 'CNY'"),
            ("cost_symbol", "TEXT NOT NULL DEFAULT ''"),
            ("cost_period", "TEXT NOT NULL DEFAULT 'month'"),
            ("expire_at", "INTEGER NOT NULL DEFAULT 0"),
            ("remark", "TEXT NOT NULL DEFAULT ''"),
            ("created_at", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_monitor_setting_node", True, ("node_id",)),
        ],
    },
    # 保存节点选择监控哪个磁盘、哪个网卡、哪些服务  target_type:disk,nic,service  target_key:对象唯一标识  extra:JSON 扩展字段  is_primary:标记展示的磁盘网卡
    "node_monitor_target": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL"),
            ("target_type", "TEXT NOT NULL"),
            ("target_key", "TEXT NOT NULL"),
            ("target_name", "TEXT NOT NULL DEFAULT ''"),
            ("enabled", "INTEGER NOT NULL DEFAULT 1"),
            ("is_primary", "INTEGER NOT NULL DEFAULT 0"),
            ("sort", "INTEGER NOT NULL DEFAULT 0"),
            ("extra", "TEXT NOT NULL DEFAULT '{}'"),
            ("discovered_at", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_monitor_target_unique", True, ("node_id", "target_type", "target_key")),
            ("idx_node_monitor_target_node_type", False, ("node_id", "target_type")),
        ],
    },
    # 保存每个节点最新监控快照 每分钟覆盖写 status:-1在线 -0离线 -2采集失败但未判定离线 -4重启等待中 {}_json:当前节点全部磁盘网卡服务数据
    "node_monitor_latest": {
        "columns": [
            ("node_id", "INTEGER PRIMARY KEY"),
            ("ts", "INTEGER NOT NULL DEFAULT 0"),
            ("status", "INTEGER NOT NULL DEFAULT 0"),
            ("error_msg", "TEXT NOT NULL DEFAULT ''"),
            ("cpu_usage", "REAL NOT NULL DEFAULT 0"),
            ("mem_usage", "REAL NOT NULL DEFAULT 0"),
            ("mem_used", "INTEGER NOT NULL DEFAULT 0"),
            ("mem_total", "INTEGER NOT NULL DEFAULT 0"),
            ("load1", "REAL NOT NULL DEFAULT 0"),
            ("load5", "REAL NOT NULL DEFAULT 0"),
            ("load15", "REAL NOT NULL DEFAULT 0"),
            ("disk_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("nic_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("service_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("raw_json", "TEXT NOT NULL DEFAULT '{}'"),
        ],
        "indexes": [
            ("idx_node_monitor_latest_ts", False, ("ts",)),
        ],
    },
    # 保存历史监控数据，用于趋势图、平均值告警、持续时间判断
    # 每分钟一条，一台节点一天 1440 条，100 台节点一天 14.4 万条。
    # 保留策略：
    # 分钟级数据保留 7 天
    # 5 分钟聚合数据保留 30 天
    # 超期数据定时清理

    "node_monitor_snapshot": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL"),
            ("ts", "INTEGER NOT NULL"),
            ("status", "INTEGER NOT NULL DEFAULT 0"),
            ("error_msg", "TEXT NOT NULL DEFAULT ''"),
            ("cpu_usage", "REAL NOT NULL DEFAULT 0"),
            ("mem_usage", "REAL NOT NULL DEFAULT 0"),
            ("mem_used", "INTEGER NOT NULL DEFAULT 0"),
            ("mem_total", "INTEGER NOT NULL DEFAULT 0"),
            ("load1", "REAL NOT NULL DEFAULT 0"),
            ("load5", "REAL NOT NULL DEFAULT 0"),
            ("load15", "REAL NOT NULL DEFAULT 0"),
            ("disk_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("nic_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("service_json", "TEXT NOT NULL DEFAULT '[]'"),
            ("raw_json", "TEXT NOT NULL DEFAULT '{}'"),
        ],
        "indexes": [
            ("idx_node_monitor_snapshot_node_ts", False, ("node_id", "ts")),
            ("idx_node_monitor_snapshot_ts", False, ("ts",)),
        ],
    },
    # 节点告警设置 通用设置 告警通道 告警最小间隔 允许告警时间范围
    "node_alert_setting": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL DEFAULT 0"),
            ("sender_ids", "TEXT NOT NULL DEFAULT '[]'"),
            ("send_interval_enabled", "INTEGER NOT NULL DEFAULT 1"),
            ("send_interval", "INTEGER NOT NULL DEFAULT 1800"),
            ("time_range_enabled", "INTEGER NOT NULL DEFAULT 0"),
            ("time_range_start", "INTEGER NOT NULL DEFAULT 0"),
            ("time_range_end", "INTEGER NOT NULL DEFAULT 86400"),
            ("created_at", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_alert_setting_node", True, ("node_id",)),
        ],
    },

    # 固定监控项配置 每个节点或全局(node_id=0) 每个metric监控指标 一条
    # target_key：磁盘路径或网卡名. CPU/内存/离线/到期为空
    # duration_minutes：持续多少分钟触发
    # threshold 阈值 xx   超过xx%  xxMB/s   xxGB xxMB
    # threshold_unit  %  MB/s  GB

    "node_alert_item": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL DEFAULT 0"),
            ("metric", "TEXT NOT NULL"),
            ("enabled", "INTEGER NOT NULL DEFAULT 0"),
            ("operator", "TEXT NOT NULL DEFAULT '>='"),
            ("threshold", "REAL NOT NULL DEFAULT 0"),
            ("threshold_unit", "TEXT NOT NULL DEFAULT ''"),
            ("duration_minutes", "INTEGER NOT NULL DEFAULT 1"),
            ("target_key", "TEXT NOT NULL DEFAULT ''"),
            ("target_name", "TEXT NOT NULL DEFAULT ''"),
            ("created_at", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_alert_item_unique", True, ("node_id", "metric", "target_key")),
            ("idx_node_alert_item_node", False, ("node_id",)),
            ("idx_node_alert_item_enabled", False, ("enabled",)),
        ],
    },

    # 保存当前告警状态 避免重复发送
    # status：normal / alert。
    # first_trigger_at：用于持续时间判断
    # last_sent_at：用于最小发送间隔
    # send_count：告警次数  后续可做次数限制
    "node_alert_state": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL"),
            ("item_id", "INTEGER NOT NULL DEFAULT 0"),
            ("metric", "TEXT NOT NULL DEFAULT ''"),
            ("target_key", "TEXT NOT NULL DEFAULT ''"),
            ("status", "TEXT NOT NULL DEFAULT 'normal'"),
            ("last_value", "REAL NOT NULL DEFAULT 0"),
            ("last_message", "TEXT NOT NULL DEFAULT ''"),
            ("first_trigger_at", "INTEGER NOT NULL DEFAULT 0"),
            ("last_checked_at", "INTEGER NOT NULL DEFAULT 0"),
            ("last_sent_at", "INTEGER NOT NULL DEFAULT 0"),
            ("send_count", "INTEGER NOT NULL DEFAULT 0"),
            ("updated_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_alert_state_node_metric_target", True, ("node_id", "metric", "target_key")),
            ("idx_node_alert_state_v2_node", False, ("node_id",)),
            ("idx_node_alert_state_v2_status", False, ("status",)),
        ],
    },
    # 告警历史
    "node_alert_history": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("node_id", "INTEGER NOT NULL"),
            ("item_id", "INTEGER NOT NULL DEFAULT 0"),
            ("metric", "TEXT NOT NULL DEFAULT ''"),
            ("target_key", "TEXT NOT NULL DEFAULT ''"),
            ("trigger_value", "REAL NOT NULL DEFAULT 0"),
            ("operator", "TEXT NOT NULL DEFAULT ''"),
            ("threshold", "REAL NOT NULL DEFAULT 0"),
            ("threshold_unit", "TEXT NOT NULL DEFAULT ''"),
            ("action", "TEXT NOT NULL DEFAULT ''"),
            ("message", "TEXT NOT NULL DEFAULT ''"),
            ("sender_ids", "TEXT NOT NULL DEFAULT '[]'"),
            ("send_result", "TEXT NOT NULL DEFAULT '{}'"),
            ("created_at", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "indexes": [
            ("idx_node_alert_history_v2_node_time", False, ("node_id", "created_at")),
            ("idx_node_alert_history_v2_metric_time", False, ("metric", "created_at")),
            ("idx_node_alert_history_v2_time", False, ("created_at",)),
        ],
    },
}


class NodeMonitorDB:
    _DB_FILE = public.get_panel_path() + "/data/db/node_monitor.db"

    def __init__(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def __del__(self):
        self.close()

    def table(self, table_name: str):
        return public.S(table_name, self._DB_FILE)

    @classmethod
    def _column_map(cls, table_name: str) -> Dict[str, str]:
        schema = TABLE_SCHEMAS[table_name]
        return {name: definition for name, definition in schema["columns"]}

    @staticmethod
    def _create_table_sql(table_name: str) -> str:
        columns = ["`{}` {}".format(name, definition) for name, definition in TABLE_SCHEMAS[table_name]["columns"]]
        return "CREATE TABLE IF NOT EXISTS `{}` (\n    {}\n);".format(table_name, ",\n    ".join(columns))

    @staticmethod
    def _create_index_sql(table_name: str, index_name: str, unique: bool, columns: Tuple[str, ...]) -> str:
        unique_sql = "UNIQUE " if unique else ""
        col_sql = ", ".join("`{}`".format(item) for item in columns)
        return "CREATE {}INDEX IF NOT EXISTS `{}` ON `{}` ({});".format(unique_sql, index_name, table_name, col_sql)

    @staticmethod
    def _sqlite_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        return bool(row)

    @staticmethod
    def _sqlite_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
        if not NodeMonitorDB._sqlite_table_exists(conn, table_name):
            return []
        return [row[1] for row in conn.execute("PRAGMA table_info(`{}`)".format(table_name)).fetchall()]

    @staticmethod
    def _archive_sqlite_table(conn: sqlite3.Connection, table_name: str, suffix: int) -> None:
        if not NodeMonitorDB._sqlite_table_exists(conn, table_name):
            return
        new_name = "{}_legacy_{}".format(table_name, suffix)
        while NodeMonitorDB._sqlite_table_exists(conn, new_name):
            suffix += 1
            new_name = "{}_legacy_{}".format(table_name, suffix)
        conn.execute("ALTER TABLE `{}` RENAME TO `{}`".format(table_name, new_name))

    @staticmethod
    def _archive_legacy_alert_tables(conn: sqlite3.Connection) -> None:
        suffix = int(time.time())
        if NodeMonitorDB._sqlite_table_exists(conn, "node_alert_rule"):
            NodeMonitorDB._archive_sqlite_table(conn, "node_alert_rule", suffix)
        state_columns = NodeMonitorDB._sqlite_columns(conn, "node_alert_state")
        if "rule_id" in state_columns:
            NodeMonitorDB._archive_sqlite_table(conn, "node_alert_state", suffix)
        history_columns = NodeMonitorDB._sqlite_columns(conn, "node_alert_history")
        if "rule_id" in history_columns or "value" in history_columns:
            NodeMonitorDB._archive_sqlite_table(conn, "node_alert_history", suffix)

    # 初始化数据库 支持新增字段(在表定义中添加
    def init_db(self):
        db_dir = os.path.dirname(self._DB_FILE)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        if not os.path.exists(self._DB_FILE):
            public.writeFile(self._DB_FILE, "")

        conn = sqlite3.connect(self._DB_FILE)
        try:
            conn.execute("PRAGMA busy_timeout=5000;")
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
            except Exception:
                pass
            # 不用兼容旧数据
            # self._archive_legacy_alert_tables(conn)
            cur = conn.cursor()
            for table_name in TABLE_SCHEMAS:
                cur.execute(self._create_table_sql(table_name))
                cur.execute("PRAGMA table_info(`{}`)".format(table_name))
                existing_cols = {row[1] for row in cur.fetchall()}
                for col_name, col_def in TABLE_SCHEMAS[table_name]["columns"]:
                    if col_name in existing_cols:
                        continue
                    if "PRIMARY KEY" in col_def.upper():
                        continue
                    cur.execute("ALTER TABLE `{}` ADD COLUMN `{}` {}".format(table_name, col_name, col_def))

                for index_name, unique, columns in TABLE_SCHEMAS[table_name].get("indexes", []):
                    cur.execute(self._create_index_sql(table_name, index_name, unique, columns))
            conn.commit()
        finally:
            conn.close()

    def get_setting(self, node_id: int, create: bool = True) -> Dict[str, Any]:
        node_id = int(node_id)
        data = self.table("node_monitor_setting").where("node_id=?", (node_id,)).find()
        if isinstance(data, dict) and data:
            return data
        if not create:
            return {}
        now = int(time.time())
        row = {
            "node_id": node_id,
            "enabled": 1,
            "collect_interval": 60,
            "status_interval": 60,
            "detail_interval": 60,
            "snapshot_retention_days": DEFAULT_SNAPSHOT_RETENTION_DAYS,
            "cost_amount": 0,
            "cost_currency": "CNY",
            "cost_symbol": "",
            "cost_period": "month",
            "expire_at": 0,
            "remark": "",
            "created_at": now,
            "updated_at": now,
        }
        self.table("node_monitor_setting").insert(row)
        return self.table("node_monitor_setting").where("node_id=?", (node_id,)).find() or row

    def save_setting(self, node_id: int, data: Dict[str, Any]) -> str:
        node_id = int(node_id)
        allowed = {
            "enabled", "collect_interval", "status_interval", "detail_interval",
            "snapshot_retention_days",
            "cost_amount", "cost_currency", "cost_symbol", "cost_period",
            "expire_at", "remark",
        }
        row = {}
        for key, value in data.items():
            if key not in allowed:
                continue
            if key == "snapshot_retention_days":
                value = _normalize_retention_days(value)
            row[key] = value
        if not row:
            return ""
        row["updated_at"] = int(time.time())
        if not self.get_setting(node_id, create=False):
            self.get_setting(node_id, create=True)
        res = self.table("node_monitor_setting").where("node_id=?", (node_id,)).update(row)
        return res if isinstance(res, str) else ""

    def get_targets(self, node_id: int, target_type: str = "") -> List[Dict[str, Any]]:
        query = self.table("node_monitor_target")
        if target_type:
            data = query.where("node_id=? AND target_type=?", (int(node_id), target_type)).order("sort", "ASC").order("id", "ASC").select()
        else:
            data = query.where("node_id=?", (int(node_id),)).order("target_type", "ASC").order("sort", "ASC").order("id", "ASC").select()
        if isinstance(data, list):
            for item in data:
                item["extra"] = _json_loads(item.get("extra"), {})
            return data
        return []

    def get_enabled_service_targets(self, node_id: int) -> List[Dict[str, Any]]:
        return [item for item in self.get_targets(node_id, "service") if int(item.get("enabled", 0)) == 1]

    def upsert_target(self, node_id: int, target_type: str, target_key: str, data: Dict[str, Any]) -> str:
        node_id = int(node_id)
        target_type = str(target_type)
        target_key = str(target_key)
        now = int(time.time())
        row = {
            "target_name": data.get("target_name", ""),
            "enabled": int(data.get("enabled", 1)),
            "is_primary": int(data.get("is_primary", 0)),
            "sort": int(data.get("sort", 0)),
            "extra": _json_dumps(data.get("extra", {})),
            "updated_at": now,
        }
        old = self.table("node_monitor_target").where(
            "node_id=? AND target_type=? AND target_key=?", (node_id, target_type, target_key)
        ).find()
        try:
            if isinstance(old, dict) and old:
                self.table("node_monitor_target").where("id=?", (old["id"],)).update(row)
            else:
                row.update({
                    "node_id": node_id,
                    "target_type": target_type,
                    "target_key": target_key,
                    "discovered_at": now,
                })
                self.table("node_monitor_target").insert(row)
        except Exception as e:
            return str(e)
        return ""

    def set_primary_target(self, node_id: int, target_type: str, target_key: str) -> str:
        if target_type not in ("disk", "nic"):
            return "Only disk or nic can be set as the primary target"
        node_id = int(node_id)
        target_key = str(target_key)
        self.table("node_monitor_target").where(
            "node_id=? AND target_type=?", (node_id, target_type)
        ).update({"is_primary": 0, "updated_at": int(time.time())})
        old = self.table("node_monitor_target").where(
            "node_id=? AND target_type=? AND target_key=?", (node_id, target_type, target_key)
        ).find()
        if not isinstance(old, dict) or not old:
            err = self.upsert_target(node_id, target_type, target_key, {
                "target_name": target_key,
                "enabled": 1,
                "is_primary": 1,
            })
            return err
        res = self.table("node_monitor_target").where("id=?", (old["id"],)).update({
            "enabled": 1,
            "is_primary": 1,
            "updated_at": int(time.time()),
        })
        return res if isinstance(res, str) else ""

    def save_service_targets(self, node_id: int, services: List[Dict[str, Any]]) -> str:
        node_id = int(node_id)
        old = self.get_targets(node_id, "service")
        old_map = {item["target_key"]: item for item in old}
        seen = set()
        for idx, item in enumerate(services):
            key = str(item.get("target_key") or item.get("name") or "").strip()
            if not key:
                continue
            seen.add(key)
            err = self.upsert_target(node_id, "service", key, {
                "target_name": item.get("target_name", key),
                "enabled": int(item.get("enabled", 1)),
                "is_primary": 0,
                "sort": int(item.get("sort", idx)),
                "extra": item.get("extra", {}),
            })
            if err:
                return err
        now = int(time.time())
        for key, item in old_map.items():
            if key not in seen:
                self.table("node_monitor_target").where("id=?", (item["id"],)).update({
                    "enabled": 0,
                    "updated_at": now,
                })
        return ""

    def sync_discovered_targets(self, node_id: int, disks: List[Dict[str, Any]], nics: List[Dict[str, Any]]) -> None:
        self._sync_discovered_by_type(node_id, "disk", disks, "path")
        self._sync_discovered_by_type(node_id, "nic", nics, "name")

    def _sync_discovered_by_type(self, node_id: int, target_type: str, items: List[Dict[str, Any]], key_name: str) -> None:
        if not items:
            return
        current = self.get_targets(node_id, target_type)
        current_keys = {item["target_key"] for item in current}
        has_primary = any(int(item.get("is_primary", 0)) == 1 for item in current)
        for idx, item in enumerate(items):
            key = str(item.get(key_name, "")).strip()
            if not key:
                continue
            is_primary = 1 if (not has_primary and idx == 0) else 0
            has_primary = has_primary or bool(is_primary)
            if key in current_keys:
                old = next((row for row in current if row["target_key"] == key), None)
                if old:
                    self.table("node_monitor_target").where("id=?", (old["id"],)).update({
                        "target_name": item.get("name", key),
                        "extra": _json_dumps(item),
                        "updated_at": int(time.time()),
                    })
                continue
            self.upsert_target(node_id, target_type, key, {
                "target_name": item.get("name", key),
                "enabled": 1,
                "is_primary": is_primary,
                "sort": idx,
                "extra": item,
            })

    def normalize_monitor_data(self, raw_data: Dict[str, Any], status: int = 1, error_msg: str = "") -> Dict[str, Any]:
        now = int(time.time())
        cpu_usage = 0.0
        cpu_data = raw_data.get("cpu", [])
        if isinstance(cpu_data, (list, tuple)) and cpu_data:
            cpu_usage = _percent(cpu_data[0])
        elif isinstance(cpu_data, dict):
            cpu_usage = _percent(cpu_data.get("usage", cpu_data.get("used", 0)))

        mem = raw_data.get("mem", {}) if isinstance(raw_data.get("mem", {}), dict) else {}
        mem_used = _to_bytes_from_panel_mem(mem.get("memRealUsed", mem.get("used", 0)))
        mem_total = _to_bytes_from_panel_mem(mem.get("memTotal", mem.get("total", 0)))
        mem_usage = round(mem_used / mem_total * 100, 2) if mem_total else 0.0

        load = raw_data.get("load", {}) if isinstance(raw_data.get("load", {}), dict) else {}
        disks = self._normalize_disks(raw_data)
        nics = self._normalize_nics(raw_data)
        services = raw_data.get("services", [])
        if not isinstance(services, list):
            services = []
        else:
            services = self._normalize_services(services)

        normalized = {
            "ts": now,
            "status": int(status),
            "error_msg": str(error_msg or ""),
            "cpu_usage": cpu_usage,
            "mem_usage": mem_usage,
            "mem_used": mem_used,
            "mem_total": mem_total,
            "load1": _to_float(load.get("one", load.get("load1", 0))),
            "load5": _to_float(load.get("five", load.get("load5", 0))),
            "load15": _to_float(load.get("fifteen", load.get("load15", 0))),
            "disk_json": _json_dumps(disks),
            "nic_json": _json_dumps(nics),
            "service_json": _json_dumps(services),
            "raw_json": _json_dumps(raw_data),
        }
        return normalized

    @staticmethod
    def _normalize_disks(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        disk_data = raw_data.get("disk", raw_data.get("disks", []))
        if not isinstance(disk_data, list):
            return []
        result = []
        for item in disk_data:
            if not isinstance(item, dict):
                continue
            byte_size = item.get("byte_size", [])
            total = used = available = 0
            if isinstance(byte_size, (list, tuple)) and len(byte_size) >= 3:
                total, used, available = _to_int(byte_size[0]), _to_int(byte_size[1]), _to_int(byte_size[2])
            elif isinstance(item.get("size"), (list, tuple)) and len(item.get("size")) >= 3:
                size_data = item.get("size")
                total, used, available = _to_bytes(size_data[0]), _to_bytes(size_data[1]), _to_bytes(size_data[2])
            else:
                total = _to_int(item.get("total", item.get("size_total", 0)))
                used = _to_int(item.get("used", item.get("size_used", 0)))
                available = _to_int(item.get("available", item.get("free", 0)))
            usage = _percent(item.get("usage", item.get("d_size", 0)))
            if not usage and total:
                usage = round(used / total * 100, 2)
            inode_usage = 0.0
            inodes = item.get("inodes", [])
            if isinstance(inodes, (list, tuple)) and len(inodes) >= 4:
                inode_usage = _percent(inodes[3])
            else:
                inode_usage = _percent(item.get("inode_usage", 0))
            result.append({
                "path": item.get("path", item.get("mountpoint", "")),
                "filesystem": item.get("filesystem", item.get("device", "")),
                "type": item.get("type", item.get("types", "")),
                "total": total,
                "used": used,
                "available": available,
                "usage": usage,
                "inode_usage": inode_usage,
            })
        return [item for item in result if item["path"]]

    @staticmethod
    def _normalize_nics(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        network = raw_data.get("network", raw_data.get("nics", {}))
        result = []
        if isinstance(network, list):
            items = [(item.get("name", ""), item) for item in network if isinstance(item, dict)]
        elif isinstance(network, dict):
            items = [(name, data) for name, data in network.items() if isinstance(data, dict)]
        else:
            items = []
        for name, item in items:
            if not name or name == "lo":
                continue
            result.append({
                "name": name,
                "up_kbs": _to_float(item.get("up", item.get("up_kbs", 0))),
                "down_kbs": _to_float(item.get("down", item.get("down_kbs", 0))),
                "up_total": _to_int(item.get("upTotal", item.get("up_total", 0))),
                "down_total": _to_int(item.get("downTotal", item.get("down_total", 0))),
                "up_packets": _to_int(item.get("upPackets", item.get("up_packets", 0))),
                "down_packets": _to_int(item.get("downPackets", item.get("down_packets", 0))),
            })
        return result

    @staticmethod
    def _normalize_services(services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for item in services:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("target_key") or "").strip()
            if not name:
                continue
            status = _to_int(item.get("status", 1 if item.get("running") else 0))
            result.append({
                "name": name,
                "target_key": str(item.get("target_key") or name),
                "target_name": str(item.get("target_name") or item.get("name") or name),
                "status": status,
                "running": bool(item.get("running", status == 1)),
                "state": str(item.get("state") or ("active" if status == 1 else "inactive")),
                "error_msg": str(item.get("error_msg") or ""),
                "ts": _to_int(item.get("ts"), int(time.time())),
            })
        return result

    def save_node_snapshot(self, node_id: int, raw_data: Dict[str, Any], status: int = 1, error_msg: str = "") -> str:
        node_id = int(node_id)
        if not isinstance(raw_data, dict):
            raw_data = {}
        row = self.normalize_monitor_data(raw_data, status=status, error_msg=error_msg)
        latest_row = {"node_id": node_id}
        latest_row.update(row)
        snapshot_row = {"node_id": node_id}
        snapshot_row.update(row)
        try:
            exists = self.table("node_monitor_latest").where("node_id=?", (node_id,)).count() > 0
            if exists:
                data = latest_row.copy()
                data.pop("node_id", None)
                self.table("node_monitor_latest").where("node_id=?", (node_id,)).update(data)
            else:
                self.table("node_monitor_latest").insert(latest_row)
            self.table("node_monitor_snapshot").insert(snapshot_row)
            self.sync_discovered_targets(
                node_id,
                _json_loads(row["disk_json"], []),
                _json_loads(row["nic_json"], []),
            )
        except Exception as e:
            return str(e)
        return ""

    def save_latest_status(self, node_id: int, status: int, error_msg: str = "") -> str:
        node_id = int(node_id)
        now = int(time.time())
        row = {
            "node_id": node_id,
            "ts": now,
            "status": int(status),
            "error_msg": str(error_msg or ""),
        }
        try:
            exists = self.table("node_monitor_latest").where("node_id=?", (node_id,)).count() > 0
            if exists:
                data = row.copy()
                data.pop("node_id", None)
                self.table("node_monitor_latest").where("node_id=?", (node_id,)).update(data)
            else:
                self.table("node_monitor_latest").insert(row)
        except Exception as e:
            return str(e)
        return ""

    def save_latest_services(self, node_id: int, services: List[Dict[str, Any]], error_msg: str = "") -> str:
        node_id = int(node_id)
        service_list = self._normalize_services(services if isinstance(services, list) else [])
        try:
            latest = self.get_latest(node_id)
            raw_json = latest.get("raw_json", {}) if latest else {}
            if not isinstance(raw_json, dict):
                raw_json = {}
            raw_json["services"] = service_list
            row = {
                "service_json": _json_dumps(service_list),
                "raw_json": _json_dumps(raw_json),
            }
            if latest:
                self.table("node_monitor_latest").where("node_id=?", (node_id,)).update(row)
            else:
                row.update({
                    "node_id": node_id,
                    "ts": int(time.time()),
                    "status": 2,
                    "error_msg": str(error_msg or ""),
                })
                self.table("node_monitor_latest").insert(row)
        except Exception as e:
            return str(e)
        return ""

    def get_latest(self, node_id: int) -> Dict[str, Any]:
        row = self.table("node_monitor_latest").where("node_id=?", (int(node_id),)).find()
        if not isinstance(row, dict) or not row:
            return {}
        return self._decode_latest_row(row)

    def _decode_latest_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        row = dict(row)
        row["disk_json"] = _json_loads(row.get("disk_json"), [])
        row["nic_json"] = _json_loads(row.get("nic_json"), [])
        row["service_json"] = _json_loads(row.get("service_json"), [])
        row["raw_json"] = _json_loads(row.get("raw_json"), {})
        return row

    def get_latest_view(self, node_id: int) -> Dict[str, Any]:
        latest = self.get_latest(node_id)
        if not latest:
            return {}
        targets = self.get_targets(node_id)
        target_map = {}
        for item in targets:
            target_map.setdefault(item["target_type"], []).append(item)

        latest["selected_disk"] = self._select_primary(latest["disk_json"], target_map.get("disk", []), "path")
        latest["selected_nic"] = self._select_primary(latest["nic_json"], target_map.get("nic", []), "name")
        service_targets = [item["target_key"] for item in target_map.get("service", []) if int(item.get("enabled", 0)) == 1]
        if service_targets:
            latest["service_json"] = [
                item for item in latest["service_json"]
                if isinstance(item, dict) and (item.get("target_key") in service_targets or item.get("name") in service_targets)
            ]
        return latest

    def get_list_monitor_map(self, node_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        node_ids = self._normalize_node_ids(node_ids)
        if not node_ids:
            return {}

        setting_list = []
        latest_list = []
        target_list = []
        for chunk_ids in self._chunk_node_ids(node_ids):
            placeholders = ",".join(["?"] * len(chunk_ids))
            params = tuple(chunk_ids)
            settings = self.table("node_monitor_setting").where(
                "node_id IN ({})".format(placeholders), params
            ).select()
            latest = self.table("node_monitor_latest").where(
                "node_id IN ({})".format(placeholders), params
            ).select()
            targets = self.table("node_monitor_target").where(
                "node_id IN ({})".format(placeholders), params
            ).order("node_id", "ASC").order("target_type", "ASC").order("sort", "ASC").order("id", "ASC").select()
            if isinstance(settings, list):
                setting_list.extend(settings)
            if isinstance(latest, list):
                latest_list.extend(latest)
            if isinstance(targets, list):
                target_list.extend(targets)

        setting_map = {}
        if isinstance(setting_list, list):
            setting_map = {int(item["node_id"]): item for item in setting_list if isinstance(item, dict)}

        latest_map = {}
        if isinstance(latest_list, list):
            latest_map = {
                int(item["node_id"]): self._decode_latest_row(item)
                for item in latest_list if isinstance(item, dict)
            }

        target_map = {node_id: {"disk": [], "nic": [], "service": []} for node_id in node_ids}
        if isinstance(target_list, list):
            for item in target_list:
                if not isinstance(item, dict):
                    continue
                node_id = int(item.get("node_id", 0))
                target_type = item.get("target_type")
                if node_id not in target_map or target_type not in target_map[node_id]:
                    continue
                item = dict(item)
                item["extra"] = _json_loads(item.get("extra"), {})
                target_map[node_id][target_type].append(item)

        return {
            node_id: self._build_list_monitor_item(
                node_id,
                setting_map.get(node_id) or self._default_setting_row(node_id),
                latest_map.get(node_id) or {},
                target_map.get(node_id) or {"disk": [], "nic": [], "service": []},
            )
            for node_id in node_ids
        }

    @staticmethod
    def _normalize_node_ids(node_ids: List[int]) -> List[int]:
        result = []
        seen = set()
        for node_id in node_ids:
            try:
                node_id = int(node_id)
            except Exception:
                continue
            if node_id <= 0 or node_id in seen:
                continue
            seen.add(node_id)
            result.append(node_id)
        return result

    @staticmethod
    def _chunk_node_ids(node_ids: List[int], chunk_size: int = 500) -> List[List[int]]:
        return [node_ids[idx:idx + chunk_size] for idx in range(0, len(node_ids), chunk_size)]

    @staticmethod
    def _default_setting_row(node_id: int) -> Dict[str, Any]:
        now = int(time.time())
        return {
            "id": 0,
            "node_id": int(node_id),
            "enabled": 1,
            "collect_interval": 60,
            "status_interval": 60,
            "detail_interval": 60,
            "snapshot_retention_days": DEFAULT_SNAPSHOT_RETENTION_DAYS,
            "cost_amount": 0,
            "cost_currency": "CNY",
            "cost_symbol": "",
            "cost_period": "month",
            "expire_at": 0,
            "remark": "",
            "created_at": now,
            "updated_at": now,
        }

    def _build_list_monitor_item(
            self,
            node_id: int,
            setting: Dict[str, Any],
            latest: Dict[str, Any],
            targets: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        disks = latest.get("disk_json", []) if isinstance(latest, dict) else []
        nics = latest.get("nic_json", []) if isinstance(latest, dict) else []
        services = latest.get("service_json", []) if isinstance(latest, dict) else []
        if not isinstance(disks, list):
            disks = []
        if not isinstance(nics, list):
            nics = []
        if not isinstance(services, list):
            services = []

        selected_disk = self._select_primary(disks, targets.get("disk", []), "path")
        selected_nic = self._select_primary(nics, targets.get("nic", []), "name")
        service_targets = [
            item.get("target_key")
            for item in targets.get("service", [])
            if int(item.get("enabled", 0)) == 1 and item.get("target_key")
        ]
        if service_targets:
            service_key_set = set(service_targets)
            services = [
                item for item in services
                if isinstance(item, dict) and (item.get("target_key") in service_key_set or item.get("name") in service_key_set)
            ]
        else:
            services = []

        summary = {
            "ts": _to_int(latest.get("ts", 0)) if latest else 0,
            "status": _to_int(latest.get("status", 0)) if latest else 0,
            "error_msg": str(latest.get("error_msg", "")) if latest else "",
            "cpu_usage": _percent(latest.get("cpu_usage", 0)) if latest else 0,
            "mem_usage": _percent(latest.get("mem_usage", 0)) if latest else 0,
            "mem_used": _to_int(latest.get("mem_used", 0)) if latest else 0,
            "mem_total": _to_int(latest.get("mem_total", 0)) if latest else 0,
            "load1": _to_float(latest.get("load1", 0)) if latest else 0,
            "load5": _to_float(latest.get("load5", 0)) if latest else 0,
            "load15": _to_float(latest.get("load15", 0)) if latest else 0,
        }
        latest_view = dict(summary)
        latest_view.update({
            "selected_disk": selected_disk,
            "selected_nic": selected_nic,
            "services": services,
        })

        return {
            "enabled": int(setting.get("enabled", 1)),
            "setting": setting,
            "summary": summary,
            "latest": latest_view,
            "selected_disk": selected_disk,
            "selected_nic": selected_nic,
            "disks": disks,
            "nics": nics,
            "services": services,
            "targets": targets,
            "cost": {
                "amount": _to_float(setting.get("cost_amount", 0)),
                "currency": str(setting.get("cost_currency", "")),
                "symbol": str(setting.get("cost_symbol", "")),
                "period": str(setting.get("cost_period", "")),
            },
            "expire": self._build_expire_info(setting.get("expire_at", 0)),
            "has_latest": bool(latest),
        }

    @staticmethod
    def _build_expire_info(expire_at: Any) -> Dict[str, Any]:
        expire_at = _to_int(expire_at)
        if expire_at <= 0:
            return {
                "expire_at": 0,
                "days_left": None,
                "status": "none",
                "expired": False,
                "is_soon": False,
            }
        now = int(time.time())
        seconds_left = expire_at - now
        if seconds_left >= 0:
            days_left = seconds_left // 86400
            if seconds_left % 86400:
                days_left += 1
        else:
            days_left = -((-seconds_left) // 86400)
            if seconds_left % 86400:
                days_left -= 1
        expired = seconds_left < 0
        is_soon = (not expired) and seconds_left <= 7 * 86400
        return {
            "expire_at": expire_at,
            "days_left": int(days_left),
            "status": "expired" if expired else ("soon" if is_soon else "normal"),
            "expired": expired,
            "is_soon": is_soon,
        }

    def get_alert_setting(self, node_id: int, create: bool = True) -> Dict[str, Any]:
        node_id = max(_to_int(node_id), 0)
        row = self.table("node_alert_setting").where("node_id=?", (node_id,)).find()
        if isinstance(row, dict) and row:
            return self._decode_alert_setting(row)
        if not create:
            return {}
        now = int(time.time())
        row = self._default_alert_setting_row(node_id)
        row.update({"created_at": now, "updated_at": now})
        self.table("node_alert_setting").insert({
            "node_id": row["node_id"],
            "sender_ids": _json_dumps(row["sender_ids"]),
            "send_interval_enabled": row["send_interval_enabled"],
            "send_interval": row["send_interval"],
            "time_range_enabled": row["time_range_enabled"],
            "time_range_start": row["time_range_start"],
            "time_range_end": row["time_range_end"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
        data = self.table("node_alert_setting").where("node_id=?", (node_id,)).find()
        return self._decode_alert_setting(data) if isinstance(data, dict) and data else row

    def save_alert_setting(self, node_id: int, data: Dict[str, Any]) -> str:
        node_id = max(_to_int(node_id), 0)
        row, err = self._normalize_alert_setting_data(data)
        if err:
            return err
        if not row:
            return ""
        now = int(time.time())
        row["updated_at"] = now
        try:
            old = self.get_alert_setting(node_id, create=False)
            if old:
                self.table("node_alert_setting").where("node_id=?", (node_id,)).update(row)
            else:
                default_row = self._default_alert_setting_row(node_id)
                insert_row = {
                    "node_id": node_id,
                    "sender_ids": _json_dumps(default_row["sender_ids"]),
                    "send_interval_enabled": default_row["send_interval_enabled"],
                    "send_interval": default_row["send_interval"],
                    "time_range_enabled": default_row["time_range_enabled"],
                    "time_range_start": default_row["time_range_start"],
                    "time_range_end": default_row["time_range_end"],
                    "created_at": now,
                    "updated_at": now,
                }
                insert_row.update(row)
                self.table("node_alert_setting").insert(insert_row)
        except Exception as e:
            return str(e)
        return ""

    @staticmethod
    def _default_alert_setting_row(node_id: int) -> Dict[str, Any]:
        return {
            "id": 0,
            "node_id": max(_to_int(node_id), 0),
            "sender_ids": [],
            "send_interval_enabled": 1,
            "send_interval": 1800,
            "time_range_enabled": 0,
            "time_range_start": 0,
            "time_range_end": 86400,
            "created_at": 0,
            "updated_at": 0,
            "scope": "global" if max(_to_int(node_id), 0) == 0 else "node",
        }

    @staticmethod
    def _decode_alert_setting(row: Dict[str, Any]) -> Dict[str, Any]:
        row = dict(row)
        row["sender_ids"] = NodeMonitorDB._normalize_sender_ids(row.get("sender_ids", []))
        row["scope"] = "global" if _to_int(row.get("node_id", 0)) == 0 else "node"
        return row

    @staticmethod
    def _normalize_sender_ids(value: Any) -> List[str]:
        if isinstance(value, str):
            value = _json_loads(value, [])
        if not isinstance(value, list):
            return []
        result = []
        seen = set()
        for item in value:
            sender_id = str(item).strip()
            if not sender_id or sender_id in seen:
                continue
            seen.add(sender_id)
            result.append(sender_id)
        return result

    @staticmethod
    def _normalize_alert_setting_data(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        row = {}
        if "sender_ids" in data:
            row["sender_ids"] = _json_dumps(NodeMonitorDB._normalize_sender_ids(data.get("sender_ids")))
        if "send_interval_enabled" in data:
            row["send_interval_enabled"] = 1 if _to_int(data.get("send_interval_enabled")) else 0
        if "send_interval" in data:
            row["send_interval"] = max(_to_int(data.get("send_interval"), 1800), 60)
        if "time_range_enabled" in data:
            row["time_range_enabled"] = 1 if _to_int(data.get("time_range_enabled")) else 0
        has_start = "time_range_start" in data
        has_end = "time_range_end" in data
        if has_start:
            row["time_range_start"] = _to_int(data.get("time_range_start"), 0)
        if has_end:
            row["time_range_end"] = _to_int(data.get("time_range_end"), 86400)
        start = row.get("time_range_start", _to_int(data.get("time_range_start", 0)))
        end = row.get("time_range_end", _to_int(data.get("time_range_end", 86400)))
        if has_start or has_end:
            if not (0 <= start <= 86400 and 0 <= end <= 86400):
                return {}, "time range format error"
            if _to_int(data.get("time_range_enabled", row.get("time_range_enabled", 0))) and start == end:
                return {}, "time range format error"
        return row, ""

    def get_alert_items(self, node_id: int = -1, include_global: bool = False, enabled_only: bool = False) -> List[Dict[str, Any]]:
        where = []
        params = []
        node_id = _to_int(node_id, -1)
        if node_id >= 0:
            if include_global and node_id > 0:
                where.append("(node_id=0 OR node_id=?)")
                params.append(node_id)
            else:
                where.append("node_id=?")
                params.append(node_id)
        if enabled_only:
            where.append("enabled=1")
        query = self.table("node_alert_item")
        if where:
            query = query.where(" AND ".join(where), tuple(params))
        data = query.order("node_id", "ASC").order("metric", "ASC").order("target_key", "ASC").order("id", "ASC").select()
        if not isinstance(data, list):
            return []
        return [self._decode_alert_item(item) for item in data if isinstance(item, dict)]

    def get_alert_item(self, item_id: int) -> Dict[str, Any]:
        row = self.table("node_alert_item").where("id=?", (_to_int(item_id),)).find()
        if not isinstance(row, dict) or not row:
            return {}
        return self._decode_alert_item(row)

    def save_alert_item(self, data: Dict[str, Any]) -> Tuple[int, str]:
        row, err = self._normalize_alert_item_data(data)
        if err:
            return 0, err
        item_id = _to_int(data.get("id", data.get("item_id", 0)))
        now = int(time.time())
        row["updated_at"] = now
        try:
            if item_id:
                old = self.get_alert_item(item_id)
                if not old:
                    return 0, "Alert item does not exist"
                self.table("node_alert_item").where("id=?", (item_id,)).update(row)
                return item_id, ""
            old = self.table("node_alert_item").where(
                "node_id=? AND metric=? AND target_key=?",
                (row["node_id"], row["metric"], row["target_key"]),
            ).find()
            if isinstance(old, dict) and old:
                self.table("node_alert_item").where("id=?", (old["id"],)).update(row)
                return _to_int(old.get("id")), ""
            row["created_at"] = now
            new_id = self.table("node_alert_item").insert(row)
            return _to_int(new_id, 0), "" if not isinstance(new_id, str) else new_id
        except Exception as e:
            return 0, str(e)

    def save_alert_items(self, node_id: int, items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
        node_id = max(_to_int(node_id), 0)
        if not isinstance(items, list):
            return [], "items format error"
        result = []
        for item in items:
            if not isinstance(item, dict):
                continue
            data = dict(item)
            data["node_id"] = node_id
            item_id, err = self.save_alert_item(data)
            if err:
                return result, err
            result.append(self.get_alert_item(item_id))
        return result, ""

    def set_alert_item_status(self, item_id: int, enabled: int) -> str:
        item_id = _to_int(item_id)
        if item_id <= 0:
            return "item_id cannot be empty"
        try:
            self.table("node_alert_item").where("id=?", (item_id,)).update({
                "enabled": 1 if _to_int(enabled) else 0,
                "updated_at": int(time.time()),
            })
        except Exception as e:
            return str(e)
        return ""

    def delete_alert_item(self, item_id: int) -> str:
        item_id = _to_int(item_id)
        if item_id <= 0:
            return "item_id cannot be empty"
        try:
            self.table("node_alert_item").where("id=?", (item_id,)).delete()
            self.table("node_alert_state").where("item_id=?", (item_id,)).delete()
        except Exception as e:
            return str(e)
        return ""

    @staticmethod
    def _decode_alert_item(row: Dict[str, Any]) -> Dict[str, Any]:
        row = dict(row)
        row["scope"] = "global" if _to_int(row.get("node_id", 0)) == 0 else "node"
        return row

    @staticmethod
    def _normalize_alert_item_data(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        metric = str(data.get("metric", "")).strip()[:64]
        if not metric:
            return {}, "metric cannot be empty"
        operator = str(data.get("operator", ">=")).strip()
        if operator not in (">", ">=", "<", "<=", "==", "!="):
            return {}, "Unsupported alert operator"
        row = {
            "node_id": max(_to_int(data.get("node_id", 0)), 0),
            "metric": metric,
            "enabled": 1 if _to_int(data.get("enabled", 0)) else 0,
            "operator": operator,
            "threshold": _to_float(data.get("threshold", 0)),
            "threshold_unit": str(data.get("threshold_unit", "") or "").strip()[:32],
            "duration_minutes": max(_to_int(data.get("duration_minutes", 1)), 0),
            "target_key": str(data.get("target_key", "") or "").strip()[:255],
            "target_name": str(data.get("target_name", "") or "").strip()[:255],
        }
        return row, ""

    def get_alert_state(self, node_id: int, metric: str, target_key: str = "") -> Dict[str, Any]:
        row = self.table("node_alert_state").where(
            "node_id=? AND metric=? AND target_key=?",
            (_to_int(node_id), str(metric or ""), str(target_key or "")),
        ).find()
        if not isinstance(row, dict) or not row:
            return {}
        return row

    def upsert_alert_state(self, node_id: int, metric: str, target_key: str, data: Dict[str, Any]) -> str:
        node_id = _to_int(node_id)
        metric = str(metric or "")
        target_key = str(target_key or "")
        now = int(time.time())
        row = {
            "item_id": _to_int(data.get("item_id", 0)),
            "status": str(data.get("status", "normal")),
            "last_value": _to_float(data.get("last_value", 0)),
            "last_message": str(data.get("last_message", ""))[:1000],
            "first_trigger_at": _to_int(data.get("first_trigger_at", 0)),
            "last_checked_at": _to_int(data.get("last_checked_at", now)),
            "last_sent_at": _to_int(data.get("last_sent_at", 0)),
            "send_count": _to_int(data.get("send_count", 0)),
            "updated_at": now,
        }
        try:
            old = self.get_alert_state(node_id, metric, target_key)
            if old:
                self.table("node_alert_state").where("id=?", (old["id"],)).update(row)
            else:
                row.update({
                    "node_id": node_id,
                    "metric": metric,
                    "target_key": target_key,
                })
                self.table("node_alert_state").insert(row)
        except Exception as e:
            return str(e)
        return ""

    def get_alert_states(self, node_id: int = 0, metric: str = "", status: str = "", item_id: int = 0, limit: int = 1000) -> List[Dict[str, Any]]:
        where = []
        params = []
        if _to_int(node_id):
            where.append("node_id=?")
            params.append(_to_int(node_id))
        if metric:
            where.append("metric=?")
            params.append(str(metric))
        if status:
            where.append("status=?")
            params.append(str(status))
        if _to_int(item_id):
            where.append("item_id=?")
            params.append(_to_int(item_id))
        query = self.table("node_alert_state")
        if where:
            query = query.where(" AND ".join(where), tuple(params))
        data = query.order("updated_at", "DESC").limit(max(1, min(_to_int(limit, 1000), 5000))).select()
        return data if isinstance(data, list) else []

    def add_alert_history(self, data: Dict[str, Any]) -> str:
        row = {
            "node_id": _to_int(data.get("node_id", 0)),
            "item_id": _to_int(data.get("item_id", 0)),
            "metric": str(data.get("metric", "")),
            "target_key": str(data.get("target_key", "")),
            "trigger_value": _to_float(data.get("trigger_value", 0)),
            "operator": str(data.get("operator", "")),
            "threshold": _to_float(data.get("threshold", 0)),
            "threshold_unit": str(data.get("threshold_unit", "") or "").strip()[:32],
            "action": str(data.get("action", "")),
            "message": str(data.get("message", ""))[:2000],
            "sender_ids": _json_dumps(self._normalize_sender_ids(data.get("sender_ids", []))),
            "send_result": _json_dumps(data.get("send_result", {})),
            "created_at": _to_int(data.get("created_at", int(time.time()))),
        }
        try:
            self.table("node_alert_history").insert(row)
        except Exception as e:
            return str(e)
        return ""

    def get_alert_history(self, node_id: int = 0, metric: str = "", item_id: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        where = []
        params = []
        if _to_int(node_id):
            where.append("node_id=?")
            params.append(_to_int(node_id))
        if metric:
            where.append("metric=?")
            params.append(str(metric))
        if _to_int(item_id):
            where.append("item_id=?")
            params.append(_to_int(item_id))
        query = self.table("node_alert_history")
        if where:
            query = query.where(" AND ".join(where), tuple(params))
        data = query.order("created_at", "DESC").limit(max(1, min(_to_int(limit, 100), 1000))).select()
        if not isinstance(data, list):
            return []
        for item in data:
            if isinstance(item, dict):
                item["sender_ids"] = _json_loads(item.get("sender_ids"), [])
                item["send_result"] = _json_loads(item.get("send_result"), {})
        return data

    @staticmethod
    def _select_primary(items: List[Dict[str, Any]], targets: List[Dict[str, Any]], item_key: str) -> Dict[str, Any]:
        if not isinstance(items, list) or not items:
            return {}
        primary_key = ""
        for target in targets:
            if int(target.get("is_primary", 0)) == 1:
                primary_key = target.get("target_key", "")
                break
        if primary_key:
            for item in items:
                if isinstance(item, dict) and item.get(item_key) == primary_key:
                    return item
        return items[0] if isinstance(items[0], dict) else {}

    def get_snapshots(self, node_id: int, start_ts: int = 0, end_ts: int = 0, limit: int = 1440) -> List[Dict[str, Any]]:
        where = ["node_id=?"]
        params = [int(node_id)]
        if start_ts:
            where.append("ts>=?")
            params.append(int(start_ts))
        if end_ts:
            where.append("ts<=?")
            params.append(int(end_ts))
        limit = max(1, min(int(limit), 10080))
        data = self.table("node_monitor_snapshot").where(" AND ".join(where), tuple(params)).order("ts", "DESC").limit(limit).select()
        if not isinstance(data, list):
            return []
        result = [self._decode_latest_row(item) for item in data if isinstance(item, dict)]
        result.reverse()
        return result

    def cleanup_snapshots(self, before_ts: int) -> str:
        try:
            self.table("node_monitor_snapshot").where("ts<?", (int(before_ts),)).delete()
        except Exception as e:
            return str(e)
        return ""

    def cleanup_expired_snapshots(self) -> str:
        now = int(time.time())
        try:
            settings = self.table("node_monitor_setting").field("node_id,snapshot_retention_days").select()
            if not isinstance(settings, list) or not settings:
                return self.cleanup_snapshots(now - DEFAULT_SNAPSHOT_RETENTION_DAYS * 86400)
            cleaned_nodes = set()
            for item in settings:
                if not isinstance(item, dict):
                    continue
                node_id = _to_int(item.get("node_id", 0))
                if node_id <= 0 or node_id in cleaned_nodes:
                    continue
                cleaned_nodes.add(node_id)
                retention_days = _normalize_retention_days(item.get("snapshot_retention_days"))
                before_ts = now - retention_days * 86400
                self.table("node_monitor_snapshot").where("node_id=? AND ts<?", (node_id, before_ts)).delete()
        except Exception as e:
            return str(e)
        return ""
