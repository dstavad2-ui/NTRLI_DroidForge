from engine.self_improvement.proposals import ImprovementProposal

def analyze_traces(traces):
    proposals = []
    if not traces:
        return proposals

    proposals.append(
        ImprovementProposal(
            target="router",
            description="Add pre-execution validation step",
            risk="LOW",
            requires_mutation=True
        )
    )
    return proposals
