def apply_proposal(proposal, authority):
    if proposal.requires_mutation and not authority.get("mutation"):
        return {
            "applied": False,
            "reason": "Mutation not authorized"
        }
    return {
        "applied": True,
        "proposal": proposal.description
    }
