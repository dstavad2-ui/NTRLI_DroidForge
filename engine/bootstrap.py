import sys
import os

# Ensure repo root is on PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.context import build_context
from engine.router.router import route
from engine.trace.trace import emit_trace

def main():
    context = build_context()
    trace = route(context)
    emit_trace(trace)

if __name__ == "__main__":
    main()
