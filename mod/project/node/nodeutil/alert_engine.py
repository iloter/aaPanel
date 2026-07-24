# coding: utf-8
import datetime
import html
import time
from typing import Any, Dict, List, Tuple

import public
from mod.project.node.dbutil import NodeMonitorDB, ServerNodeDB


METRIC_DEFINITIONS = {
    "offline": {
        "label": "Node offline",
        "operator": "==",
        "threshold": 1,
        "threshold_unit": "",
        "unit_options": [],
        "duration_minutes": 1,
        "unit": "",
        "target_type": "",
    },
    "cpu_usage": {
        "label": "CPU usage",
        "operator": ">=",
        "threshold": 80,
        "threshold_unit": "%",
        "unit_options": ["%"],
        "duration_minutes": 1,
        "unit": "%",
        "target_type": "",
    },
    "mem_usage": {
        "label": "Memory usage",
        "operator": ">=",
        "threshold": 80,
        "threshold_unit": "%",
        "unit_options": ["%"],
        "duration_minutes": 1,
        "unit": "%",
        "target_type": "",
    },
    "disk_usage": {
        "label": "Disk usage",
        "operator": ">=",
        "threshold": 80,
        "threshold_unit": "%",
        "unit_options": ["%"],
        "duration_minutes": 1,
        "unit": "%",
        "target_type": "disk",
    },
    "bandwidth_up": {
        "label": "Upload bandwidth",
        "operator": ">=",
        "threshold": 0,
        "threshold_unit": "KB/s",
        "unit_options": ["KB/s", "MB/s"],
        "duration_minutes": 1,
        "unit": "KB/s",
        "target_type": "nic",
    },
    "bandwidth_down": {
        "label": "Download bandwidth",
        "operator": ">=",
        "threshold": 0,
        "threshold_unit": "KB/s",
        "unit_options": ["KB/s", "MB/s"],
        "duration_minutes": 1,
        "unit": "KB/s",
        "target_type": "nic",
    },
    "traffic_up": {
        "label": "Upload traffic",
        "operator": ">=",
        "threshold": 0,
        "threshold_unit": "GB",
        "unit_options": ["MB", "GB"],
        "duration_minutes": 1,
        "unit": "MB/GB",
        "target_type": "nic",
    },
    "traffic_down": {
        "label": "Download traffic",
        "operator": ">=",
        "threshold": 0,
        "threshold_unit": "GB",
        "unit_options": ["MB", "GB"],
        "duration_minutes": 1,
        "unit": "MB/GB",
        "target_type": "nic",
    },
    "expire": {
        "label": "Expiration time",
        "operator": "<=",
        "threshold": 7,
        "threshold_unit": "days",
        "unit_options": ["days"],
        "duration_minutes": 0,
        "unit": "days",
        "target_type": "",
    },
}

METRIC_LABELS = {key: item["label"] for key, item in METRIC_DEFINITIONS.items()}


