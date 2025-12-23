class ImprovementProposal:
    def __init__(self, target, description, risk, requires_mutation):
        self.target = target
        self.description = description
        self.risk = risk
        self.requires_mutation = requires_mutation
        self.id = None
