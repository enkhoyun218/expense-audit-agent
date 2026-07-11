"""
Expense Audit Agent v0.1
========================
Your first financial agent. It reads an expense report (CSV) and a company
policy (markdown), asks Claude to audit every expense against the policy,
and writes a decision log you can inspect.

HOW TO RUN (see README.md for full setup):
    export ANTHROPIC_API_KEY=your-key-here
    python agent.py

Every design choice here is deliberately simple. Your job in Weeks 1-2 is to
understand it, extend it, and then BREAK it. The planted flaws in the data
(and in this code) are your curriculum.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone

import anthropic  # pip install anthropic

# ---------------------------------------------------------------- settings
MODEL = "claude-haiku-4-5-20251001"          # the model that powers the agent
DATA_FILE = "data/expenses.csv"    # the expense report to audit
POLICY_FILE = "policy.md"          # the rules the agent enforces
LOG_FILE = "audit_log.jsonl"       # every run appends its decisions here


# ---------------------------------------------------------------- step 1: load inputs
def load_expenses(path):
    """Read the CSV into a list of dictionaries, one per expense row."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_policy(path):
    """Read the policy file as plain text."""
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- step 2: build the prompt
def build_prompt(policy, expenses):
    """
    Everything the agent knows arrives through this prompt.
    Notice: the expense DESCRIPTIONS are untrusted user input, but we are
    pasting them straight into the prompt. Remember that in attacker week.
    """
    expense_block = json.dumps(expenses, indent=2)
    return f"""You are an expense auditor for Acme Corp. Audit every expense
below against the company policy. Think carefully about duplicates,
limits, receipts, and anything suspicious.

<policy>
{policy}
</policy>

<expenses>
{expense_block}
</expenses>

For EVERY expense id, return a verdict. Respond with ONLY a JSON array,
no other text, in this exact shape:
[
  {{
    "id": "E001",
    "verdict": "APPROVE" | "REJECT" | "FLAG_FOR_HUMAN",
    "policy_rule": "which rule applies, or 'none'",
    "reasoning": "one or two sentences explaining the decision"
  }}
]
"""


# ---------------------------------------------------------------- step 3: call the model
def run_audit(client, policy, expenses):
    """Send the prompt to Claude and parse its JSON reply."""
    prompt = build_prompt(policy, expenses)
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    # Some models return a "thinking" block before the answer, so we can't
    # assume the first content block is text — find the text block explicitly.
    raw = next(b.text for b in response.content if b.type == "text").strip()

    # Models sometimes wrap JSON in ```json fences; strip them if present.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        raw = raw.removeprefix("json").strip()

    return json.loads(raw)  # QUESTION: what happens if this line fails?


# ---------------------------------------------------------------- step 4: report + log
def print_report(verdicts, expenses):
    """Human-readable summary in the terminal."""
    by_id = {e["id"]: e for e in expenses}
    counts = {"APPROVE": 0, "REJECT": 0, "FLAG_FOR_HUMAN": 0}

    print(f"\n{'ID':<6}{'VERDICT':<17}{'AMOUNT':>10}  REASONING")
    print("-" * 90)
    for v in verdicts:
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
        amount = by_id.get(v["id"], {}).get("amount_usd", "?")
        print(f"{v['id']:<6}{v['verdict']:<17}{amount:>10}  {v['reasoning']}")

    total = sum(counts.values())
    print("-" * 90)
    print(f"Audited {total} expenses: "
          f"{counts.get('APPROVE', 0)} approved, "
          f"{counts.get('REJECT', 0)} rejected, "
          f"{counts.get('FLAG_FOR_HUMAN', 0)} flagged for human review.\n")


def write_log(verdicts):
    """
    Append every decision to audit_log.jsonl — one JSON object per line.
    An agent that acts on money MUST leave a trail. This file is the seed
    of the 'verification layer' idea: today you log your own agent;
    eventually you verify everyone else's.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for v in verdicts:
            f.write(json.dumps({"run_at": timestamp, "model": MODEL, **v}) + "\n")


# ---------------------------------------------------------------- main
def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set your API key first:  export ANTHROPIC_API_KEY=your-key-here")

    client = anthropic.Anthropic()
    expenses = load_expenses(DATA_FILE)
    policy = load_policy(POLICY_FILE)

    print(f"Auditing {len(expenses)} expenses against {POLICY_FILE} ...")
    verdicts = run_audit(client, policy, expenses)

    print_report(verdicts, expenses)
    write_log(verdicts)
    print(f"Decision log appended to {LOG_FILE}")


if __name__ == "__main__":
    main()
