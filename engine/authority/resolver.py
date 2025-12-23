def resolve_authority(context):
    return {
        "analysis": True,
        "execution": "EXECUTION" in context.env.get("NTRLI_AUTH", ""),
        "mutation": "MUTATION" in context.env.get("NTRLI_AUTH", ""),
        "state": "STATEFUL" in context.env.get("NTRLI_MODE", "")
    }
