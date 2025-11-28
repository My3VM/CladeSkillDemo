# Agent Skills in This Project

This project demonstrates **production-ready Agent Skills** using Claude Agent SDK with progressive disclosure.

## ⚙️ Prerequisites

**Required:** Claude Code CLI **2.0.55 or later**

```bash
claude --version  # Must show 2.0.55+
claude update     # If needed
```

Earlier versions don't include the `Skill` tool and Skills won't work.

## What Are Agent Skills?

Agent Skills are **filesystem-based workflows** that Claude autonomously invokes:

- ✅ `SKILL.md` files in `.claude/skills/` directories
- ✅ YAML frontmatter (name + description) + Markdown instructions
- ✅ Loaded from filesystem via `setting_sources=["user", "project"]`
- ✅ Model-invoked via `Skill` tool when description matches user prompt
- ✅ Enabled via `allowed_tools=["Skill", "Read", ...]`
- ✅ **Progressive disclosure:** Phase instructions revealed incrementally

## Skills in This Project

### Incident Analysis Skill ⭐ (Production-Ready)

**Location:** `.claude/skills/incident-analysis/SKILL.md`

**Description:** Analyze and resolve production incidents using systematic investigation, root cause analysis, and autonomous remediation

**When Claude Uses It:**
- Production system degraded or failing
- Users reporting issues
- Metrics showing abnormal behavior
- Need autonomous incident resolution

**What It Does:**
Implements a **6-phase incident response workflow with progressive disclosure:**

1. **Phase 1: Triage & Assessment** (`phases/triage.md`)
   - Gathers system metrics and health status
   - Assesses severity (Critical/High/Medium/Low)
   - Creates incident ticket with tracking ID
   - **Summary before transition:** Key findings, incident ID, severity, anomalies

2. **Phase 2: Investigation** (`phases/investigation.md`)
   - Analyzes logs for error patterns
   - Forms ranked hypotheses about root cause
   - Performs targeted testing
   - **Summary before transition:** Error patterns, ranked hypotheses, evidence, what was ruled out

3. **Phase 3: Root Cause Analysis** (`phases/rca.md`)
   - Deep-dive analysis by category (deployment/capacity/config/integration)
   - Validates root cause with 90%+ confidence
   - Documents evidence chain
   - **Summary before transition:** Confirmed root cause, confidence %, evidence, alternatives ruled out

4. **Phase 4: Remediation Planning** (`phases/remediation.md`)
   - Evaluates options (immediate/short-term/long-term)
   - Balances speed, risk, and completeness
   - Documents fix strategy and success criteria
   - **Summary before transition:** Chosen approach, execution steps, expected outcomes, rollback plan

5. **Phase 5: Execution** (`phases/execution.md`)
   - Executes remediation steps
   - Monitors for effects
   - Verifies resolution (metrics, health checks, stability)
   - **Summary before transition:** Steps executed, verification results, system status

6. **Phase 6: Communication & Documentation** (`phases/documentation.md`)
   - Creates post-mortem documentation
   - Notifies team via appropriate channels
   - Documents lessons learned and preventive measures

**Key Features:**
- 📋 **TodoWrite Integration:** Creates 6 todos (one per phase) for real-time progress tracking
- 🔄 **Progressive Disclosure:** Agent reads each phase file sequentially, preventing information overload
- 📊 **Structured Summaries:** Mandated phase completion summaries create audit trail
- 🔧 **MCP Tool Integration:** Uses monitoring and workflow orchestration tools
- ⏱️ **Time-bounded:** Each phase has target duration (2-10 minutes)
- ✅ **Success Criteria:** Clear completion criteria for each phase

---

### Log Analytics Skill 📊 (Production-Ready)

**Location:** `.claude/skills/log-analytics/SKILL.md`

**Description:** Generate and execute Python code to analyze large log datasets (1000+ entries), detect patterns, and extract actionable insights

**When Claude Uses It:**
- Need to analyze 500+ log entries
- Detect error patterns across large datasets
- Calculate statistical distributions (error rates, response times)
- Perform time-series analysis on logs
- Identify anomalies and outliers
- Can be invoked by other skills (e.g., `incident-analysis`) when deep log analysis is needed

