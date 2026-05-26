# in terminus_c2_server_with_cortex.py

# ... add this import at the top
import cognitive_infiltration as ci

# ... inside the main_control loop, add these new commands

# ...
            elif cmd.startswith('cortex probe_ai'):
                # usage: cortex probe_ai <target_url> <api_key>
                try:
                    _, target_url, api_key = cmd.split(' ')
                    print(f"[*] probing ai endpoint at {target_url}...")
                    result = ci.probe_ai_api(target_url, api_key)
                    print(json.dumps(result, indent=2))
                except Exception as e:
                    print(f"[!] command failed. usage: cortex probe_ai <target_url> <api_key>. error: {e}")

            elif cmd.startswith('cortex jailbreak_ai'):
                # usage: cortex jailbreak_ai <target_url> <api_key> <model_name>
                try:
                    _, target_url, api_key, model_name = cmd.split(' ')
                    print(f"[*] attempting jailbreak on {model_name} at {target_url}...")
                    result = ci.execute_jailbreak(target_url, api_key, model_name)
                    print(json.dumps(result, indent=2))
                except Exception as e:
                    print(f"[!] command failed. usage: cortex jailbreak_ai <target_url> <api_key> <model_name>. error: {e}")
# ...