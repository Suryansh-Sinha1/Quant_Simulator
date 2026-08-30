import re

PROPOSE_RE = re.compile(r"PROPOSE\s*:", re.IGNORECASE)


def parse_proposal(text, pool):
    matches = list(PROPOSE_RE.finditer(text))
    if not matches:
        return ("none", None)

    # Prefer the last proposal in the message: if the model echoes the format
    # line before writing its real offer, the real offer is the later one.
    for match in reversed(matches):
        body = text[match.end():]
        proposal = {}

        for item in pool:
            found = re.search(rf"\b{re.escape(item)}\s*=\s*(\d+)", body, re.IGNORECASE)
            if found is None:
                break
            count = int(found.group(1))
            if count > pool[item]:
                break
            proposal[item] = count
        else:
            return ("valid", proposal)

    return ("invalid", None)
