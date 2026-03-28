---
name: seed-safety
description: Pre-flight checks and safe execution protocol for database seed scripts and migrations with verification and idempotency rules.
origin: Boiler 3.0
version: 1.0
---

# Seed & Migration Safety Skill

Use this whenever running seed scripts, database migrations, or any destructive/additive DB operation.

## Pre-Flight Checks (mandatory, every time)

1. **Verify working directory:**
   ```bash
   pwd
   ```
   Confirm output matches the project root. If not, `cd` to the correct directory before anything else.

2. **Check current DB state:**
   ```bash
   npx prisma db execute --stdin <<< "SELECT COUNT(*) FROM <target_table>;"
   ```
   Record the count. This is your baseline.

3. **Check for existing data overlap:**
   - If the seed creates records with known identifiers (slugs, names, SKUs), query for them first.
   - If any already exist, STOP and ask the user whether to skip duplicates, upsert, or wipe and reseed.

## Execution

4. **Run the seed/migration exactly once:**
   ```bash
   npx prisma db seed
   ```
   Or whatever the specific command is.

5. **Verify the result immediately:**
   ```bash
   npx prisma db execute --stdin <<< "SELECT COUNT(*) FROM <target_table>;"
   ```
   Compare to baseline. The delta should match exactly the number of records the seed was supposed to create.

6. **If the count is wrong:**
   - Do NOT re-run the seed.
   - Query for duplicates or anomalies.
   - Report findings to the user with the exact counts.
   - Wait for user direction before any cleanup.

## Rules

- Never re-run a seed on ambiguous failure. Always check DB state first.
- Never run seeds from a directory other than the project root.
- If writing a new seed script, always compile-check with `npx tsc --noEmit` before executing it.
- Make seeds idempotent when possible: use upserts or existence checks rather than blind inserts.
- For large seeds (50+ records), log progress during execution so partial failures are visible.
