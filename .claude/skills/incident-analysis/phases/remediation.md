# Phase 4: Remediation Planning (2-3 minutes)

## Objective
Choose the best remediation approach balancing speed, risk, and completeness.

## Evaluate Remediation Options

### Immediate Actions (Minutes)
- **Rollback**: Revert to previous known-good version
- **Restart**: Restart affected services/servers
- **Scale**: Add more resources to handle load
- **Disable**: Turn off problematic feature
- **Circuit Break**: Isolate failing dependency

### Short-term Fixes (Hours)
- **Hotfix**: Quick code patch for critical issue
- **Configuration Change**: Adjust settings/limits
- **Resource Adjustment**: Increase capacity/limits
- **Temporary Workaround**: Bypass issue temporarily

### Long-term Solutions (Days/Weeks)
- **Code Fix**: Proper bug fix with tests
- **Architecture Change**: Redesign component
- **Infrastructure Upgrade**: Better resources/tools
- **Process Improvement**: Prevent future occurrences

## Choose Best Approach

Consider these factors:

**Speed:**
- How fast can it be implemented?
- How urgently is resolution needed?

**Risk:**
- What's the risk of making it worse?
- Is rollback possible if it fails?
- What's the blast radius?

**Completeness:**
- Does it fully resolve the issue?
- Or just reduce symptoms?
- Will issue recur?

**Trade-offs:**
- Quick but incomplete vs slow but thorough
- High certainty vs some risk
- Immediate relief vs permanent fix

## Get Approval (If Needed)

For critical/risky actions:
- Document planned steps clearly
- Explain rationale and risks
- Get stakeholder approval
- Have rollback plan ready

For routine remediation:
- Proceed autonomously
- Document what you're doing
- Monitor effects carefully

## Document the Plan

Before executing:
- List specific steps in order
- Identify tools/commands to use
- Note expected outcomes
- Define success criteria
- Plan verification steps

## Phase Completion

Before moving to the next phase:

**Provide Remediation Plan Summary:**
- Chosen approach (immediate/short-term/long-term)
- Specific steps to execute
- Expected outcomes and success criteria
- Rollback plan if needed

Then proceed to **Phase 5: Execution** by reading `phases/execution.md`.

