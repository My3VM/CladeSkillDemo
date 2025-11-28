# Phase 3: Root Cause Analysis (2-5 minutes)

## Objective
Confirm the root cause with high confidence and document the evidence chain.

## Deep Dive by Category

### Deployment-Related
If recent deployment suspected:
- Examine code changes in the deployment
- Check for new dependencies or version changes
- Review deployment logs for errors
- Compare before/after behavior

### Capacity-Related
If resource exhaustion suspected:
- Check CPU, memory, disk, network limits
- Analyze growth trends
- Identify resource leaks
- Review scaling policies

### Configuration-Related
If config change suspected:
- Review recent configuration changes
- Compare current vs previous configs
- Check for typos or invalid values
- Validate against documentation

### Integration-Related
If dependency issue suspected:
- Check external service health
- Review API changes from dependencies
- Analyze network connectivity
- Check authentication/authorization

## Validate Root Cause

**Achieve 90%+ Confidence:**
- Confirm with multiple data points
- Ensure timeline matches
- Verify affected scope makes sense
- Check if explanation is complete

**Document Evidence Chain:**
- What led you to this conclusion?
- What data supports it?
- What alternative explanations were ruled out?
- How confident are you? (percentage)

## Tools to Use

- `root_cause_analysis(incident_type, deployment)` - Deep RCA assistance
- `analyze_logs()` - Additional log correlation
- `get_system_metrics()` - Confirm resource state

## Phase Completion

Before moving to the next phase:

**Provide RCA Summary:**
- Confirmed root cause with confidence level (target: 90%+)
- Evidence chain supporting the conclusion
- Alternative explanations ruled out
- Validation data points

Then proceed to **Phase 4: Remediation Planning** by reading `phases/remediation.md`.

