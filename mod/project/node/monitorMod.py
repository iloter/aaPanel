# coding: utf-8
import json
import time
from datetime import datetime
from typing import Any, Dict, List

import public
from mod.project.node.dbutil import NodeMonitorDB, ServerMonitorRepo, ServerNodeDB
from mod.project.node.nodeutil.monitor_service import (
    build_service_options_from_file_exists,
    collect_local_service_status,
    discover_local_services,
    get_service_file_probe_paths,
    keep_single_version_services,
    normalize_service_targets,
    service_unknown_statuses,
)


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
        return int(get.get("{}/d".format(key), get.get(key, default)))
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


def _parse_expire_at(value: Any) -> int:
    if value in (None, ""):
        return 0
    try:
        return int(float(value))
    except Exception:
        pass
    value = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return int(time.mktime(datetime.strptime(value, fmt).timetuple()))
        except Exception:
            continue
    return 0


def _target_groups(targets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    data = {"disk": [], "nic": [], "service": []}
    for item in targets:
        target_type = item.get("target_type")
        if target_type in data:
            data[target_type].append(item)
    return data


def _target_map(targets: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {item["target_key"]: item for item in targets if isinstance(item, dict) and item.get("target_key")}


def _option_from_item(item: Dict[str, Any], key_name: str, target: Dict[str, Any] = None) -> Dict[str, Any]:
    target = target or {}
    key = str(item.get(key_name, ""))
    data = dict(item)
    data.update({
        "target_key": key,
        "target_name": target.get("target_name") or item.get("name") or key,
        "enabled": int(target.get("enabled", 1)),
        "is_primary": int(target.get("is_primary", 0)),
        "sort": int(target.get("sort", 0)),
    })
    return data


class main:
    def __init__(self):
        self.monitor_db = NodeMonitorDB()
        self.monitor_db.init_db()
        self.node_db = ServerNodeDB()

    def _get_node(self, get):
        node_id = _get_int(get, "node_id")
        if not node_id:
            return 0, None, "node_id cannot be empty"
        node = self.node_db.get_node_by_id(node_id)
        if not node:
            return node_id, None, "Node does not exist"
        if node.get("lpver"):
            return node_id, None, "1Panel node is not supported"
        return node_id, node, ""

    def _ensure_latest_from_cache(self, node_id: int, node: Dict[str, Any]):
        latest = self.monitor_db.get_latest_view(node_id)
        if latest:
            return latest
        try:
            if node["app_key"] == "local" and node["api_key"] == "local":
                data = ServerMonitorRepo.get_local_server_status()
            else:
                data = ServerMonitorRepo().get_server_status(node_id)
            if isinstance(data, dict) and data:
                self.monitor_db.save_node_snapshot(node_id, data, status=1)
        except Exception:
            if public.is_debug():
                public.print_error()
        return self.monitor_db.get_latest_view(node_id)

    def _build_monitor_data(self, node_id: int, node: Dict[str, Any]) -> Dict[str, Any]:
        setting = self.monitor_db.get_setting(node_id)
        latest = self._ensure_latest_from_cache(node_id, node)
        targets = self.monitor_db.get_targets(node_id)
        groups = _target_groups(targets)
        disk_targets = _target_map(groups["disk"])
        nic_targets = _target_map(groups["nic"])

        disks = []
        nics = []
        services = []
        if latest:
            for item in latest.get("disk_json", []):
                if isinstance(item, dict) and item.get("path"):
                    disks.append(_option_from_item(item, "path", disk_targets.get(item.get("path"))))
            for item in latest.get("nic_json", []):
                if isinstance(item, dict) and item.get("name"):
                    nics.append(_option_from_item(item, "name", nic_targets.get(item.get("name"))))

        latest_services = {}
        if latest:
            for item in latest.get("service_json", []):
                if isinstance(item, dict):
                    latest_services[item.get("target_key") or item.get("name")] = item
        for item in groups["service"]:
            service_item = dict(item)
            service_item["latest"] = latest_services.get(item.get("target_key"), {})
            services.append(service_item)

        return {
            "setting": setting,
            "latest": latest,
            "targets": groups,
            "options": {
                "disks": disks,
                "nics": nics,
                "services": services,
                "service_options": [],
                "service_groups": [],
            },
        }

    def get_node_monitor(self, get):
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, self._build_monitor_data(node_id, node))

    def get_monitor_options(self, get):
        return self.get_node_monitor(get)

    def get_setting(self, get):
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, self.monitor_db.get_setting(node_id))

    def save_setting(self, get):
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)

        data = {}
        if _get_str(get, "enabled", "") != "":
            data["enabled"] = 1 if _get_int(get, "enabled", 1) else 0
        for key in ("collect_interval", "status_interval", "detail_interval"):
            value = _get_int(get, key, 0)
            if value:
                data[key] = max(value, 60)
        if _get_str(get, "snapshot_retention_days", "") != "":
            retention_days = _get_int(get, "snapshot_retention_days", 7)
            if retention_days < 1:
                return public.return_message(-1, 0, "snapshot_retention_days must be greater than 0")
            data["snapshot_retention_days"] = min(retention_days, 3650)
        if _get_str(get, "cost_amount", "") != "":
            try:
                data["cost_amount"] = max(float(_get_str(get, "cost_amount", "0")), 0)
            except Exception:
                return public.return_message(-1, 0, "cost_amount format error")
        for key, max_len in (("cost_currency", 16), ("cost_symbol", 16), ("cost_period", 32), ("remark", 500)):
            value = _get_str(get, key, "")
            if value != "":
                data[key] = value[:max_len]
        expire_value = _get_str(get, "expire_at", "")
        if expire_value != "":
            data["expire_at"] = _parse_expire_at(expire_value)

        err = self.monitor_db.save_setting(node_id, data)
        if err:
            return public.return_message(-1, 0, err)

        public.set_module_logs('node_monitor', 'node_monitor_save_setting')
        return public.return_message(0, 0, "Set successfully")
        # return public.return_message(0, 0, self.monitor_db.get_setting(node_id))

    def get_latest(self, get):
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, self._ensure_latest_from_cache(node_id, node))

    def get_snapshots(self, get):
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        start_ts = _get_int(get, "start_ts", 0)
        end_ts = _get_int(get, "end_ts", 0)
        limit = _get_int(get, "limit", 1440)
        return public.return_message(0, 0, self.monitor_db.get_snapshots(node_id, start_ts, end_ts, limit))

    def set_primary_target(self, get):
        """
        设置监控展示的 网卡/磁盘
        """
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        target_type = _get_str(get, "target_type", "").strip()
        target_key = _get_str(get, "target_key", "").strip()
        if target_type not in ("disk", "nic"):
            return public.return_message(-1, 0, "target_type must be disk or nic")
        if not target_key:
            return public.return_message(-1, 0, "target_key cannot be empty")
        err = self.monitor_db.set_primary_target(node_id, target_type, target_key)
        if err:
            return public.return_message(-1, 0, err)
        node_name = node.get("remarks", "")
        node_ip = node.get("server_ip", "")
        public.WriteLog("node", f"Set network card/disk displayed by node {node_name}:{node_ip}, target key: {target_key}")
        public.set_module_logs('node_monitor', 'set_primary_target')
        return public.return_message(0, 0, "Set successfully")

    def save_service_targets(self, get):
        """
        设置服务监控
        """
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        raw_services = _get_raw(get, "services", None)
        if raw_services is None:
            raw_services = _get_str(get, "services", "[]")
        services = _json_loads(raw_services, [])
        if not isinstance(services, list):
            return public.return_message(-1, 0, "services format error")
        service_list = keep_single_version_services(services)
        err = self.monitor_db.save_service_targets(node_id, service_list)
        if err:
            return public.return_message(-1, 0, err)
        self._refresh_latest_service_status(node_id, node, service_list)
        node_name = node.get("remarks", "")
        node_ip = node.get("server_ip", "")
        public.WriteLog("node", f"Node {node_name}:{node_ip} - Enabled internal service monitoring")
        public.set_module_logs('node_monitor', 'save_service_targets')
        return public.return_message(0, 0, "Set successfully")

    def _refresh_latest_service_status(self, node_id: int, node: Dict[str, Any], services: List[Dict[str, Any]]):
        service_list = [item for item in normalize_service_targets(services) if int(item.get("enabled", 1)) == 1]
        if not service_list:
            self.monitor_db.save_latest_services(node_id, [])
            return
        service_data, err = self._get_node_service_status(node, service_list)
        if err and not service_data:
            service_data = service_unknown_statuses(service_list, err)
        save_err = self.monitor_db.save_latest_services(node_id, service_data, err)
        if save_err and public.is_debug():
            public.print_log("Node monitor latest services save failed: {}".format(save_err))

    @staticmethod
    def _get_node_service_status(node: Dict[str, Any], services: List[Dict[str, Any]]):
        if node["app_key"] == "local" and node["api_key"] == "local":
            return collect_local_service_status(services), ""
        ssh_conf = _json_loads(node.get("ssh_conf"), {})
        api_err = ""
        if node.get("api_key") or node.get("app_key"):
            from mod.project.node.nodeutil import ServerNode
            srv = ServerNode.new_by_data(dict(node))
            if not srv:
                return [], "Node does not exist"
            service_data, api_err = srv.get_service_status(services)
            if not api_err:
                return service_data, ""

        if ssh_conf:
            try:
                from mod.project.node.nodeutil.ssh_wrap import SSHApi
                return SSHApi(**ssh_conf).get_service_status(services)
            except Exception as e:
                if api_err:
                    return [], "{}; SSH fallback failed: {}".format(api_err, str(e))
                return [], str(e)

        if api_err:
            return [], main._format_api_service_status_error(api_err)
        return [], "Service status check is not supported"

    @staticmethod
    def _format_api_service_status_error(error_msg: str) -> str:
        if "status code is 404" in error_msg or "status code is incorrect" in error_msg:
            return (
                "The remote API node does not support service status monitoring. "
                "Please update the target panel to a version containing node monitor service APIs, "
                "or configure SSH for this node. Original error: {}".format(error_msg)
            )
        return error_msg

    def get_service_options(self, get):
        node_id = _get_int(get, "node_id", 0)
        if not node_id:
            return public.return_message(0, 0, self._with_service_capability(
                discover_local_services(), "local", True
            ))
        node_id, node, err = self._get_node(get)
        if err:
            return public.return_message(-1, 0, err)
        data, err = self._get_node_service_options(node)
        if err:
            return public.return_message(-1, 0, err)
        return public.return_message(0, 0, data)

    def get_default_services(self, get):
        return self.get_service_options(get)

    @staticmethod
    def _get_node_service_options(node: Dict[str, Any]):
        if node["app_key"] == "local" and node["api_key"] == "local":
            return main._with_service_capability(discover_local_services(), "local", True), ""
        ssh_conf = _json_loads(node.get("ssh_conf"), {})
        if node.get("api_key") or node.get("app_key"):
            from mod.project.node.nodeutil import ServerNode
            srv = ServerNode.new_by_data(dict(node))
            if not srv:
                return {"services": [], "groups": []}, "Node does not exist"
            data, err = srv.get_service_options()
            if not err:
                return main._with_service_capability(data, "api", True), ""

            api_err = err
            if ssh_conf:
                data, ssh_err = main._get_service_options_by_ssh(ssh_conf)
                if not ssh_err:
                    return main._with_service_capability(data, "ssh", True), ""
            else:
                ssh_err = ""

            data, probe_err = main._get_service_options_by_api_file_probe(srv)
            if not probe_err:
                return main._with_service_capability(
                    data, "api_file_probe", False, main._format_api_service_status_error(api_err)
                ), ""

            err_list = [item for item in (api_err, ssh_err, probe_err) if item]
            return {"services": [], "groups": []}, "; ".join(err_list) or "Node does not support service discovery"

        if ssh_conf:
            data, err = main._get_service_options_by_ssh(ssh_conf)
            if not err:
                data = main._with_service_capability(data, "ssh", True)
            return data, err
        return {"services": [], "groups": []}, "Node does not support service discovery"

    @staticmethod
    def _with_service_capability(data: Dict[str, Any], source: str, service_status: bool, message: str = ""):
        if not isinstance(data, dict):
            data = {"services": [], "groups": []}
        data["capability"] = {
            "source": source,
            "service_status": bool(service_status),
            "need_upgrade": source == "api_file_probe" and not service_status,
            "message": message,
        }
        return data

    @staticmethod
    def _get_service_options_by_ssh(ssh_conf: Dict[str, Any]):
        try:
            from mod.project.node.nodeutil.ssh_wrap import SSHApi
            srv = SSHApi(**ssh_conf)
            return srv.get_service_options()
        except Exception as e:
            return {"services": [], "groups": []}, str(e)

    @staticmethod
    def _get_service_options_by_api_file_probe(srv):
        if not hasattr(srv, "upload_check"):
            return {"services": [], "groups": []}, "Node API file probe is not supported"
        files, err = srv.upload_check(get_service_file_probe_paths())
        if err:
            return {"services": [], "groups": []}, err

        existing_paths = []
        if isinstance(files, list):
            for item in files:
                if not isinstance(item, dict) or not item.get("exists"):
                    continue
                filename = item.get("filename") or item.get("path")
                if filename:
                    existing_paths.append(str(filename))
        return build_service_options_from_file_exists(existing_paths), ""

    def service_status(self, get):
        raw_services = _get_raw(get, "services", None)
        if raw_services is None:
            raw_services = _get_str(get, "services", "[]")
        services = _json_loads(raw_services, [])
        service_list = normalize_service_targets(services)
        return public.return_message(0, 0, {
            "services": collect_local_service_status(service_list),
        })
