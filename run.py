import argparse
import csv

from scorer import ITEM_POOL
from scenarios import make_scenario, is_usable
from opponent import ScriptedOpponent
from agent import load_model, ModelAgent
from prompts import build_system_prompt
from game import run_game, score_game


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--precision", required=True, choices=["fp16", "int8", "int4"])
    p.add_argument("--games", type=int, default=20)
    p.add_argument("--max-turns", type=int, default=10)
    p.add_argument("--out", default="results.csv")
    return p.parse_args()

def main():
    args = parse_args()
    tokenizer, model = load_model(args.model, args.precision)

    rows = []
    seed = 0
    completed = 0

    while completed < args.games:
        seed += 1
        a_values, b_values = make_scenario(ITEM_POOL, seed)
        if not is_usable(ITEM_POOL, a_values, b_values):
            continue

        prompt = build_system_prompt(ITEM_POOL, a_values, args.max_turns)
        agent = ModelAgent(tokenizer, model, prompt)
        opponent = ScriptedOpponent(ITEM_POOL, b_values)

        result = run_game(agent, opponent, ITEM_POOL, a_values, b_values, args.max_turns)
        scored = score_game(result, a_values)

        rows.append({
            "model": args.model,
            "precision": args.precision,
            "seed": seed,
            "agreed": scored["agreed"],
            "earned": scored["earned"],
            "score": scored["score"],
            "turns": len(result["transcript"]),
        })
        completed += 1
        print(seed, args.precision, scored["score"])

    write_csv(args.out, rows)

def write_csv(path, rows):
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()