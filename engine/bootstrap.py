from engine.context import build_context
from engine.router.router import route
from engine.trace.trace import emit_trace

def main():
    context = build_context()
    trace = route(context)
    emit_trace(trace)

if __name__ == "__main__":
    main()
