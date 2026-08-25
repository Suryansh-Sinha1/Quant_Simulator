import random

def make_scenario(pool, seed, max_value=6):
    rng = random.Random(seed)
    a_values = {item: rng.randint(0, max_value) for item in pool}
    b_values = {item: rng.randint(0, max_value) for item in pool}
    return a_values, b_values

def is_usable(pool, a_values, b_values):
    if sum(a_values[i] * pool[i] for i in pool) == 0:
        return False
    if sum(b_values[i] * pool[i] for i in pool) == 0:
        return False
    return True