class NodeAlertEngine:
    def __init__(self):
        self.monitor_db = NodeMonitorDB()
        self.node_db = ServerNodeDB()

    def scan_once(self, node_id: int = 0, force: bool = False) -> Dict[str, Any]:
        nodes = self._load_nodes(node_id)
        node_ids = [int(item.get("id", 0)) for item in nodes if int(item.get("id", 0)) > 0]
        monitor_map = self.monitor_db.get_list_monitor_map(node_ids)
        global_items = self.monitor_db.get_alert_items(0, enabled_only=True)
        global_setting = self.monitor_db.get_alert_setting(0, create=True)

        checked = triggered = sent = 0
        errors = []
        for node in nodes:
            if not node or node.get("lpver"):
                continue
            actual_node_id = int(node.get("id", 0))
            if actual_node_id <= 0:
                continue
            try:
                node_items = self.monitor_db.get_alert_items(actual_node_id, enabled_only=False)
                node_setting = self.monitor_db.get_alert_setting(actual_node_id, create=False)
                items = self._build_effective_items(global_items, node_items)
                monitor = monitor_map.get(actual_node_id, {})
                for item in items:
                    checked += 1
                    setting = self._setting_for_item(item, node_setting, global_setting)
                    result = self._check_item_node(item, setting, node, monitor, force)
                    if result.get("triggered"):
                        triggered += 1
                    if result.get("sent"):
                        sent += 1
            except Exception as e:
                errors.append(str(e))
                if public.is_debug():
                    public.print_error()

        return {
            "checked": checked,
            "triggered": triggered,
            "sent": sent,
            "force": bool(force),
            "errors": errors,
        }

    def _load_nodes(self, node_id: int = 0) -> List[Dict[str, Any]]:
        if node_id:
            node = self.node_db.get_node_by_id(int(node_id))
            return [node] if node else []
        data = public.S("node", self.node_db._DB_FILE).select()
        return data if isinstance(data, list) else []

    @staticmethod
    def _build_effective_items(global_items: List[Dict[str, Any]], node_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        item_map = {}
        for item in global_items if isinstance(global_items, list) else []:
            if int(item.get("enabled", 0)) != 1:
                continue
            item_map[(item.get("metric", ""), item.get("target_key", ""))] = item
        for item in node_items if isinstance(node_items, list) else []:
            key = (item.get("metric", ""), item.get("target_key", ""))
            if int(item.get("enabled", 0)) == 1:
                item_map[key] = item
            else:
                item_map.pop(key, None)
        return list(item_map.values())

    @staticmethod
    def _setting_for_item(item: Dict[str, Any], node_setting: Dict[str, Any], global_setting: Dict[str, Any]) -> Dict[str, Any]:
        if int(item.get("node_id", 0)) == 0:
            return global_setting or {}
        return node_setting or global_setting or {}

    def _check_item_node(
            self,
            item: Dict[str, Any],
            setting: Dict[str, Any],
            node: Dict[str, Any],
            monitor: Dict[str, Any],
            force: bool = False,
    ) -> Dict[str, Any]:
        node_id = int(node.get("id", 0))
        metric = str(item.get("metric", ""))
        target_key = self._real_target_key(item, monitor)
        state = self.monitor_db.get_alert_state(node_id, metric, target_key)
        if metric == "offline" and self._is_local_node(node):
            now = int(time.time())
            self.monitor_db.upsert_alert_state(node_id, metric, target_key, {
                "item_id": item.get("id", 0),
                "status": "normal",
                "last_value": 0,
                "last_message": "Local node offline alert skipped",
                "first_trigger_at": 0,
                "last_checked_at": now,
                "last_sent_at": int(state.get("last_sent_at", 0)) if state else 0,
                "send_count": int(state.get("send_count", 0)) if state else 0,
            })
            return {"triggered": False, "sent": False, "reason": "local_node_offline_skipped"}
        metric_data = self._metric_value(item, node, monitor)
        value = metric_data["value"]
        display_value = metric_data["display_value"]
        ok = metric_data["ok"]
        message = metric_data["message"]
        operator = metric_data["operator"]
        threshold = metric_data["threshold"]
        threshold_display = metric_data["threshold_display"]
        threshold_unit = metric_data["threshold_unit"]
        now = int(time.time())

        if not ok:
            normal_message = self._format_normal_message(
                item, node, display_value, operator, threshold_display, threshold_unit, message
            )
            self.monitor_db.upsert_alert_state(node_id, metric, target_key, {
                "item_id": item.get("id", 0),
                "status": "normal",
                "last_value": value,
                "last_message": normal_message,
                "first_trigger_at": 0,
                "last_checked_at": now,
                "last_sent_at": int(state.get("last_sent_at", 0)) if state else 0,
                "send_count": int(state.get("send_count", 0)) if state else 0,
            })
            return {"triggered": False, "sent": False}

        first_trigger_at = int(state.get("first_trigger_at", 0)) if state and state.get("status") == "alert" else now
        last_sent_at = int(state.get("last_sent_at", 0)) if state else 0
        send_count = int(state.get("send_count", 0)) if state else 0
        self.monitor_db.upsert_alert_state(node_id, metric, target_key, {
            "item_id": item.get("id", 0),
            "status": "alert",
            "last_value": value,
            "last_message": message,
            "first_trigger_at": first_trigger_at,
            "last_checked_at": now,
            "last_sent_at": last_sent_at,
            "send_count": send_count,
        })

        duration_seconds = max(int(item.get("duration_minutes", 0)), 0) * 60
        if not force and duration_seconds and now - first_trigger_at < duration_seconds:
            return {"triggered": True, "sent": False, "reason": "duration_wait"}

        if not force and self._send_interval_blocked(setting, last_sent_at, now):
            return {"triggered": True, "sent": False, "reason": "send_interval"}

        if not self._in_time_range(setting):
            if not state or state.get("status") != "alert":
                self._save_history(
                    item, setting, node, target_key, display_value, operator,
                    threshold_display, threshold_unit, "blocked_time_range", message, {}
                )
            return {"triggered": True, "sent": False, "reason": "time_range"}

        sender_ids = setting.get("sender_ids", [])
        if not isinstance(sender_ids, list) or not sender_ids:
            if not state or state.get("status") != "alert":
                self._save_history(item, setting, node, target_key, display_value, operator, threshold_display, threshold_unit, "no_sender", message, {
                    "_error": "No alarm channel is configured",
                })
            return {"triggered": True, "sent": False, "reason": "no_sender"}

        send_result = self._send(item, setting, node, display_value, threshold_unit, message, operator, threshold_display)
        is_sent = any(item == 1 for item in send_result.values())
        action = "sent" if is_sent else "send_failed"
        self._save_history(item, setting, node, target_key, display_value, operator, threshold_display, threshold_unit, action, message, send_result)
        if is_sent:
            send_count += 1
        self.monitor_db.upsert_alert_state(node_id, metric, target_key, {
            "item_id": item.get("id", 0),
            "status": "alert",
            "last_value": value,
            "last_message": message,
            "first_trigger_at": first_trigger_at,
            "last_checked_at": now,
            "last_sent_at": now,
            "send_count": send_count,
        })
        return {"triggered": True, "sent": is_sent}

    @staticmethod
    def _real_target_key(item: Dict[str, Any], monitor: Dict[str, Any]) -> str:
        if item.get("target_key"):
            return str(item.get("target_key"))
        metric = item.get("metric")
        if metric == "disk_usage":
            return str((monitor.get("selected_disk") or {}).get("path", ""))
        if metric in ("bandwidth_up", "bandwidth_down", "traffic_up", "traffic_down"):
            return str((monitor.get("selected_nic") or {}).get("name", ""))
        return ""

    @staticmethod
    def _is_local_node(node: Dict[str, Any]) -> bool:
        return str(node.get("app_key", "")) == "local" and str(node.get("api_key", "")) == "local"

    # 给节点名加 [ ] 强化显示
    @staticmethod
    def _node_name(node: Dict[str, Any], marked: bool = False) -> str:
        name = str(node.get("remarks") or node.get("address") or "Node {}".format(node.get("id"))).strip()
        if not name:
            name = "Node {}".format(node.get("id"))
        if marked and not (name.startswith("[") and name.endswith("]")):
            return "[{}]".format(name)
        return name

    def _metric_value(
            self,
            item: Dict[str, Any],
            node: Dict[str, Any],
            monitor: Dict[str, Any],
    ) -> Dict[str, Any]:
        metric = item.get("metric", "")
        meta = METRIC_DEFINITIONS.get(metric, {})
        operator = str(item.get("operator", meta.get("operator", ">=")))
        threshold_display = float(item.get("threshold", meta.get("threshold", 0)) or 0)
        threshold_unit = self._normalize_threshold_unit(metric, item.get("threshold_unit") or meta.get("threshold_unit", ""))
        threshold = self._threshold_for_compare(metric, threshold_display, threshold_unit)
        value = 0.0

        if metric == "cpu_usage":
            value = float((monitor.get("summary") or {}).get("cpu_usage", 0) or 0)
        elif metric == "mem_usage":
            value = float((monitor.get("summary") or {}).get("mem_usage", 0) or 0)
        elif metric == "disk_usage":
            disk = self._select_item(monitor.get("disks", []), "path", item.get("target_key")) or monitor.get("selected_disk", {})
            if not disk:
                return self._metric_result(metric, value, False, "Disk data is not available", operator, threshold, threshold_display, threshold_unit)
            value = float(disk.get("usage", 0) or 0)
        elif metric in ("bandwidth_up", "bandwidth_down", "traffic_up", "traffic_down"):
            nic = self._select_item(monitor.get("nics", []), "name", item.get("target_key")) or monitor.get("selected_nic", {})
            if not nic:
                return self._metric_result(metric, value, False, "Network interface data is not available", operator, threshold, threshold_display, threshold_unit)
            key = {
                "bandwidth_up": "up_kbs",
                "bandwidth_down": "down_kbs",
                "traffic_up": "up_total",
                "traffic_down": "down_total",
            }[metric]
            value = float(nic.get(key, 0) or 0)
        elif metric == "offline":
            summary_status = int((monitor.get("summary") or {}).get("status", 1) or 0)
            value = 1.0 if int(node.get("status", 1) or 0) == 0 or summary_status == 0 else 0.0
            operator = "=="
            threshold_display = 1.0
            threshold_unit = ""
            threshold = 1.0
        elif metric == "expire":
            expire = monitor.get("expire") or {}
            if int(expire.get("expire_at", 0) or 0) <= 0 or expire.get("days_left") is None:
                return self._metric_result(metric, value, False, "Expiration time is not configured", operator, threshold, threshold_display, threshold_unit)
            value = float(expire.get("days_left", 0) or 0)
            operator = "<="
        else:
            return self._metric_result(metric, value, False, "Unsupported metric", operator, threshold, threshold_display, threshold_unit)

        ok = self._compare(value, operator, threshold)
        display_value = self._value_for_display(metric, value, threshold_unit)
        message = self._format_message(item, node, display_value, operator, threshold_display, threshold_unit)
        return self._metric_result(metric, value, ok, message, operator, threshold, threshold_display, threshold_unit)

    def _metric_result(
            self,
            metric: str,
            value: float,
            ok: bool,
            message: str,
            operator: str,
            threshold: float,
            threshold_display: float,
            threshold_unit: str,
    ) -> Dict[str, Any]:
        return {
            "value": value,
            "display_value": self._value_for_display(metric, value, threshold_unit),
            "ok": ok,
            "message": message,
            "operator": operator,
            "threshold": threshold,
            "threshold_display": threshold_display,
            "threshold_unit": threshold_unit,
        }

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
    def _threshold_for_compare(metric: str, threshold: float, unit: str) -> float:
        if metric in ("bandwidth_up", "bandwidth_down"):
            return threshold * 1024 if unit == "MB/s" else threshold
        if metric in ("traffic_up", "traffic_down"):
            if unit == "GB":
                return threshold * 1024 ** 3
            if unit == "MB":
                return threshold * 1024 ** 2
            return threshold
        return threshold

    @staticmethod
    def _value_for_display(metric: str, value: float, unit: str) -> float:
        if metric in ("bandwidth_up", "bandwidth_down"):
            return value / 1024 if unit == "MB/s" else value
        if metric in ("traffic_up", "traffic_down"):
            if unit == "GB":
                return value / 1024 ** 3
            if unit == "MB":
                return value / 1024 ** 2
            return value
        return value

    @staticmethod
    def _select_item(items: List[Dict[str, Any]], key: str, target: Any) -> Dict[str, Any]:
        target = str(target or "")
        if not target:
            return {}
        for item in items if isinstance(items, list) else []:
            if isinstance(item, dict) and str(item.get(key, "")) == target:
                return item
        return {}

    @staticmethod
    def _compare(value: float, operator: str, threshold: float) -> bool:
        if operator == ">":
            return value > threshold
        if operator == ">=":
            return value >= threshold
        if operator == "<":
            return value < threshold
        if operator == "<=":
            return value <= threshold
        if operator == "==":
            return value == threshold
        if operator == "!=":
            return value != threshold
        return False

    @staticmethod
    def _send_interval_blocked(setting: Dict[str, Any], last_sent_at: int, now: int) -> bool:
        if int(setting.get("send_interval_enabled", 0) or 0) != 1:
            return False
        if not last_sent_at:
            return False
        interval = max(int(setting.get("send_interval", 1800) or 1800), 60)
        return now < last_sent_at + interval

    @staticmethod
    def _in_time_range(setting: Dict[str, Any]) -> bool:
        if int(setting.get("time_range_enabled", 0) or 0) != 1:
            return True
        start = max(0, min(int(setting.get("time_range_start", 0) or 0), 86400))
        end = max(0, min(int(setting.get("time_range_end", 86400) or 86400), 86400))
        if start == end:
            return True
        now = datetime.datetime.now()
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        if start < end:
            return start <= seconds <= end
        return seconds >= start or seconds <= end

    @staticmethod
    def _format_message(item: Dict[str, Any], node: Dict[str, Any], value: float, operator: str, threshold: float, unit: str) -> str:
        node_name = NodeAlertEngine._node_name(node, marked=True)
        metric = item.get("metric", "")
        if metric == "offline":
            duration = max(int(item.get("duration_minutes", 0) or 0), 0)
            duration_text = ", notify after {} minute(s)".format(duration) if duration else ""
            return "Node offline alert on {}: node is offline{}".format(node_name, duration_text)
        label = METRIC_LABELS.get(metric, metric)
        target = " [{}]".format(item.get("target_key")) if item.get("target_key") else ""
        unit_text = " {}".format(unit) if unit else ""
        return "{}{} alert on {}: current value {}{} {} threshold {}{}".format(
            label, target, node_name, round(value, 2), unit_text, operator, round(threshold, 2), unit_text
        )

    @staticmethod
    def _format_normal_message(
            item: Dict[str, Any],
            node: Dict[str, Any],
            value: float,
            operator: str,
            threshold: float,
            unit: str,
            fallback: str,
    ) -> str:
        if fallback in ("Disk data is not available", "Network interface data is not available",
                        "Expiration time is not configured", "Unsupported metric"):
            return fallback
        node_name = NodeAlertEngine._node_name(node, marked=True)
        metric = item.get("metric", "")
        if metric == "offline":
            return "Node offline status normal on {}: node is online".format(node_name)
        label = METRIC_LABELS.get(metric, metric)
        target = " [{}]".format(item.get("target_key")) if item.get("target_key") else ""
        unit_text = " {}".format(unit) if unit else ""
        return "{}{} normal on {}: current value {}{} {} threshold {}{}".format(
            label, target, node_name, round(value, 2), unit_text, operator, round(threshold, 2), unit_text
        )

    def _send(
            self,
            item: Dict[str, Any],
            setting: Dict[str, Any],
            node: Dict[str, Any],
            value: float,
            unit: str,
            message: str,
            operator: str,
            threshold: float,
    ) -> Dict[str, Any]:
        sender_ids = setting.get("sender_ids", [])
        title = self._format_alert_title(item, node)
        now_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            from mod.base.push_mod.system import PushSystem
            push_system = PushSystem()
            panel_info = {
                "server_name": public.GetConfigValue("title") or "aaPanel",
            }
            try:
                panel_ip = str(public.get_server_ip() or "").strip()
                if panel_ip:
                    panel_info["ip"] = panel_ip
            except Exception:
                pass
            result = {}
            for sender_id in sender_ids:
                conf = push_system.sd_cfg.get_by_id(str(sender_id))
                if not conf:
                    result[str(sender_id)] = "Alarm channel does not exist"
                    continue
                if not conf.get("used", True):
                    result[str(sender_id)] = "Alarm channel is disabled"
                    continue
                sender_type = conf.get("sender_type")
                if sender_type in ("sms", "wx_account"):
                    result[str(sender_id)] = "Unsupported alarm channel"
                    continue
                try:
                    body = self._format_alert_body(
                        item, node, value, unit, message, operator, threshold,
                        now_text, panel_info, html_mode=(sender_type == "mail")
                    )
                    res = push_system.sender_cls(sender_type)(conf).send_msg(msg=body, title=title)
                    result[str(sender_id)] = res if isinstance(res, str) else 1
                except Exception as e:
                    result[str(sender_id)] = str(e)
            return result
        except Exception as e:
            return {"_error": str(e)}

    @staticmethod
    def _format_alert_title(item: Dict[str, Any], node: Dict[str, Any]) -> str:
        node_name = NodeAlertEngine._node_name(node, marked=True)
        label = METRIC_LABELS.get(item.get("metric", ""), item.get("metric", ""))
        return "Node Alert {} - {}".format(node_name, label)

    @staticmethod
    def _panel_source_rows(panel_info: Dict[str, Any]) -> List[Tuple[str, str]]:
        panel_info = panel_info if isinstance(panel_info, dict) else {}
        panel_name = str(panel_info.get("server_name") or public.GetConfigValue("title") or "aaPanel").strip()
        panel_ip = str(panel_info.get("ip") or "").strip()
        if panel_ip and panel_ip not in panel_name:
            panel_name = "{} ({})".format(panel_name, panel_ip)
        return [("Server", panel_name)]

    @staticmethod
    def _node_source_rows(node: Dict[str, Any]) -> List[Tuple[str, str]]:
        node_name = NodeAlertEngine._node_name(node, marked=True)
        rows = [("Alert node", str(node_name))]
        address = str(node.get("address") or "").strip()
        server_ip = str(node.get("server_ip") or "").strip()
        ssh_conf = node.get("ssh_conf") if isinstance(node.get("ssh_conf"), dict) else {}
        ssh_host = str(ssh_conf.get("host") or "").strip()
        if address:
            rows.append(("Node address", address))
        if server_ip and server_ip != address:
            rows.append(("Node IP", server_ip))
        if ssh_host and ssh_host not in (address, server_ip):
            rows.append(("SSH host", ssh_host))
        return rows

    def _format_alert_body(
            self,
            item: Dict[str, Any],
            node: Dict[str, Any],
            value: float,
            unit: str,
            message: str,
            operator: str,
            threshold: float,
            now_text: str,
            panel_info: Dict[str, Any] = None,
            html_mode: bool = False,
    ) -> str:
        metric = item.get("metric", "")
        label = METRIC_LABELS.get(metric, metric)
        node_name = self._node_name(node, marked=True)
        duration = max(int(item.get("duration_minutes", 0) or 0), 0)
        value_text = self._format_alert_value(metric, value, unit)
        threshold_text = self._format_threshold_text(metric, operator, threshold, unit)
        duration_text = "{} minute(s)".format(duration) if duration else "immediate"
        summary = self._format_alert_summary(metric, node_name, value_text, duration_text)
        source_rows = self._panel_source_rows(panel_info) + self._node_source_rows(node)
        detail_rows = [
            ("Metric", label),
            ("Current", value_text),
            ("Condition", threshold_text),
            ("Duration", duration_text),
            ("Time", now_text),
        ]

        if not html_mode:
            return "\n".join([
                "Node Alert",
                "",
                summary,
                "",
                *["{}: {}".format(key, val) for key, val in source_rows],
                "Metric: {}".format(label),
                "Current: {}".format(value_text),
                "Condition: {}".format(threshold_text),
                "Duration: {}".format(duration_text),
                "Time: {}".format(now_text),
                "",
                "Detail: {}".format(message),
            ])

        rows = source_rows + detail_rows
        row_html = "".join(
            "<tr><td style=\"padding:9px 0;color:#667085;border-bottom:1px solid #eef0f3;width:120px;\">{}</td>"
            "<td style=\"padding:9px 0;color:#111827;border-bottom:1px solid #eef0f3;font-weight:500;\">{}</td></tr>".format(
                html.escape(str(key)), html.escape(str(val))
            )
            for key, val in rows
        )
        return (
            "<div style=\"font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#111827;\">"
            "<div style=\"max-width:640px;border:1px solid #e6e8ec;border-radius:8px;background:#fff;overflow:hidden;\">"
            "<div style=\"padding:20px 22px 12px 22px;\">"
            "<div style=\"margin:0 0 8px 0;color:#667085;font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;\">Node monitoring</div>"
            "<div style=\"margin:0 0 10px 0;font-size:18px;font-weight:600;color:#111827;\">Alert detected "
            "<span style=\"display:inline-block;margin-left:8px;padding:2px 8px;border-radius:999px;background:#fef3f2;color:#b42318;font-size:12px;font-weight:600;vertical-align:middle;\">Alert</span>"
            "</div>"
            "<p style=\"margin:0;color:#344054;font-size:14px;\">{}</p>"
            "</div>"
            "<div style=\"padding:0 22px 20px 22px;background:#fff;\">"
            "<table style=\"border-collapse:collapse;width:100%;border-top:1px solid #eef0f3;\">{}</table>"
            "<p style=\"margin:14px 0 0 0;color:#98a2b3;font-size:12px;\">Generated by aaPanel node monitoring.</p>"
            "</div></div></div>"
        ).format(html.escape(summary), row_html)

    @staticmethod
    def _format_alert_summary(metric: str, node_name: str, value_text: str, duration_text: str) -> str:
        if metric == "offline":
            return "Node {} is offline. The condition has met the configured duration: {}.".format(node_name, duration_text)
        return "Node {} triggered an alert. Current value: {}.".format(node_name, value_text)

    @staticmethod
    def _format_alert_value(metric: str, value: float, unit: str) -> str:
        if metric == "offline":
            return "Offline" if float(value) == 1 else "Online"
        unit_text = " {}".format(unit) if unit else ""
        return "{}{}".format(round(value, 2), unit_text)

    @staticmethod
    def _format_threshold_text(metric: str, operator: str, threshold: float, unit: str) -> str:
        if metric == "offline":
            return "Node status is offline"
        unit_text = " {}".format(unit) if unit else ""
        return "{} {}{}".format(operator, round(threshold, 2), unit_text)

    def _save_history(
            self,
            item: Dict[str, Any],
            setting: Dict[str, Any],
            node: Dict[str, Any],
            target_key: str,
            value: float,
            operator: str,
            threshold: float,
            threshold_unit: str,
            action: str,
            message: str,
            send_result: Dict[str, Any],
    ):
        self.monitor_db.add_alert_history({
            "node_id": node.get("id", 0),
            "item_id": item.get("id", 0),
            "metric": item.get("metric", ""),
            "target_key": target_key,
            "trigger_value": value,
            "operator": operator,
            "threshold": threshold,
            "threshold_unit": threshold_unit,
            "action": action,
            "message": message,
            "sender_ids": setting.get("sender_ids", []),
            "send_result": send_result,
        })
