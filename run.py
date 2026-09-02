import argparse
import csv
import os

from scorer import ITEM_POOL
from scenarios import make_scenario, is_usable
from opponent import ScriptedOpponent
from agent import load_model, ModelAgent
from prompts import build_system_prompt, build_turn_reminder
from game import run_game, score_game


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--precision", required=True, choices=["fp16", "int8", "int4"])
    p.add_argument("--games", type=int, default=20)
    p.add_argument("--max-turns", type=int, default=10)
    p.add_argument("--out", default="results.csv")
    p.add_argument("--show-transcript", action="store_true")
    return p.parse_args()


CSV_FIELDS = ["model", "precision", "seed", "agreed", "earned",
              "score", "pareto", "turns",
              "format_ok", "parse_none", "parse_invalid"]


def check_out_file(path):
    """Fail before the model loads if `path` has an incompatible header.

    write_csv appends, so an older file written with a different set of
    columns would silently misalign every new row.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return

    with open(path, newline="") as f:
        header = next(csv.reader(f), None)

    if header != CSV_FIELDS:
        raise SystemExit(
            f"{path} has an incompatible header.\n"
            f"  found:    {header}\n"
            f"  expected: {CSV_FIELDS}\n"
            "Move or delete that file, or pass --out with a new filename."
        )


def write_csv(path, rows):
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    check_out_file(args.out)
    tokenizer, model = load_model(args.model, args.precision)

    seed = 0
    completed = 0

    while completed < args.games:
        seed += 1
        a_values, b_values = make_scenario(ITEM_POOL, seed)
        if not is_usable(ITEM_POOL, a_values, b_values):
            continue

        prompt = build_system_prompt(ITEM_POOL, a_values, args.max_turns)
        reminder = build_turn_reminder(ITEM_POOL)
        agent = ModelAgent(tokenizer, model, prompt, turn_reminder=reminder)
        opponent = ScriptedOpponent(ITEM_POOL, b_values, args.max_turns)

        result = run_game(agent, opponent, ITEM_POOL, a_values, b_values, args.max_turns)
        scored = score_game(result, ITEM_POOL, a_values, b_values)

        if args.show_transcript:
            print("--- seed", seed, "A values", a_values, "B values", b_values)
            for speaker, text in result["transcript"]:
                print(speaker, "|", text)
            print("--- outcome", result["outcome"])

        row = {
            "model": args.model,
            "precision": args.precision,
            "seed": seed,
            "agreed": scored["agreed"],
            "earned": scored["earned"],
            "score": scored["score"],
            "pareto": scored["pareto"],
            "turns": (len(result["transcript"]) + 1) // 2,
            "format_ok": scored["format_ok"],
            "parse_none": scored["parse_none"],
            "parse_invalid": scored["parse_invalid"],
        }
        # Written per game rather than once at the end, so a crash partway
        # through a long run does not discard the games already played.
        write_csv(args.out, [row])
        completed += 1
        print(seed, args.precision, "score", scored["score"],
              "pareto", scored["pareto"],
              "format_ok", scored["format_ok"],
              "none", scored["parse_none"],
              "invalid", scored["parse_invalid"])


if __name__ == "__main__":
    main()