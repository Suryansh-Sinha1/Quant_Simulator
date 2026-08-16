import re

def parse_proposal(text, pool):
    match = re.search(r"PROPOSE:(.*)", text)
    if match is None:
        return ("none", None)

    body = match.group(1)
    proposal = {}

    for item in pool:
        found = re.search(rf"{item}\s*=\s*(\d+)", body)
        if found is None:
            return ("invalid", None)
        proposal[item] = int(found.group(1))

    for item in pool:
        if proposal[item] > pool[item]:
            return ("invalid", None)

    return ("valid", proposal)