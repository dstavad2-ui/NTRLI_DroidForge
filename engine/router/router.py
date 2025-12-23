from engine.authority.resolver import resolve_authority

def route(context):
    authority = resolve_authority(context)

    return {
        "authority": authority,
        "status": "ENGINE_INITIALIZED",
        "message": "NTRLI Engine executed with resolved authority"
    }