**What It Does:**
Implements a **3-phase log analysis workflow with progressive disclosure:**

1. **Phase 1: Data Fetch** (`phases/data-fetch.md`)
   - Fetches raw log data (1000+ entries) from the MCP server
   - Saves data to `analytics/incident_logs.json`
   - Inspects log structure and identifies key fields
   - **Summary before transition:** Total entries, error rate, primary error codes

2. **Phase 2: Code Generation** (`phases/code-generation.md`)
   - **Generates Python analysis script** tailored to actual log structure (not generic templates!)
   - Script analyzes: error patterns, service breakdowns, time-series, performance metrics, anomalies
   - Saves script to `analytics/parse_logs_[timestamp].py`
   - **Summary before transition:** Script filename, analysis capabilities

3. **Phase 3: Analysis Execution** (`phases/analysis-execution.md`)
   - Executes the generated Python script
   - Interprets results and extracts insights
   - Formulates root cause hypotheses based on patterns
   - Provides immediate/short-term/long-term recommendations
   - Saves results to `analytics/analysis_results_[timestamp].json`

**🔒 Security Features:**
- **Enforced File Paths:** All files (logs, scripts, results) MUST be saved to `analytics/` directory
- **Blocked Paths:** `/tmp/`, `/private/tmp/` are **forbidden** (prevents exposure to other processes)
- **Secure Workspace:** Sensitive incident data stays within project boundaries
- **Explicit Warnings:** Each phase file includes security requirements with verification steps

**Key Features:**
- 🐍 **Dynamic Code Generation:** Claude writes Python code based on ACTUAL log structure
- 📈 **Statistical Analysis:** Calculates error rates, percentiles (P95, P99), time distributions
- 🔍 **Anomaly Detection:** Identifies services with high error rates, unusual patterns
- 💾 **Audit Trail:** Saves raw data, generated scripts, and results for review
- 🔗 **Composable:** Can be invoked by other skills or used standalone
- 🎯 **JSON Output:** Structured results for programmatic consumption

**MCP Tools Used:**
- `get_raw_logs(incident_id, timeframe)` - Fetch large log datasets
- `execute_analysis_script(script_path)` - Run generated Python code

**Example Generated Output:**
```json
{
  "summary": {
    "total_logs": 1200,
    "total_errors": 45,
    "error_rate_percent": 3.75
  },
  "error_analysis": {
    "top_error_codes": [
      {"code": "AUTH_TIMEOUT", "count": 30},
      {"code": "REDIS_TIMEOUT", "count": 15}
    ],
    "errors_by_service": {
      "auth-service": 30,
      "session-store": 15
    },
    "peak_error_hour": {"hour": 14, "count": 25}
  },
  "performance_metrics": {
    "avg_response_time_ms": 245.3,
    "p95_response_time_ms": 850.0,
    "p99_response_time_ms": 5000.0
  },
  "anomalies": [
    {
      "type": "high_error_rate",
      "service": "auth-service",
      "error_rate_percent": 6.25,
      "severity": "medium"
    }
  ]
}
```

---

## How Skills Are Loaded

In the agent configuration:

```python
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

project_root = Path(__file__).parent.parent

options = ClaudeAgentOptions(
    cwd=str(project_root),                       # Project with .claude/skills/
    setting_sources=["user", "project"],         # Load Skills from filesystem
    system_prompt=base_system_prompt,
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    permission_mode='bypassPermissions',
    mcp_servers=mcp_servers,                     # MCP tools enabled here
    allowed_tools=["Skill", "Read", "TodoWrite", "Bash"],  # Enable core tools
    max_turns=100                                # Full workflow completion
)

async for message in query(prompt=user_prompt, options=options):
    # Claude autonomously invokes Skills when relevant
    print(message)
```

## Skill File Structure

Each Skill is a directory with a `SKILL.md` file:

```
.claude/skills/
├── incident-analysis/
│   ├── SKILL.md                  # Main skill definition
│   ├── phases/                   # Progressive disclosure phase files
│   │   ├── triage.md
│   │   ├── investigation.md
│   │   ├── rca.md
│   │   ├── remediation.md
│   │   ├── execution.md
│   │   └── documentation.md
│   └── tools/                    # Tool usage documentation
│       ├── monitoring-analysis.md
│       └── workflow-orchestration.md
│
└── log-analytics/
    ├── SKILL.md                  # Main skill definition
    └── phases/                   # Progressive disclosure phase files
        ├── data-fetch.md
        ├── code-generation.md
        └── analysis-execution.md
```

### SKILL.md Format

```markdown
---
name: skill-name
description: When to use this skill - Claude matches this to user prompts
---

# Skill Name

Instructions and guidance for Claude when this skill is invoked.

## When to Use This Skill
- Condition 1
- Condition 2

## How to Use This Skill
Step-by-step instructions...

## Key Principles
Important guidelines...

## Example
Sample usage...
```

## Testing Skills

### List Available Skills

```python
async for message in query(
    prompt="What Skills are available?",
    options=options
):
    print(message)
```

### Test a Specific Skill

```python
async for message in query(
    prompt="Investigate why our API is slow and resolve it",
    options=options
):
    print(message)
```

Claude will automatically invoke the `incident-analysis` Skill based on the description match.

## Creating New Skills

1. **Create skill directory:**
   ```bash
   mkdir -p .claude/skills/your-skill-name
   ```

2. **Create SKILL.md:**
   ```bash
   touch .claude/skills/your-skill-name/SKILL.md
   ```

3. **Add content:**
   ```markdown
   ---
   name: your-skill-name
   description: Clear description of when to use this skill
   ---
   
   # Your Skill Name
   
   Detailed instructions for Claude...
   ```

4. **Test it:**
   - Ask Claude a question that matches the description
   - Claude should automatically invoke your Skill

## Skills vs MCP Tools

**Skills** (`.claude/skills/SKILL.md`):
- ✅ High-level workflows and processes
- ✅ Multi-step reasoning patterns
- ✅ Domain-specific guidance
- ✅ Best practices and methodologies
- ✅ Claude decides when to use them

**MCP Tools** (via MCP servers):
- ✅ Low-level actions and operations
- ✅ External system integrations
- ✅ Data retrieval and manipulation
- ✅ Command execution
- ✅ Claude calls them explicitly

**Together:**
Skills guide *how* Claude thinks and approaches problems.
MCP Tools provide *what* Claude can actually do.

## Key Differences from Python Classes

❌ **Wrong** (what I initially built):
```python
from skills import ProgressiveReasoningSkill
skill = ProgressiveReasoningSkill(max_steps=20)
```

✅ **Right** (actual Agent Skills):
```markdown
.claude/skills/progressive-reasoning/SKILL.md
```

Agent Skills are:
- **Filesystem-based**, not programmatic
- **Model-invoked**, not called by code
- **Description-matched**, not explicitly invoked
- **Loaded at runtime**, not imported

## Troubleshooting

### Skills Not Loading

**Check setting_sources:**
```python
# Wrong - Skills won't load
options = ClaudeAgentOptions(allowed_tools=["Skill"])

# Right - Skills will load
options = ClaudeAgentOptions(
    setting_sources=["project"],  # Required!
    allowed_tools=["Skill"]
)
```

**Check working directory:**
```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",  # Must contain .claude/skills/
    setting_sources=["project"]
)
```

**Verify filesystem:**
```bash
ls .claude/skills/*/SKILL.md
```

### Skill Not Being Used

**Check description:**
- Make it specific and keyword-rich
- Match user's likely prompts
- Be clear about when it applies

**Check enabled:**
```python
allowed_tools=["Skill"]  # Must include "Skill"
```

## Resources

- [Agent Skills Documentation](https://platform.claude.com/docs/en/agent-sdk/skills)
- [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)

## Summary

This project now correctly uses Agent Skills as filesystem-based `SKILL.md` files that Claude autonomously invokes. Combined with MCP tools for actual operations, this enables powerful autonomous incident response with progressive reasoning and systematic workflows.

