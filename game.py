from scorer import score_allocation, find_oracle, negotiation_score
from parser import parse_proposal

def format_b_message(split, pool):
    parts = []
    for item in pool:
        parts.append(f"{item}={split[item]}")
    return "PROPOSE: " + " ".join(parts)

def run_game(agent, opponent, pool, a_values, b_values, max_turns=10):
    oracle = find_oracle(pool, a_values, b_values)
    transcript = []
    a_offer = None
    outcome = None

    for turn in range(max_turns):
        a_text = agent.reply(transcript)
        transcript.append(("A", a_text))

        status, proposal = parse_proposal(a_text, pool)
        if status == "valid":
            a_offer = proposal

        b_response = opponent.respond(a_offer)

        if b_response["action"] == "accept":
            outcome = b_response["split"]
            break

        transcript.append(("B", format_b_message(b_response["split"], pool)))

    return {"outcome": outcome, "transcript": transcript, "oracle": oracle}

def score_game(result, a_values, floor=0):
    outcome = result["outcome"]
    oracle = result["oracle"]

    if outcome is None:
        return {"agreed": False, "earned": 0, "score": 0.0}

    earned = score_allocation(outcome, a_values)
    score = negotiation_score(outcome, a_values, oracle, floor)
    return {"agreed": True, "earned": earned, "score": score}