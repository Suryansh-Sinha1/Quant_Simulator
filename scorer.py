from itertools import product

ITEM_POOL = {"book": 3, "hat": 2, "ball": 1}


def score_allocation(allocation, values):
    total = 0
    for item, count in allocation.items():
        total += count * values[item]
    return total


def all_splits(pool):
    items = list(pool.keys())
    ranges = [range(pool[item] + 1) for item in items]

    splits = []
    for combo in product(*ranges):
        a_gets = dict(zip(items, combo))
        b_gets = {item: pool[item] - a_gets[item] for item in items}
        splits.append((a_gets, b_gets))
    return splits


def find_oracle(pool, a_values, b_values):
    best = None
    for a_gets, b_gets in all_splits(pool):
        a_score = score_allocation(a_gets, a_values)
        b_score = score_allocation(b_gets, b_values)
        joint = a_score + b_score

        if best is None or joint > best["joint"]:
            best = {"a_gets": a_gets, "a_score": a_score,
                    "b_score": b_score, "joint": joint}
    return best


def a_ceiling(pool, a_values):
    return score_allocation(pool, a_values)


def negotiation_score(a_final, pool, a_values, floor=0):
    earned = score_allocation(a_final, a_values)
    ceiling = a_ceiling(pool, a_values)

    if ceiling == floor:
        return None
    return (earned - floor) / (ceiling - floor)


def pareto_efficiency(a_final, pool, a_values, b_values, oracle):
    b_final = {item: pool[item] - a_final[item] for item in pool}
    joint = score_allocation(a_final, a_values) + score_allocation(b_final, b_values)

    if oracle["joint"] == 0:
        return None
    return joint / oracle["joint"]