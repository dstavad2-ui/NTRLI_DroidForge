from engine.commands.schemas import COMMAND_SCHEMAS

def list_commands():
    return COMMAND_SCHEMAS

def describe_command(name):
    for category, commands in COMMAND_SCHEMAS.items():
        if name in commands:
            return {
                "category": category,
                "name": name
            }
    return None
