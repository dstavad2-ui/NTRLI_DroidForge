from engine.ai.registry import discover_providers
from engine.ai.dispatcher import AIDispatcher
from engine.ai import roles

class NTRLI_AI:
    def __init__(self, env):
        self.providers = discover_providers(env)
        self.dispatcher = AIDispatcher(self.providers)
        self._default_role_assignment()

    def _default_role_assignment(self):
        # Conservative defaults; can be improved later
        for name in self.providers:
            self.dispatcher.assign_role(name, roles.ANALYST)
            self.dispatcher.assign_role(name, roles.VALIDATOR)

    def plan(self, intent, context):
        # Meta-reasoning stub
        analysis = self.dispatcher.call(roles.ANALYST, f"Analyze intent: {intent}")
        validation = self.dispatcher.call(roles.VALIDATOR, f"Validate plan for: {intent}")
        return {
            "intent": intent,
            "analysis": analysis,
            "validation": validation
        }

    def self_analyze(self, traces):
        meta = self.dispatcher.call(roles.META, "Self-analyze recent traces")
        return {
            "type": "SELF_ANALYSIS",
            "meta": meta
        }
