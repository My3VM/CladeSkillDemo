# Phase 2: Investigation (5-10 minutes)

## Objective
Gather evidence and form hypotheses about the root cause.

## Analyze Logs

**Pattern Detection:**
- Search for error patterns and anomalies
- Identify when issues started (exact timestamp)
- Find correlations:
  - Time-based (when did it start?)
  - Service-based (which components affected?)
  - Operation-based (which actions failing?)

**Use Tools:**
- `analyze_logs(timeframe, filter, incident_type)` - Find error patterns
- Start with recent timeframe (last hour), expand if needed
- Filter by error type if patterns emerge

## Form Hypotheses

Based on evidence gathered:

1. **List possible root causes**
   - Deployment issues
   - Configuration changes
   - Resource exhaustion
   - External dependencies
   - Data corruption
   - Code bugs

2. **Rank by likelihood**
   - Most likely hypothesis first
   - Consider recent changes
   - Look for simplest explanation

3. **Identify validation criteria**
   - What would confirm each hypothesis?
   - What would rule it out?

## Targeted Testing

**Systematic Approach:**
- Test most likely hypothesis first
- Look for supporting or contradicting evidence
- Use findings to refine hypotheses
- Pivot if hypothesis disproven
- Continue until root cause identified

**Document Findings:**
- What you tested
- What you found
- What it rules in/out

## Phase Completion

Before moving to the next phase:

**Provide Investigation Summary:**
- Error patterns and anomalies discovered
- Leading hypotheses (ranked by likelihood)
- Evidence supporting each hypothesis
- What was ruled out

Then proceed to **Phase 3: Root Cause Analysis** by reading `phases/rca.md`.

