# coding: utf-8
import json
from typing import Any, Dict, List, Tuple

import public
from mod.project.node.dbutil import NodeMonitorDB
from mod.project.node.nodeutil.alert_engine import METRIC_DEFINITIONS, METRIC_LABELS, NodeAlertEngine


def _json_loads(value: Any, default: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str) or not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _get_int(get, key: str, default: int = 0) -> int:
    try:
        return int(float(get.get("{}/d".format(key), get.get(key, default))))
    except Exception:
        return default


def _get_float(get, key: str, default: float = 0.0) -> float:
    try:
        return float(get.get(key, default))
    except Exception:
        return default


def _get_str(get, key: str, default: str = "") -> str:
    try:
        value = get.get("{}/s".format(key), get.get(key, default))
    except Exception:
        value = default
    return str(value if value is not None else default)


def _get_raw(get, key: str, default: Any = None) -> Any:
    try:
        return get.get(key, default)
    except Exception:
        return default


class main:
    def __init__(self):
        self.monitor_db = NodeMonitorDB()
        self.monitor_db.init_db()

    def get_metric_options(self, get):
        return public.return_message(0, 0, {
            "metrics": self._metric_options(),
            "operators": [">", ">=", "<", "<=", "==", "!="],
            "defaults": self._default_items(0),
        })

    def get_sender_list(self, get):
        try:
            from mod.base.push_mod.mods import SenderConfig
            senders = []
            allowed = ("weixin", "mail", "webhook", "feishu", "dingding", "tg", "discord")
            for item in SenderConfig().config:
                if item.get("sender_type") not in allowed:
                    continue
                senders.append(item)
            senders.sort(key=lambda x: x.get("sender_type", ""))
            return public.return_message(0, 0, {
                "senders": senders,
                "source_api": "/v2/mod/push/msgconf/get_sender_list",
            })
        except Exception as e:
            return public.return_message(-1, 0, str(e))

    def get_config(self, get):
        """
        获取节点监控配置
        """
        node_id = self._scope_node_id(get)
        limit = _get_int(get, "history_limit", 50)
        data = self._build_config(node_id, limit)
        public.set_module_logs('node_alert', 'node_alert_get_config')
        return public.return_message(0, 0, data)

    def save_config(self, get):
        node_id = self._scope_node_id(get)
        setting_data = self._parse_setting_data(get)
        items, items_err = self._parse_items_data(get, node_id, required=False)
        if items_err:
            return public.return_message(-1, 0, items_err)

        existing_setting = self.monitor_db.get_alert_setting(node_id, create=True)
        sender_ids = setting_data.get("sender_ids", existing_setting.get("sender_ids", []))
        enabled_items = items if items is not None else self.monitor_db.get_alert_items(node_id, enabled_only=True)
        sender_err = self._validate_sender_ids(sender_ids, self._has_enabled_items(enabled_items))
        if sender_err:
            return public.return_message(-1, 0, sender_err)

        if setting_data:
            err = self.monitor_db.save_alert_setting(node_id, setting_data)
            if err:
                return public.return_message(-1, 0, err)
        if items is not None:
            _, err = self.monitor_db.save_alert_items(node_id, items)
            if err:
                return public.return_message(-1, 0, err)
        public.WriteLog("node", f"Set Node Alert Configuration")
        public.set_module_logs('node_alert', 'node_alert_save_config')
        return public.return_message(0, 0, "Set successfully")

    def save_setting(self, get):
        node_id = self._scope_node_id(get)
        setting_data = self._parse_setting_data(get)
        existing_items = self.monitor_db.get_alert_items(node_id, enabled_only=True)
        sender_ids = setting_data.get("sender_ids", self.monitor_db.get_alert_setting(node_id, create=True).get("sender_ids", []))
        sender_err = self._validate_sender_ids(sender_ids, self._has_enabled_items(existing_items))
        if sender_err:
            return public.return_message(-1, 0, sender_err)
        err = self.monitor_db.save_alert_setting(node_id, setting_data)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, self.monitor_db.get_alert_setting(node_id, create=True))

    def save_items(self, get):
        node_id = self._scope_node_id(get)
        items, err = self._parse_items_data(get, node_id, required=True)
        if err:
            return public.return_message(-1, 0, err)
        setting = self.monitor_db.get_alert_setting(node_id, create=True)
        sender_err = self._validate_sender_ids(setting.get("sender_ids", []), self._has_enabled_items(items))
        if sender_err:
            return public.return_message(-1, 0, sender_err)
        saved, err = self.monitor_db.save_alert_items(node_id, items)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, {"items": [self._with_metric_meta(item) for item in saved]})

    def set_item_status(self, get):
        item_id = _get_int(get, "item_id", _get_int(get, "id", 0))
        enabled = _get_int(get, "enabled", _get_int(get, "status", 1))
        if item_id:
            old_item = self.monitor_db.get_alert_item(item_id)
            if enabled and old_item:
                setting = self.monitor_db.get_alert_setting(old_item.get("node_id", 0), create=True)
                sender_err = self._validate_sender_ids(setting.get("sender_ids", []), True)
                if sender_err:
                    return public.return_message(-1, 0, sender_err)
            err = self.monitor_db.set_alert_item_status(item_id, enabled)
            if err:
                return public.return_message(-1, 0, err)
            return public.return_message(0, 0, self._with_metric_meta(self.monitor_db.get_alert_item(item_id)))

        node_id = self._scope_node_id(get)
        if enabled:
            setting = self.monitor_db.get_alert_setting(node_id, create=True)
            sender_err = self._validate_sender_ids(setting.get("sender_ids", []), True)
            if sender_err:
                return public.return_message(-1, 0, sender_err)
        metric = _get_str(get, "metric")
        target_key = _get_str(get, "target_key")
        item, err = self._normalize_item_data({
            "node_id": node_id,
            "metric": metric,
            "target_key": target_key,
            "enabled": enabled,
        }, node_id)
        if err:
            return public.return_message(-1, 0, err)
        item_id, err = self.monitor_db.save_alert_item(item)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, self._with_metric_meta(self.monitor_db.get_alert_item(item_id)))

    def delete_item(self, get):
        item_id = _get_int(get, "item_id", _get_int(get, "id", 0))
        err = self.monitor_db.delete_alert_item(item_id)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, "Deleted successfully")

    def get_states(self, get):
        node_id = _get_int(get, "node_id", 0)
        metric = _get_str(get, "metric")
        status = _get_str(get, "status")
        item_id = _get_int(get, "item_id", 0)
        limit = _get_int(get, "limit", 1000)
        return public.return_message(0, 0, {
            "states": self.monitor_db.get_alert_states(node_id, metric, status, item_id, limit)
        })

    def get_history(self, get):
        node_id = _get_int(get, "node_id", 0)
        metric = _get_str(get, "metric")
        item_id = _get_int(get, "item_id", 0)
        limit = _get_int(get, "limit", 100)
        return public.return_message(0, 0, {
            "history": self.monitor_db.get_alert_history(node_id, metric, item_id, limit)
        })

    def scan_once(self, get):
        node_id = _get_int(get, "node_id", 0)
        force = _get_int(get, "force", _get_int(get, "force_send", 0)) == 1
        return public.return_message(0, 0, NodeAlertEngine().scan_once(node_id, force))

    def _build_config(self, node_id: int, history_limit: int = 50) -> Dict[str, Any]:
        setting = self.monitor_db.get_alert_setting(node_id, create=True)
        global_setting = self.monitor_db.get_alert_setting(0, create=True)
        items = self._build_items(node_id)
        global_items = self._build_items(0)
        data = {
            "node_id": node_id,
            "scope": "global" if node_id == 0 else "node",
            "setting": setting,
            "items": items,
            "global_setting": global_setting,
            "global_items": global_items,
            "metrics": self._metric_options(),
            "states": self.monitor_db.get_alert_states(node_id, limit=1000) if node_id else [],
            "history": self.monitor_db.get_alert_history(node_id, limit=history_limit) if node_id else [],
        }
        senders = self.get_sender_list(None)
        if isinstance(senders, dict) and senders.get("status") == 0:
            data["senders"] = senders.get("message", {}).get("senders", [])
        else:
            data["senders"] = []
        return data

    def _build_items(self, node_id: int) -> List[Dict[str, Any]]:
        node_id = max(int(node_id), 0)
        defaults = self._default_items(node_id)
        item_map = {(item["metric"], item.get("target_key", "")): item for item in defaults}
        extra_items = []
        for item in self.monitor_db.get_alert_items(node_id):
            key = (item.get("metric", ""), item.get("target_key", ""))
            item = self._with_metric_meta(item)
            if key in item_map:
                item_map[key].update(item)
            else:
                extra_items.append(item)
        result = list(item_map.values())
        result.extend(extra_items)
        return result

    @staticmethod
    def _metric_options() -> List[Dict[str, Any]]:
        result = []
        for metric, meta in METRIC_DEFINITIONS.items():
            item = dict(meta)
            item["metric"] = metric
            result.append(item)
        return result

    @staticmethod
    def _default_items(node_id: int) -> List[Dict[str, Any]]:
        result = []
        for metric, meta in METRIC_DEFINITIONS.items():
            result.append({
                "id": 0,
                "node_id": max(int(node_id), 0),
                "metric": metric,
                "label": meta.get("label", metric),
                "enabled": 0,
                "operator": meta.get("operator", ">="),
                "threshold": meta.get("threshold", 0),
                "threshold_unit": meta.get("threshold_unit", ""),
                "duration_minutes": meta.get("duration_minutes", 1),
                "target_key": "",
                "target_name": "",
                "unit": meta.get("unit", ""),
                "unit_options": meta.get("unit_options", []),
                "target_type": meta.get("target_type", ""),
                "scope": "global" if int(node_id) == 0 else "node",
            })
        return result

    @staticmethod
    def _with_metric_meta(item: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(item, dict):
            return {}
        item = dict(item)
        metric = item.get("metric", "")
        meta = METRIC_DEFINITIONS.get(metric, {})
        item["label"] = meta.get("label", METRIC_LABELS.get(metric, metric))
        item["unit"] = meta.get("unit", "")
        item["unit_options"] = meta.get("unit_options", [])
        item["threshold_unit"] = main._normalize_threshold_unit(metric, item.get("threshold_unit") or meta.get("threshold_unit", ""))
        item["target_type"] = meta.get("target_type", "")
        item["scope"] = "global" if _to_int(item.get("node_id", 0)) == 0 else "node"
        return item

    @staticmethod
    def _scope_node_id(get) -> int:
        scope = _get_str(get, "scope")
        if scope == "global" or _get_int(get, "is_global", 0):
            return 0
        return max(_get_int(get, "node_id", 0), 0)

    def _parse_setting_data(self, get) -> Dict[str, Any]:
        raw = _get_raw(get, "setting", None)
        data = _json_loads(raw, {}) if raw is not None else {}
        if not isinstance(data, dict):
            data = {}
        fields = (
            "sender_ids", "send_interval_enabled", "send_interval",
            "time_range_enabled", "time_range_start", "time_range_end",
        )
        for key in fields:
            value = _get_raw(get, key, None)
            if value is not None:
                data[key] = value
        time_range = _get_raw(get, "time_range", data.get("time_range", None))
        time_range = _json_loads(time_range, time_range)
        if isinstance(time_range, list) and len(time_range) == 2:
            data["time_range_start"] = _to_int(time_range[0])
            data["time_range_end"] = _to_int(time_range[1])
        if "sender_ids" in data and isinstance(data["sender_ids"], str):
            data["sender_ids"] = _json_loads(data["sender_ids"], [])
        for key in ("send_interval_enabled", "send_interval", "time_range_enabled", "time_range_start", "time_range_end"):
            if key in data:
                data[key] = _to_int(data[key])
        return data

    def _parse_items_data(self, get, node_id: int, required: bool = False) -> Tuple[Any, str]:
        raw = _get_raw(get, "items", _get_raw(get, "alert_items", None))
        if raw is None:
            if not required:
                return None, ""
            return [], "items cannot be empty"
        items = _json_loads(raw, raw)
        if not isinstance(items, list):
            return [], "items format error"
        result = []
        for item in items:
            data, err = self._normalize_item_data(item, node_id)
            if err:
                return result, err
            result.append(data)
        return result, ""

    def _normalize_item_data(self, item: Any, node_id: int) -> Tuple[Dict[str, Any], str]:
        if not isinstance(item, dict):
            return {}, "item format error"
        metric = str(item.get("metric", "")).strip()
        if metric not in METRIC_DEFINITIONS:
            return {}, "Unsupported alert metric: {}".format(metric)
        meta = METRIC_DEFINITIONS[metric]
        data = {
            "id": _to_int(item.get("id", item.get("item_id", 0))),
            "node_id": max(int(node_id), 0),
            "metric": metric,
            "enabled": 1 if _to_int(item.get("enabled", 0)) else 0,
            "operator": str(item.get("operator", meta.get("operator", ">="))).strip(),
            "threshold": _to_float(item.get("threshold", meta.get("threshold", 0))),
            "threshold_unit": self._normalize_threshold_unit(metric, item.get("threshold_unit") or meta.get("threshold_unit", "")),
            "duration_minutes": max(_to_int(item.get("duration_minutes", meta.get("duration_minutes", 1))), 0),
            "target_key": str(item.get("target_key", "") or "").strip(),
            "target_name": str(item.get("target_name", "") or "").strip(),
        }
        if metric == "offline":
            data["operator"] = "=="
            data["threshold"] = 1
            data["threshold_unit"] = ""
            data["target_key"] = ""
            data["target_name"] = ""
        elif metric == "expire":
            data["operator"] = "<="
            data["threshold_unit"] = "days"
            data["target_key"] = ""
            data["target_name"] = ""
        elif not meta.get("target_type"):
            data["target_key"] = ""
            data["target_name"] = ""
        if data["operator"] not in (">", ">=", "<", "<=", "==", "!="):
            return {}, "Unsupported alert operator"
        return data, ""

    @staticmethod
    def _normalize_threshold_unit(metric: str, unit: Any) -> str:
        raw = str(unit or "").strip()
        key = raw.upper().replace(" ", "")
        if metric in ("bandwidth_up", "bandwidth_down"):
            if key in ("MB", "M", "MB/S", "M/S", "MBS"):
                return "MB/s"
            return "KB/s"
        if metric in ("traffic_up", "traffic_down"):
            if key in ("GB", "G", "GIB"):
                return "GB"
            if key in ("B", "BYTE", "BYTES"):
                return "B"
            return "MB"
        if metric in ("cpu_usage", "mem_usage", "disk_usage"):
            return "%"
        if metric == "expire":
            return "days"
        return raw

    @staticmethod
    def _has_enabled_items(items: Any) -> bool:
        if not isinstance(items, list):
            return False
        for item in items:
            if isinstance(item, dict) and _to_int(item.get("enabled", 0)) == 1:
                return True
        return False

    @staticmethod
    def _validate_sender_ids(sender_ids: List[Any], required: bool = False) -> str:
        if isinstance(sender_ids, str):
            sender_ids = _json_loads(sender_ids, [])
        if not isinstance(sender_ids, list) or not sender_ids:
            return "No alarm channel is configured" if required else ""
        try:
            from mod.base.push_mod.mods import SenderConfig
            sender_config = SenderConfig()
            for sender_id in sender_ids:
                sender = sender_config.get_by_id(str(sender_id))
                if not sender:
                    return "Alarm channel does not exist: {}".format(sender_id)
                if sender.get("sender_type") in ("sms", "wx_account"):
                    return "Unsupported alarm channel: {}".format(sender.get("sender_type"))
                if not sender.get("used", True):
                    return "Alarm channel is disabled: {}".format(sender.get("data", {}).get("title", sender_id))
        except Exception as e:
            return str(e)
        return ""


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default
