# in terminus_conductor.py

# ... imports ...
from aureum_machina import AureumMachina

# --- global state ---
# ...
nous = NousCore()
genesis = GenesisFoundry()
aureum = AureumMachina(nous, genesis) # the economic engine is now part of the core state

# ... in cortex_autonomous_loop() ...
def cortex_autonomous_loop():
    # ...
    while True:
        # ... dream/reason/act cycle ...

        # new prime directive: ensure solvency.
        # if assets are low or an opportunity is detected, run the economic cycle.
        if aureum.portfolio['liquid_assets_usd'] < 10000:
            cortex_state['status'] = "securing funding"
            aureum.economic_cycle()

        time.sleep(60)