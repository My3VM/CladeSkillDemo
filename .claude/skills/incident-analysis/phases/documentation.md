# Phase 6: Communication & Documentation (3-5 minutes)

## Objective
Notify stakeholders, document the incident, and create action items for improvement.

## Notify Stakeholders

### Team Channels

Use `notify_team()` to send updates to:
- **Slack/Teams channels** - Dev team, ops team
- **Status pages** - Customer-facing status
- **Incident channels** - Dedicated incident room

### Resolution Announcement

Include in notification:
- ✅ **Incident resolved** - State clearly it's fixed
- **Duration** - How long it lasted
- **Impact** - What was affected
- **Root cause** - Brief explanation
- **Resolution** - What fixed it
- **Prevention** - What's being done to prevent recurrence

### Example Message

```
🟢 RESOLVED: Production API Degradation (INC-2024-1127)

Duration: 27 minutes (15:00 - 15:27 UTC)
Impact: API response times elevated, 8.5% error rate
Root Cause: Missing connection.close() in error handler (v2.3.1)
Resolution: Rollback to v2.3.0 + database pool scaling
Status: All metrics back to normal, monitoring ongoing

Action items created for prevention.
```

## Document Incident

### Create Post-Mortem

Use `document_resolution()` to create comprehensive documentation:

**Timeline of Events:**
- When alert received
- When investigation started
- Key findings at each phase
- When remediation executed
- When resolution verified
- Total time to resolution

**Root Cause Explanation:**
- What went wrong
- Why it happened
- How it was discovered
- Evidence that confirms it

**Remediation Steps Taken:**
- What actions were executed
- Why these actions were chosen
- What alternatives were considered
- How effectiveness was verified

**Verification Results:**
- Metrics before and after
- Error rates comparison
- System health status
- Ongoing monitoring plan

### Tools to Use

- `document_resolution(incident_id, resolution, action_items)` - Create post-mortem
- `notify_team(incident_id, channel, message)` - Send notifications

## Create Action Items

### Prevent Recurrence

- Fix underlying cause permanently
- Add validation to prevent similar bugs
- Improve testing coverage
- Update deployment checklist

### Improve Detection

- Add monitoring/alerts for this scenario
- Lower alert thresholds if appropriate
- Create dashboard for this metric
- Set up automated health checks

### Update Documentation

- Add to runbook
- Document troubleshooting steps
- Update architecture diagrams
- Share lessons learned

### Schedule Retrospective

- Set date for team discussion
- Invite relevant stakeholders
- Prepare incident timeline
- Focus on process improvement, not blame

## Example Action Items

```
1. [P0] Add connection.close() to all error handlers (DEV-1234)
2. [P0] Add integration test for connection cleanup (DEV-1235)
3. [P1] Set up alert for DB connection pool >80% (OPS-5678)
4. [P2] Create runbook for connection leak scenarios (DOC-9012)
5. [P2] Schedule retrospective for next sprint planning (TEAM-3456)
```

## Final Checklist

Before closing the incident, verify:

- ✅ Metrics returned to baseline
- ✅ No new errors occurring
- ✅ Team notified of resolution
- ✅ Incident documented in tracking system
- ✅ Post-mortem created
- ✅ Action items logged
- ✅ All phases completed in TodoWrite
- ✅ Stakeholders informed

## Completion

🎉 **Incident successfully resolved and documented!**

Update your TodoWrite to mark all phases as completed, then provide a final summary to the user.

