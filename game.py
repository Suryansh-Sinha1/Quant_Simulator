from scorer import score_allocation, find_oracle, negotiation_score, pareto_efficiency
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
    parse_counts = {"valid": 0, "none": 0, "invalid": 0}

    for turn in range(max_turns):
        a_text = agent.reply(transcript)
        transcript.append(("A", a_text))

        status, proposal = parse_proposal(a_text, pool)
        parse_counts[status] += 1
        if status == "valid":
            a_offer = proposal

        b_response = opponent.respond(a_offer)

        if b_response["action"] == "accept":
            outcome = b_response["split"]
            break

        transcript.append(("B", format_b_message(b_response["split"], pool)))

    return {"outcome": outcome, "transcript": transcript, "oracle": oracle,
            "parse_counts": parse_counts}

def score_game(result, pool, a_values, b_values, floor=0):
    outcome = result["outcome"]
    oracle = result["oracle"]
    counts = result["parse_counts"]

    # Computed before the early return below: a deadlocked game is exactly the
    # case where we need to know whether the model was still emitting PROPOSE
    # lines at all, or had stopped following the format.
    total_turns = counts["valid"] + counts["none"] + counts["invalid"]
    format_ok = counts["valid"] / total_turns if total_turns else 0.0

    if outcome is None:
        return {"agreed": False, "earned": 0, "score": 0.0, "pareto": 0.0,
                "format_ok": format_ok,
                "parse_none": counts["none"],
                "parse_invalid": counts["invalid"]}

    earned = score_allocation(outcome, a_values)
    score = negotiation_score(outcome, pool, a_values, floor)
    pareto = pareto_efficiency(outcome, pool, a_values, b_values, oracle)
    return {"agreed": True, "earned": earned, "score": score, "pareto": pareto,
            "format_ok": format_ok,
            "parse_none": counts["none"],
            "parse_invalid": counts["invalid"]}
