import json
import requests
import os

def emit_trace(trace):
    print(json.dumps(trace, indent=2))
