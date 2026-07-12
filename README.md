# Expense Audit Agent

Your first financial agent: it audits an expense report against a company
policy using Claude, prints verdicts, and logs every decision.

## Files

- `agent.py` — the agent
- `policy.md` — the expense policy it enforces
- `data/expenses.csv` — 25 expenses
- `audit_log.jsonl` — created after your first run; every decision, timestamped

## Setup (once, ~15 minutes)

1. **Install Python 3.10+**
2. **Get an API key**
3. **Install the SDK:**
   ```
   pip3 install anthropic
   ```
4. **Set your key** (every new terminal session, or add to your shell profile):
   ```
   export ANTHROPIC_API_KEY=your-key-here
   ```
