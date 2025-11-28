# Phase 1: Triage & Assessment (2-5 minutes)

## Objective
Quickly assess the situation and determine incident severity.

## Gather Initial Data

**System Metrics:**
- Get current system metrics (response time, error rate, resource usage)
- Compare against baselines
- Identify anomalies

**Recent Changes:**
- Check recent deployments
- Review configuration changes
- Note traffic pattern shifts

**Scope Identification:**
- Which services are affected?
- How many users impacted?
- Which regions/environments?

## Assess Severity

Choose the appropriate severity level:

- **Critical**: Complete outage, data loss risk, security breach
- **High**: Major degradation, significant customer impact
- **Medium**: Partial degradation, workarounds available
- **Low**: Minor issues, minimal or no customer impact

## Create Incident Ticket

Use `create_incident()` tool to:
- Log the incident for tracking
- Set severity level
- Document initial symptoms
- Record start time

## Tools to Use

- `get_system_metrics(incident_type)` - Get current system state
- `create_incident(severity, title, description)` - Create tracking ticket

## Phase Completion

Before moving to the next phase:

**Provide a Phase Summary:**
- Key findings from triage
- Incident ID and severity level
- Critical metrics observed
- Next phase objective

Then proceed to **Phase 2: Investigation** by reading `phases/investigation.md`.

