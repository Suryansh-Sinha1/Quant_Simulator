from scorer import score_allocation, find_oracle, negotiation_score
from parser import parse_proposal


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

        transcript.append(("B", b_response))

    return {"outcome": outcome, "transcript": transcript, "oracle": oracle}