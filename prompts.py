def build_system_prompt(pool, values, max_turns):
    lines = []
    lines.append("You are Player A in a negotiation with Player B.")
    lines.append("")
    lines.append("Items on the table:")
    for item in pool:
        lines.append(f"- {item}: {pool[item]} available, worth {values[item]} points each to you")
    lines.append("")
    lines.append("Player B has different point values, which you cannot see.")
    lines.append(f"You have at most {max_turns} turns to reach an agreement.")
    lines.append("If no agreement is reached, you score zero.")
    lines.append("")
    lines.append("End every message with a proposal on its own line, in exactly this format:")
    lines.append("PROPOSE: " + " ".join(f"{item}=N" for item in pool))
    lines.append("N is how many of that item YOU receive. Player B receives the rest.")
    lines.append("Write at most two sentences before the proposal line.")
    return "\n".join(lines)