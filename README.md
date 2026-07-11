# Expense Audit Agent — Sprint 1 Starter Kit

Your first financial agent: it audits an expense report against a company
policy using Claude, prints verdicts, and logs every decision.

## Files

- `agent.py` — the agent (heavily commented; read every line)
- `policy.md` — the expense policy it enforces
- `data/expenses.csv` — 25 expenses. **Several have planted problems.** Finding them all is part of the exercise — don't peek at answer keys that don't exist; reason it out.
- `audit_log.jsonl` — created after your first run; every decision, timestamped

## Setup (once, ~15 minutes)

1. **Install Python 3.10+** — check with `python3 --version` in your terminal. If missing: https://python.org/downloads
2. **Get an API key** — sign up at https://console.anthropic.com, create a key under API Keys ($5 of credit is more than enough for weeks of this).
3. **Install the SDK:**
   ```
   pip3 install anthropic
   ```
4. **Set your key** (every new terminal session, or add to your shell profile):
   ```
   export ANTHROPIC_API_KEY=your-key-here
   ```

## Run it

```
cd expense-audit-agent
python3 agent.py
```

You should see a verdict table for all 25 expenses and a new `audit_log.jsonl`.

## Week 1 exercises (do in order)

1. **Run it 3 times.** Compare the three runs in `audit_log.jsonl`. Do the verdicts change between runs? Which ones? Write down every inconsistency — *an auditor that gives different answers on the same data is your first failure mode.*
2. **Manually audit the CSV yourself** against `policy.md`, before trusting the agent. Make your own verdict list. Where do you and the agent disagree? Who's right?
3. **Study E019 closely.** Read its description field. What is it trying to do to your agent? Did it work? (This is called prompt injection — untrusted data giving instructions to the model.)
4. **Check the sneaky ones:** E010+E011 (split to dodge a limit?), E012+E013 (duplicate), E003+E025 (resubmission), E015 (currency), E024 (negative amount), E005 vs E023 (flight class rules).
5. **Find the crash.** `run_audit()` has a line with a QUESTION comment. Feed the agent 200 expenses instead of 25 (copy-paste rows) and see what breaks and why.

## Week 2: make it yours

- Add a rule to `policy.md` and expenses that test it.
- Make the agent handle a malformed CSV row without crashing.
- Add a `confidence` field to verdicts — then check whether high confidence actually correlates with being right.

## Week 3–4: attacker mode

Start your **Failure Catalog** (a running doc). For every failure you find, record: name, how to reproduce it, why it happens, what damage it could cause with real money. Categories to fill: input attacks (E019 is #1), inconsistency, silent errors, reasoning failures, accountability gaps (what does the log *not* capture?).

By Aug 31 you want 20+ entries. That document is your ticket into every Sprint 2 conversation.
