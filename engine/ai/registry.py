import os

class AIProvider:
    def __init__(self, name, key):
        self.name = name
        self.key = key
        self.roles = set()
        self.metrics = {
            "calls": 0,
            "failures": 0,
            "latency_ms": []
        }

def discover_providers(env=None):
    env = env or os.environ
    providers = {}
    for k, v in env.items():
        if k.startswith("AI_") and v:
            providers[k] = AIProvider(name=k, key=v)
    return providers
