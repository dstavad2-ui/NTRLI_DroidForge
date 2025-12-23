from engine.ai.roles import ALL_ROLES

class AIDispatcher:
    def __init__(self, providers):
        self.providers = providers  # dict[name -> AIProvider]

    def assign_role(self, provider_name, role):
        if provider_name in self.providers and role in ALL_ROLES:
            self.providers[provider_name].roles.add(role)

    def providers_for_role(self, role):
        return [
            p for p in self.providers.values()
            if role in p.roles
        ]

    def call(self, role, prompt):
        # Stubbed on purpose: pluggable execution
        # Returns a structured placeholder result
        results = []
        for p in self.providers_for_role(role):
            p.metrics["calls"] += 1
            results.append({
                "provider": p.name,
                "role": role,
                "output": f"[STUB] {role} response from {p.name}"
            })
        return results
