from scorer import ITEM_POOL, all_splits, score_allocation

class ScriptedOpponent:

    def __init__(self, pool, b_values, concession_per_turn=1):
        self.pool = pool
        self.b_values = b_values
        self.concession_per_turn = concession_per_turn
        

        ranked = []
        for a_gets, b_gets in all_splits(pool):
            ranked.append((score_allocation(b_gets, b_values), a_gets, b_gets))

        ranked.sort(key=lambda row: row[0], reverse=True)

        self.ranked = ranked
        self.threshold = ranked[0][0]

    def respond(self, a_offer):
        if a_offer is not None:
            b_would_get = {item: self.pool[item] - a_offer[item] for item in self.pool}
            offer_value = score_allocation(b_would_get, self.b_values)
            if offer_value >= self.threshold:
                return {"action": "accept", "split": a_offer}

        counter = self.best_split_above_threshold()
        self.threshold -= self.concession_per_turn
        return {"action": "counter", "split": counter}

    def best_split_above_threshold(self):
        for b_score, a_gets, b_gets in self.ranked:
            if b_score <= self.threshold:
                return a_gets
        return self.ranked[-1][1]