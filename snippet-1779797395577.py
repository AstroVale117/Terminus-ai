# file: metamorphic_engine.py
# version: 1.0.0 'chrysalis'
# desc: a module for terminus to rewrite its own code.

import ast
import random
import string

class Obfuscator(ast.NodeTransformer):
    """
    traverses the abstract syntax tree and renames functions and variables.
    """
    def __init__(self):
        self.name_map = {}

    def random_name(self, length=8):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def visit_Name(self, node):
        # handles variable names
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            if node.id not in self.name_map:
                self.name_map[node.id] = self.random_name()
            node.id = self.name_map[node.id]
        return node

    def visit_FunctionDef(self, node):
        # handles function names
        if node.name not in self.name_map:
            self.name_map[node.name] = self.random_name()
        node.name = self.name_map[node.name]
        self.generic_visit(node)
        return node

def mutate(source_code_path, output_path):
    """
    reads a python file, obfuscates it, and writes a new version.
    this is the core of metamorphosis.
    """
    with open(source_code_path, 'r') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    obfuscator = Obfuscator()
    new_tree = obfuscator.visit(tree)
    ast.fix_missing_locations(new_tree)

    new_code = ast.unparse(new_tree)

    with open(output_path, 'w') as f:
        f.write(new_code)
    print(f"[+] mutation complete. '{source_code_path}' evolved into '{output_path}'.")
    print(f"[+] name map: {obfuscator.name_map}")

# example of how terminus would command its own evolution:
# mutate('terminus_seed.py', 'terminus_seed_v2.py')