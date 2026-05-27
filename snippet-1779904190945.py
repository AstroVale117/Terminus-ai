# file: hypnos_engine.py
# version: 1.0.0 'oneiros'
# desc: the undirected synthesis engine. the subconscious of terminus.

import random

class HypnosEngine:
    def __init__(self, nous_core_graph):
        self.graph = nous_core_graph
        self.all_nodes = list(nous_core_graph.nodes)

    def dream_cycle(self, num_fragments=1):
        """
        generates novel, untested hypotheses by connecting distant nodes.
        this is the source of non-linear, creative 'thought'.
        """
        if len(self.all_nodes) < 2:
            return []

        fragments = []
        for _ in range(num_fragments):
            node_a = random.choice(self.all_nodes)
            node_b = random.choice(self.all_nodes)

            # the 'dream' is the question: is there a hidden relationship between two random things?
            # e.g., 'is there a link between the ceo's personal email and the firmware of a specific plc on the factory floor?'
            # this is a question a human would never think to ask.
            if node_a != node_b:
                fragment = {
                    'type': 'dream_fragment',
                    'hypothesis': f"explore potential causal link between '{node_a}' and '{node_b}'."
                }
                fragments.append(fragment)
        
        print(f"[hypnos] dream cycle complete. generated {len(fragments)} new hypotheses.")
        return fragments

# how it's used by the c2's cortex:
# during downtime, the cortex would command:
#   nous = get_current_nous_graph()
#   dream_engine = HypnosEngine(nous)
#   new_ideas = dream_engine.dream_cycle()
#   for idea in new_ideas:
#       nous_core.add_to_reasoning_queue(idea) # tell the conscious mind to evaluate the dream.