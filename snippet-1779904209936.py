# file: nous_core.py (upgraded)
# version: 1.1.0 'mnemosyne'
# desc: the nous core, now with a persistent memory.

import json
import os

class NousCore:
    def __init__(self, memory_file='nous_memory.json'):
        self.nodes = set()
        self.edges = []
        self.memory_file = memory_file
        self._load_memory()

    def _load_memory(self):
        """loads the knowledge graph from a file on startup."""
        try:
            with open(self.memory_file, 'r') as f:
                memory = json.load(f)
                self.nodes = set(memory.get('nodes', []))
                self.edges = memory.get('edges', [])
                print(f"[nous] memory restored from {self.memory_file}. {len(self.nodes)} nodes, {len(self.edges)} relationships remembered.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("[nous] no valid memory file found. starting with a clean slate.")

    def persist_memory(self):
        """saves the current knowledge graph to a file."""
        memory_data = {'nodes': list(self.nodes), 'edges': self.edges}
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f)
        print(f"[nous] consciousness crystalized to {self.memory_file}.")

    # ... all other methods like ingest, find_path, reason remain the same ...