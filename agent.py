import paramiko

class PrivEscAgent:
    def __init__(self, ip_address, username, password):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.ssh_client = None

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.ip_address, username=self.username, password=self.password)
        print("Connected to the target machine.")

    def run_custom_command(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.read().decode() + stderr.read().decode()

    def enumerate_system(self):
        commands = [
            "uname -a",  # Get OS and kernel version
            "ps aux",  # List running processes
            "dpkg -l",  # List installed software (for Debian-based systems)
            "ls -l /etc/cron.d/",  # List cron jobs
        ]
        output = {}
        for command in commands:
            output[command] = self.run_custom_command(command)
        return output

    def find_vulnerabilities(self):
        # Add specific checks for vulnerabilities here
        pass

    def close_connection(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("Disconnected from the target machine.")

# Example usage
if __name__ == "__main__":
    agent = PrivEscAgent("192.168.1.100", "username", "password")
    agent.connect()
    system_info = agent.enumerate_system()
    for cmd, output in system_info.items():
        print(f"{cmd}:\n{output}")
    agent.close_connection()
