import os
import shlex
import subprocess
import sys
from datetime import datetime
if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")

os.chdir("/www/server/panel")
import public

from mod.project.ssh.base import SSHbase


class JournalctlManage(SSHbase):
    def __init__(self):
        super(JournalctlManage, self).__init__()

    def use_journalctl_logs(self):
        try:
            if not self.journalctl_system():
                return False
            log_path = getattr(self, 'ssh_log_path', '')
            return log_path.startswith('/var/log/message') or not self.has_secure_log_files()
        except Exception:
            return False

    def get_secure_logs(self, login_type, pagesize=10, page=1, query=''):
        if self.use_journalctl_logs():
            return self.get_journalctl_login_logs(login_type, pagesize, page, query)
        return super(JournalctlManage, self).get_secure_logs(login_type, pagesize, page, query)

    def get_secure_log_count(self, login_type, query=''):
        if self.use_journalctl_logs():
            return self.get_journalctl_login_count(login_type, query)
        return super(JournalctlManage, self).get_secure_log_count(login_type, query)

    def get_journalctl_since_option(self):
        try:
            res, err = public.ExecShell("journalctl --disk-usage")
            total_bytes = public.parse_journal_disk_usage(res)
            if total_bytes > 5 * 1024 * 1024 * 1024:
                return " --since '30 days ago'"
        except Exception:
            pass
        return ""

    def get_journalctl_login_command(self, login_type):
        grep_pattern = shlex.quote("({})".format(login_type))
        return "LC_ALL=C journalctl -q -u ssh -u sshd{} --no-pager --output=short-iso --grep={}".format(
            self.get_journalctl_since_option(),
            grep_pattern
        )

    def get_journalctl_query_pipe(self, query):
        query = (query or '').strip()
        if not query:
            return ""
        return " | grep -aiF -- {}".format(shlex.quote(query))

    def exec_journalctl_count_page(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                executable="/bin/bash",
                timeout=30
            )
            count = int((result.stdout or "0").strip() or 0)
            datas = result.stderr.strip().split("\n") if result.stderr.strip() else []
        except subprocess.TimeoutExpired:
            public.print_log("SSH journalctl query timed out")
            count = 0
            datas = []
        except Exception:
            count = 0
            datas = []
        return count, datas

    def exec_journalctl_count(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                executable="/bin/bash",
                timeout=30
            )
            return int((result.stdout or "0").strip() or 0)
        except subprocess.TimeoutExpired:
            public.print_log("SSH journalctl count query timed out")
            return 0
        except Exception:
            return 0

    def get_journalctl_login_logs(self, login_type, pagesize=10, page=1, query=''):
        new_logins = []
        end = pagesize * page
        command = "{}{} | tee >(tail -n {} | head -n {} | tac >&2) | wc -l".format(
            self.get_journalctl_login_command(login_type),
            self.get_journalctl_query_pipe(query),
            end,
            pagesize
        )
        total, lines = self.exec_journalctl_count_page(command)
        year = datetime.now().year
        for line in lines:
            entry = self.parse_login_entry(line.split(), year)
            if entry:
                entry["log_file"] = "journalctl"
                new_logins.append(entry)
        return total, new_logins

    def get_journalctl_login_count(self, login_type, query=''):
        command = "{}{} | wc -l".format(
            self.get_journalctl_login_command(login_type),
            self.get_journalctl_query_pipe(query)
        )
        return self.exec_journalctl_count(command)

    def get_journalctl_logs(self, file_positions):
        '''
        获取 systemd journalctl 的 SSH 登录日志
        return  日志,游标位置
        '''
        new_logins = []
        current_positions = ""

        command_list = [
                "journalctl -u ssh --no-pager --show-cursor --grep='Accepted|Failed password for|Accepted publickey'",  # 全量获取
                "journalctl -u ssh --since '30 days ago' --no-pager --show-cursor --grep='Accepted|Failed password for|Accepted publickey'",  # 30天
                "journalctl -u ssh --no-pager --show-cursor --grep='Accepted|Failed password for|Accepted publickey' --cursor='{}'".format(file_positions)  # 从记录的游标开始读取
            ]

        if not file_positions:
            # 获取systemd日志所占用的空间
            res, err = public.ExecShell("journalctl --disk-usage")
            total_bytes = public.parse_journal_disk_usage(res)
            limit_bytes = 5 * 1024 * 1024 * 1024
            # 大于5G 取30天的数据量
            command = command_list[1] if total_bytes > limit_bytes else command_list[0]
            content = public.ExecShell(command)[0].strip()
        else:
            content = public.ExecShell(command_list[2])[0].strip()

        lines = content.split('\n')
        if lines:
             # 处理去除多余游标字符
            current_positions = lines[-1].replace("-- cursor: ", "")

        for line in lines[:-1]:
            if "No entries" in line:break

            if any(keyword in line for keyword in ["Accepted password", "Failed password", "Accepted publickey"]):
                parts = line.split()
                year = datetime.now().year
                entry = self.parse_login_entry(parts, year)
                if entry:
                    entry["log_file"] = "journalctl"
                    new_logins.append(entry)
        return new_logins, current_positions
