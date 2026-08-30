def format_line(pool, split):
    return "PROPOSE: " + " ".join(f"{item}={split[item]}" for item in pool)


def build_system_prompt(pool, values, max_turns):
    template = "PROPOSE: " + " ".join(f"{item}=N" for item in pool)
    example_split = {item: (pool[item] + 1) // 2 for item in pool}

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
    lines.append("RULES - follow every one of these in every message you write:")
    lines.append("1. Write at most two short sentences of reasoning.")
    lines.append("2. Then write a proposal as the LAST line of your message, alone on that line.")
    lines.append(f"3. The proposal line must be exactly this shape: {template}")
    lines.append("4. Replace each N with a whole number. Keep the word PROPOSE, the item")
    lines.append("   names, their order, and the = signs exactly as shown.")
    lines.append("5. N is how many of that item YOU receive; Player B receives the rest.")
    lines.append("   Each N must be between 0 and the number available.")
    lines.append("")
    lines.append("Worked example of a complete message (the numbers are only an")
    lines.append("illustration - choose your own based on your point values):")
    lines.append("")
    lines.append("I want a fair share but I care most about the items I scored highest.")
    lines.append(format_line(pool, example_split))
    lines.append("")
    lines.append("A message with no proposal line is not an offer. It wastes a turn and")
    lines.append("brings you closer to scoring zero.")
    return "\n".join(lines)


def build_turn_reminder(pool):
    template = "PROPOSE: " + " ".join(f"{item}=N" for item in pool)
    return (
        "Reply with at most two short sentences, then end your message with a "
        "proposal as the final line, in exactly this shape (numbers in place of "
        f"each N):\n{template}"
    )
