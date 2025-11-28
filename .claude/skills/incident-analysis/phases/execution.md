# Phase 5: Execution (2-5 minutes)

## Objective
Execute remediation safely and verify the issue is resolved.

## Execute Remediation

### Follow the Plan

Execute steps in the order planned:
1. Follow your documented plan from Phase 4
2. Execute one step at a time
3. Verify each step before proceeding
4. Document what you're doing as you go

### Use Dry-Run When Available

- If tool supports `dry_run` flag, use it first
- Review dry-run output for unexpected effects
- Proceed with real execution only if dry-run looks good

### Monitor for Effects

**Watch for:**
- Expected improvements (metrics improving)
- Unexpected side effects (new errors)
- Partial success (some but not all better)
- Rollback triggers (things getting worse)

**Be Ready to:**
- Stop if things worsen
- Rollback if needed
- Adjust approach mid-execution
- Call for help if stuck

### Tools to Use

- `execute_remediation(incident_id, steps, dry_run)` - Execute planned fixes
- Set `dry_run=True` first, then `dry_run=False`
- Monitor logs and metrics during execution

## Verify Resolution

### Check Metrics

- **Response times** back to baseline?
- **Error rates** dropped to normal?
- **Resource usage** healthy?
- **Connection counts** normal?

### Confirm Errors Stopped

- No new errors of the same type?
- Existing errors cleared/recovered?
- System processing requests normally?

### Validate with Tests

- Sample requests succeeding?
- End-to-end workflows working?
- Critical paths functional?

### Monitor Duration

- Watch for 5-10 minutes minimum
- Ensure issue doesn't immediately recur
- Confirm stability over time

### Tools to Use

- `verify_health(after_remediation=True)` - Health verification
- `get_system_metrics()` - Check current state
- Compare against baseline from Phase 1

## Handle Incomplete Resolution

If issue not fully resolved:
1. Document what improved vs what didn't
2. Return to Phase 3 (RCA) with new information
3. Form new hypothesis
4. Plan additional remediation

If issue got worse:
1. Stop immediately
2. Rollback changes
3. Reassess situation
4. Get help if needed

## Phase Completion

Before moving to the next phase:

**Provide Execution Summary:**
- Remediation steps executed
- Verification results (metrics, health checks)
- System status after remediation
- Any issues encountered or incomplete items

Then proceed to **Phase 6: Communication & Documentation** by reading `phases/documentation.md`.

