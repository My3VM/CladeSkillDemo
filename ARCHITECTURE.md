# Production-Ready Architecture: Claude Agent SDK + MCP + Skills

## ✅ Verified Working Implementation

This project demonstrates the **Claude Agent SDK** with Skills and MCP:
1. **Agent Skills** (filesystem-based SKILL.md files with progressive disclosure)
   - `incident-analysis` - 6-phase incident response workflow
   - `log-analytics` - **Dynamic Python code generation** for log analysis
2. **MCP Servers** (FastMCP with streamable HTTP on ports 9001, 9002, 9003)
3. **Claude Agent SDK** (`query()` function with `ClaudeAgentOptions`)
4. **CLI Requirement:** Claude Code CLI 2.0.55+ (for `Skill` tool support)

**Key Innovation:** The `log-analytics` skill demonstrates **Claude generating and executing custom Python code** based on actual data structures, not templates.

## Key Concepts

### Claude Skills
- **Filesystem-Based Capabilities**: Skills are just markdown files with YAML frontmatter - no complex frameworks, easily version-controlled, and shareable across teams
- **Autonomous Skill Discovery**: Claude automatically matches user queries to skill descriptions and invokes relevant workflows without explicit programming
- **Composable Expertise**: Package domain knowledge into reusable skills that transform general-purpose agents into specialized experts (e.g., incident responder, log analyst)

### Progressive Disclosure
- **Context Efficiency**: Load only 50-150 lines per phase vs entire 192-line monolith, reducing costs by 23-48% and enabling unlimited skill complexity
- **Just-In-Time Learning**: Claude reads detailed phase instructions only when entering that phase, keeping context focused on current task
- **Scalable Knowledge**: Add unlimited playbooks, phases, and documentation without bloating the initial skill load - only relevant content gets loaded

### Code Execution
- **Deterministic Operations**: Use Python/Bash for operations requiring reliability (sorting, parsing, calculations) rather than expensive token generation
- **Dynamic Code Generation**: Claude writes custom analysis scripts based on actual data structures, not pre-written templates
- **Tool Augmentation**: Code execution extends Claude's capabilities beyond language model limitations (file I/O, network calls, computation)

## Power Tools Used

### Core Technologies
- **Claude Agent SDK** - Python SDK providing `query()` function for building agentic workflows with skills and tool use
- **Claude Code CLI 2.0.55+** - Command-line interface with `Skill` tool support and filesystem access for agent execution
- **FastMCP** - Python framework for building MCP servers with streamable HTTP/SSE transport on custom ports
- **FastAPI + WebSockets** - Modern async web framework with real-time bidirectional communication for live streaming UI

### Agent Tools
- **Skill Tool** - Built-in tool for discovering and loading skill workflows from `.claude/skills/` directories
- **Read/Write/Edit Tools** - Filesystem operations for progressive disclosure and dynamic file manipulation
- **Bash Tool** - Code execution for running Python scripts, shell commands, and helper utilities
- **TodoWrite Tool** - Task tracking with real-time progress updates for multi-phase workflows

### UI & Presentation
- **Rich** - Python library for beautiful terminal output with colors, tables, and progress indicators
- **Marked.js** - Client-side markdown parser for rendering agent responses with proper formatting in browser
- **Python-dotenv** - Environment variable management for API keys and configuration

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Claude Agent SDK                                  │
│  query(prompt, options) → Claude Code CLI 2.0.55+                    │
│                                                                       │
│  Options:                                                             │
│  - setting_sources: ["user", "project"]  ← Load Skills               │
│  - allowed_tools: ["Skill", "Read", "TodoWrite", "Bash", "Write"]    │
│  - mcp_servers: {monitoring, workflow, log-analytics}                │
│  - permission_mode: 'bypassPermissions'                               │
│  - max_turns: 100                                                     │
└──────┬──────────────────┬───────────────────┬────────────────────────┘
       │                  │                   │
       │ 1. Invokes       │ 2. Reads          │ 3. Calls
       │ Skill tool       │ phase files       │ MCP tools
       │                  │                   │
   ┌───▼──────────────┐  ┌▼─────────────────┐  ┌▼───────────────────┐
   │  Skill Tool      │  │  Phase Files     │  │  MCP Servers       │
   │                  │  │                  │  │                    │
   │  Discovers:      │  │  Progressive     │  │  Port 9001:        │
   │  - incident-     │  │  Disclosure:     │  │  Monitoring        │
   │    analysis      │  │                  │  │                    │
   │  - log-analytics │  │  Incident:       │  │  Port 9002:        │
   │                  │  │  1. triage.md    │  │  Workflow          │
   │  Returns:        │  │  2. investigate  │  │                    │
   │  SKILL.md        │  │  3. rca.md       │  │  Port 9003:        │
   │  content         │  │  4. remediate    │  │  Log Analytics     │
   │                  │  │  5. execute.md   │  │                    │
   │  Claude reads    │  │  6. document     │  │  Tools:            │
   │  phase files     │  │                  │  │  - get_raw_logs()  │
   │  using Read tool │  │  Log Analytics:  │  │  - analyze_logs()  │
   │                  │  │  1. data-fetch   │  │  - execute_script()│
   │                  │  │  2. code-gen     │  │  - remediation     │
   │                  │  │  3. analysis     │  │  - incidents       │
   │                  │  │                  │  │  - notify          │
   │                  │  │  Each phase →    │  │                    │
   │                  │  │  structured      │  │  Claude calls      │
   │                  │  │  summary         │  │  tools explicitly  │
   └──────────────────┘  └──────────────────┘  └────────────────────┘
```

## Component Breakdown

### 1. Agent Skills (.claude/skills/)

**What They Are:**
- `SKILL.md` files in `.claude/skills/` directories
- YAML frontmatter with name + description
- Markdown content with instructions for Claude

**How They Work:**
1. Claude Code CLI discovers skills in `.claude/skills/` via `setting_sources`
2. When user prompt matches a skill description, Claude invokes `Skill` tool
3. Skill tool returns SKILL.md content with workflow instructions
4. Claude reads phase files progressively using `Read` tool
5. Each phase provides next phase to read (progressive disclosure)
6. Agent creates structured summaries before phase transitions

**Skills in This Project:**

#### `.claude/skills/incident-analysis/SKILL.md`
```yaml
---
name: incident-analysis
description: Analyze and resolve production incidents using systematic investigation, 
             root cause analysis, and autonomous remediation
---
```

**6-Phase Workflow with Progressive Disclosure:**
1. **Triage & Assessment** (`phases/triage.md`) - Gather metrics, assess severity, create incident
2. **Investigation** (`phases/investigation.md`) - Analyze logs, form ranked hypotheses
3. **Root Cause Analysis** (`phases/rca.md`) - Confirm root cause with 90%+ confidence
4. **Remediation Planning** (`phases/remediation.md`) - Design fix strategy (speed/risk/completeness)
5. **Execution** (`phases/execution.md`) - Execute remediation, verify resolution
6. **Communication & Documentation** (`phases/documentation.md`) - Document and notify team

**Key Features:**
- **Phase Transitions:** Mandated structured summary before moving to next phase
- **Progressive Disclosure:** Each phase file tells agent which file to read next
- **Evidence Chain:** Documents findings, hypotheses, and decisions at each step
- **MCP Integration:** Uses monitoring and workflow orchestration tools
- **TodoWrite Tracking:** 6 todos matching 6 phases for real-time progress

---

#### `.claude/skills/log-analytics/SKILL.md`
```yaml
---
name: log-analytics
description: Generate and execute Python code to analyze large log datasets, 
             detect patterns, and extract actionable insights
---
```

**3-Phase Workflow with Code Generation:**
1. **Data Fetch** (`phases/data-fetch.md`) - Fetch 1000+ log entries, save to `analytics/incident_logs.json`
2. **Code Generation** (`phases/code-generation.md`) - **Generate Python script** tailored to actual log structure
3. **Analysis Execution** (`phases/analysis-execution.md`) - Execute script, interpret results, provide recommendations

**Key Features:**
- **Dynamic Code Generation:** Claude writes Python code based on ACTUAL log structure (not templates)
- **Statistical Analysis:** Error rates, percentiles (P95, P99), time-series distributions
- **Anomaly Detection:** Identifies services with abnormal error rates, response times
- **Audit Trail:** Saves raw data, generated scripts, and analysis results
- **Composable:** Can be invoked standalone or by other skills (e.g., incident-analysis)
- **MCP Integration:** Uses log-analytics server (port 9003)

**MCP Server Data Flow:**
```
1. Agent calls: mcp__log-analytics__get_raw_logs(incident_id="INC-2025-001")
2. MCP server (port 9003) GENERATES 1200 realistic log entries on-the-fly
3. Agent receives JSON with logs (errors, warnings, normal traffic)
4. Agent saves to: analytics/incident_logs.json
5. Agent generates Python code to analyze this data
6. Agent executes code and produces insights
```

**🔒 Security Enforcement:**
- **CRITICAL:** All file paths MUST be within the `analytics/` directory
- **Blocked paths:** `/tmp/`, `/private/tmp/` - Security risk (files accessible to other processes)
- **Enforced in phase files:** Each phase explicitly forbids saving to temp directories
- **Why:** Incident logs contain sensitive data that must stay within secure project workspace

**Generated Files:**
- `analytics/incident_logs.json` - Raw log data (1200 entries fetched from MCP)
- `analytics/parse_logs_[timestamp].py` - Generated Python analysis code (348 lines)
- `analytics/analysis_results_[timestamp].json` - Structured analysis output

**Important:** If you delete `incident_logs.json`, the workflow will automatically re-fetch from the MCP server!

---

### 2. MCP Servers (FastMCP)

**What They Are:**
- Python servers using `fastmcp` library
- Expose tools via streamable HTTP transport
- Server-Sent Events (SSE) for real-time communication

**How They Work:**
- Define tools with `@mcp_server.tool()` decorator
- Run on specific ports (9001, 9002)
- Claude calls them explicitly when needed
- Return JSON results

**Servers in This Project:**

#### Monitoring & Analysis Server (Port 9001)
```python
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("monitoring-analysis", host="0.0.0.0", port=9001)

@mcp_server.tool()
async def get_system_metrics(incident_type: Optional[str] = None) -> str:
    # Return metrics as JSON
    pass

mcp_server.run(transport="streamable-http")
```

**Tools:**
- `get_system_metrics()` - Current system state
- `analyze_logs()` - Log pattern detection
- `root_cause_analysis()` - Deep RCA
- `verify_health()` - Health verification

#### Workflow Orchestration Server (Port 9002)
**Tools:**
- `create_incident()` - Incident tickets
- `execute_remediation()` - Execute fixes
- `document_resolution()` - Create post-mortem
- `notify_team()` - Team notifications

#### Log Analytics Server (Port 9003)
**Tools:**
- `get_raw_logs(incident_id, timeframe)` - Fetch 1000+ log entries as JSON
- `execute_analysis_script(script_path)` - Run generated Python analysis code

**Purpose:** Enables Claude to generate and execute custom Python code for parsing large log datasets, detecting patterns, and extracting insights. Used by the `log-analytics` Agent Skill.

### 3. Claude Agent SDK Integration

**How It All Connects:**

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from pathlib import Path

# Define MCP server connections (SSE endpoints)
mcp_servers = {
    'monitoring-analysis': {
        'type': 'sse',
        'url': 'http://127.0.0.1:9001/sse'
    },
    'workflow-orchestration': {
        'type': 'sse',
        'url': 'http://127.0.0.1:9002/sse'
    },
    'log-analytics': {
        'type': 'sse',
        'url': 'http://127.0.0.1:9003/sse'
    }
}

# Configure agent options
options = ClaudeAgentOptions(
    cwd=str(Path.cwd()),                    # Project root with .claude/skills/
    setting_sources=["user", "project"],    # Load Skills from filesystem
    system_prompt=base_system_prompt,       # Base agent instructions
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    permission_mode='bypassPermissions',    # Autonomous execution
    mcp_servers=mcp_servers,                # MCP tools enabled
    allowed_tools=["Skill", "Read", "TodoWrite", "Bash"],  # Enable core tools
    max_turns=100                           # Allow full 6-phase completion
)

# Run agent
async for message in query(
    prompt="Production system is degraded. Users can't log in.",
    options=options
):
    # Claude will:
    # 1. Invoke Skill tool with incident-analysis
    # 2. Read SKILL.md to understand the workflow
    # 3. Read phases/triage.md and follow instructions
    # 4. Provide phase summary before moving to next phase
    # 5. Read phases/investigation.md and continue
    # 6. Progress through all 6 phases with MCP tool calls
    # 7. Track progress with TodoWrite (6 todos, 6 phases)
    print(message)
```

## How It Works in Practice

### User Prompt
```
"Our production API is slow and users are complaining. 
Error rate is elevated. Please investigate and resolve."
```

### What Claude Does (Actual Execution Flow)

**Turn 1: Skill Invocation**
```
Agent: "I'll help you investigate and resolve this production login issue. 
       Let me start by using the incident-analysis skill..."

Tool: Skill(skill="incident-analysis")
Result: [SKILL.md content with workflow overview and MANDATORY FIRST STEP]
```

**Turn 2-3: Phase 1 - Triage**
```
Agent: "Let me start by reading the Phase 1 triage instructions and creating a task list..."

Tool: Read(.claude/skills/incident-analysis/phases/triage.md)
Result: [Instructions for gathering metrics, assessing severity, creating incident]

Tool: TodoWrite(todos=[6 phase tasks])
Tool: get_system_metrics(incident_type="authentication")
Tool: verify_health()
Tool: create_incident(severity="High", title="Production Login Failure...", ...)

Agent Summary:
"Phase 1 Complete - Triage Summary:
 - Incident ID: INC-2024-8986
 - Severity: HIGH
 - System Status: Degraded
 - Anomaly: Metrics healthy but auth failing
 
 Now moving to Phase 2: Investigation..."
```

**Turn 4-5: Phase 2 - Investigation**
```
Tool: Read(phases/investigation.md)
Tool: analyze_logs(timeframe="1h", incident_type="authentication")
Tool: analyze_logs(timeframe="24h", filter="error")

Agent Summary:
"Investigation Findings:
 - Low error rate (3/12,543 entries)
 - Hypotheses (ranked):
   1. Auth service specific issue (90%)
   2. Session/token management (60%)
   3. DB connection pool (40%)
 
 Let me proceed to Phase 3 for deeper root cause analysis..."
```

**Turns 6-20: Phases 3-6**
- Phase 3: Read `rca.md`, run `root_cause_analysis()`, provide RCA summary
- Phase 4: Read `remediation.md`, plan fix strategy, provide plan summary
- Phase 5: Read `execution.md`, execute remediation, verify health, provide execution summary
- Phase 6: Read `documentation.md`, document resolution, notify team

**Final Result:**
- ✅ All 6 phases completed
- ✅ All 6 todos marked completed
- ✅ Incident resolved with full audit trail
- ✅ Structured summaries at each phase transition

---

### Example: Log Analytics Skill (Standalone)

**User Prompt:**
```
"Analyze logs for incident INC-2025-001 from the last hour. 
I need error patterns, service breakdown, and anomaly detection."
```

**What Claude Does:**

**Turn 1: Skill Invocation**
```
Agent: "I'll analyze the logs for incident INC-2025-001 using the log-analytics skill..."

Tool: Skill(skill="log-analytics")
Result: [SKILL.md content with 3-phase workflow]
```

**Turn 2-3: Phase 1 - Data Fetch**
```
Tool: Read(.claude/skills/log-analytics/phases/data-fetch.md)

// Agent calls MCP tool to fetch logs from log-analytics server (port 9003)
Tool: mcp__log-analytics__get_raw_logs(
  incident_id="INC-2025-001", 
  timeframe="1h",
  service_filter="all"
)

// MCP server GENERATES 1200 realistic log entries on-the-fly
Result: {
  "incident_id": "INC-2025-001",
  "timeframe": "1h",
  "total_entries": 1200,
  "summary": {
    "errors": 36,
    "warnings": 84,
    "info": 1080,
    "error_rate_percent": 3.0
  },
  "logs": [
    {
      "timestamp": "2025-11-28T17:30:44.608219",
      "level": "ERROR",
      "service": "auth-service",
      "message": "Authentication failed: token validation timeout",
      "endpoint": "/api/v1/login",
      "response_time_ms": 5000,
      "error_code": "AUTH_TIMEOUT"
    },
    // ... 1199 more entries
  ]
}

// Agent saves the fetched data to local file
Tool: Write(file="analytics/incident_logs.json", content={raw logs from MCP})
Result: "File created successfully at: analytics/incident_logs.json"

Agent Summary:
"Phase 1 Complete - Data Fetch:
 - ✅ Fetched 1200 log entries from MCP server (port 9003)
 - ✅ Saved to analytics/incident_logs.json
 - Total logs: 1200
 - Error rate: 3.0%
 - Primary error codes: AUTH_TIMEOUT (30), REDIS_TIMEOUT (15)
 
 Moving to Phase 2: Code Generation..."
```

**Turn 4-5: Phase 2 - Code Generation**
```
Tool: Read(phases/code-generation.md)

Agent: "Based on the log structure, I'll generate a Python script to analyze:
- Error patterns by type and service
- Time-series distribution
- Performance metrics (P95, P99)
- Anomaly detection for high error rates"

Tool: Write(file="analytics/parse_logs_20251128_170000.py", content={GENERATED PYTHON CODE})

Agent shows the generated code:
```python
#!/usr/bin/env python3
import json
from datetime import datetime
from collections import Counter, defaultdict

def analyze_logs(data: dict) -> dict:
    logs = data['logs']
    error_logs = [log for log in logs if log['level'] == 'ERROR']
    error_codes = Counter([log.get('error_code', 'UNKNOWN') for log in error_logs])
    
    # Time-series analysis
    errors_by_hour = defaultdict(int)
    for log in error_logs:
        hour = datetime.fromisoformat(log['timestamp']).hour
        errors_by_hour[hour] += 1
    
    # Performance metrics
    response_times = [log['response_time_ms'] for log in logs if 'response_time_ms' in log]
    response_times.sort()
    p95 = response_times[int(len(response_times) * 0.95)]
    
    return {
        "total_logs": len(logs),
        "error_rate_percent": (len(error_logs) / len(logs)) * 100,
        "top_errors": error_codes.most_common(10),
        "p95_response_time_ms": p95,
        "anomalies": []  # Detected anomalies
    }
```

Phase 2 Complete - Code Generation:
 - Script: analytics/parse_logs_20251128_170000.py
 - Analyzes: errors, time-series, performance, anomalies
 
 Moving to Phase 3: Analysis Execution..."
```

**Turn 6-7: Phase 3 - Analysis Execution**
```
Tool: Read(phases/analysis-execution.md)
Tool: execute_analysis_script(script_path="analytics/parse_logs_20251128_170000.py")
Result: {
  "total_logs": 1200,
  "error_rate_percent": 3.75,
  "top_errors": [
    {"code": "AUTH_TIMEOUT", "count": 30},
    {"code": "REDIS_TIMEOUT", "count": 15}
  ],
  "p95_response_time_ms": 850,
  "anomalies": [
    {"type": "high_error_rate", "service": "auth-service", "error_rate_percent": 6.25}
  ]
}

Agent Analysis:
"Phase 3 Complete - Analysis Execution:

KEY INSIGHTS:
1. Primary Error: AUTH_TIMEOUT (30 occurrences, 66% of errors)
2. Secondary Error: REDIS_TIMEOUT (15 occurrences, 33% of errors)
3. Most Affected Service: auth-service (6.25% error rate)
4. Performance Impact: P95 response time 850ms (acceptable)

ROOT CAUSE HYPOTHESIS (85% confidence):
Redis connection pool exhaustion is causing session validation timeouts,
which cascade to authentication failures in the auth-service.

RECOMMENDED ACTIONS:
- Immediate: Restart Redis connection pool, monitor recovery
- Short-term: Increase Redis connection pool size
- Long-term: Implement connection pool monitoring alerts"

Tool: Write(file="analytics/analysis_results_20251128_170000.json", content={results})
```

**Final Result:**
- ✅ 3 phases completed
- ✅ 3 files generated in `analytics/`:
  - `incident_logs.json` - 1200 log entries fetched from MCP server
  - `parse_logs_20251128_170000.py` - 348 lines of generated Python code
  - `analysis_results_20251128_170000.json` - Structured analysis output
- ✅ Root cause hypothesis with 85% confidence
- ✅ Actionable recommendations provided
- ✅ Reusable analysis script for similar incidents

**Key Data Flow:**
```
MCP Server (port 9003)          Agent                    File System
─────────────────────          ─────                    ───────────
                               
get_raw_logs() generates        Agent calls              
1200 log entries    ──────────> mcp__log-analytics__    
on-the-fly                      get_raw_logs()
                                     │
                                     ▼
                               Agent receives JSON       
                               with 1200 entries
                                     │
                                     ▼
                               Write tool     ──────────> analytics/
                               saves logs     🔒 SECURE   incident_logs.json
                                              (NOT /tmp/)
                                     │
                                     ▼
                               Generate Python ──────────> analytics/
                               analysis code   🔒 SECURE   parse_logs_*.py
                                              (NOT /tmp/)
                                     │
                                     ▼
                               Execute script ──────────> analytics/
                               save results    🔒 SECURE   analysis_results_*.json
                                              (NOT /tmp/)
```

**🔒 Security Note:**
All sensitive files (logs, scripts, results) MUST be saved to `analytics/` within the secure project workspace. 
Saving to `/tmp/` or `/private/tmp/` is **FORBIDDEN** - these directories are accessible to other processes.

**Important:** If `analytics/incident_logs.json` is deleted, the workflow will re-fetch the data from the MCP server automatically!

---

### Example: Composable Skills (log-analytics invoked by incident-analysis)

**Scenario:** During Phase 2 (Investigation) of incident-analysis, if logs exceed 500 entries, the agent can invoke the log-analytics skill for deeper analysis:

```
[incident-analysis Phase 2: Investigation]
Tool: analyze_logs(timeframe="1h")
Result: {1200 log entries returned}

Agent: "The log data is extensive (1200 entries). I'll use the log-analytics skill 
       for detailed pattern analysis..."

Tool: Skill(skill="log-analytics")
[log-analytics runs its 3-phase workflow]
[Returns detailed analysis results]

Agent: "Based on the log-analytics skill results, I can now proceed with 
       high-confidence hypotheses for the incident-analysis workflow..."

[incident-analysis continues to Phase 3: RCA with enhanced insights]
```

This demonstrates **composable skills** - one skill invoking another for specialized analysis.

---

## 🔧 Critical Requirements

### Claude Code CLI Version

**Required:** Claude Code CLI **2.0.55 or later**

Earlier versions (like 2.0.10) do not include the `Skill` tool, causing:
- ❌ Skills not being discovered
- ❌ SKILL.md files not being loaded
- ❌ Progressive disclosure not working
- ❌ Agent relying on its own knowledge instead of following phase files

**Verification:**
```bash
claude --version  # Should show 2.0.55 or higher

# If outdated:
claude update
```

After upgrading, the `Skill` tool appears at position 14 in the tools list, and Skills are properly discovered and invoked.

## Common Pitfalls

### ❌ Outdated CLI Version

**Problem:** Using Claude Code CLI < 2.0.55
**Symptom:** No `Skill` tool in available tools list
**Fix:** `claude update`

### ❌ Wrong setting_sources

**Problem:** `setting_sources=["project"]` only
**Fix:** `setting_sources=["user", "project"]`

### ❌ Insufficient max_turns

**Problem:** `max_turns=20` (workflow hits limit before completion)
**Fix:** `max_turns=100` (allows full 6-phase completion)

## The Complete Stack

```
User Prompt
    ↓
Claude Agent SDK (query function)
    ↓
┌─────────────────────────────────────┐
│ Claude Model (Sonnet 4.5)          │
│ - Reads Agent Skills                │
│ - Follows Skill instructions        │
│ - Invokes Skills autonomously       │
│ - Calls MCP tools explicitly        │
│ - Generates Python code dynamically │
└─────────────────────────────────────┘
    ↓                         ↓
Skills (.claude/)         MCP Servers
- incident-analysis      - Monitoring (9001)
  (6 phases)             - Workflow (9002)
- log-analytics          - Log Analytics (9003)
  (code generation)
```

## Running the Project

### 1. Start MCP Servers
```bash
./scripts/start-servers.sh
```
This starts:
- Monitoring & Analysis on port 9001
- Workflow Orchestration on port 9002
- Log Analytics on port 9003

### 2. Run the Agent
```bash
python demos/run_scenario.py
```

### 3. What Happens
1. Agent SDK loads Skills from `.claude/skills/` (incident-analysis, log-analytics)
2. Agent SDK connects to MCP servers via SSE (ports 9001, 9002, 9003)
3. User prompt is sent to Claude
4. Claude:
   - Matches prompt to appropriate Skill (incident-analysis or log-analytics)
   - Reads SKILL.md to understand the workflow
   - Reads phase files progressively using Read tool
   - Calls MCP tools as instructed by phase files
   - Generates Python code if using log-analytics skill
   - Provides structured summaries at each phase transition
5. Results stream back with progressive disclosure
6. Task completed autonomously with full audit trail

## Files Structure

```
ClaudeSkillsSDK/
├── .claude/
│   └── skills/
│       ├── incident-analysis/               ← Incident Response Skill
│       │   ├── SKILL.md                     ← Main skill definition
│       │   ├── phases/                      ← Progressive disclosure
│       │   │   ├── triage.md
│       │   │   ├── investigation.md
│       │   │   ├── rca.md
│       │   │   ├── remediation.md
│       │   │   ├── execution.md
│       │   │   └── documentation.md
│       │   └── tools/                       ← Tool documentation
│       │
│       └── log-analytics/                   ← Log Analytics Skill
│           ├── SKILL.md                     ← Main skill definition
│           └── phases/                      ← Progressive disclosure
│               ├── data-fetch.md
│               ├── code-generation.md
│               └── analysis-execution.md
│
├── mcp-servers/                             ← MCP Tools (FastMCP)
│   ├── monitoring-analysis-server.py        (port 9001)
│   ├── workflow-orchestration-server.py     (port 9002)
│   └── log-analytics-server.py              (port 9003)
│
├── claude-agent/
│   ├── agent.py                             ← Agent SDK integration
│   └── utils/
│       └── todo_tracker.py                  ← Progress tracking
│
├── web_ui.py                                ← Web UI (localhost:8000)
│
├── demos/
│   └── run_scenario.py                      ← CLI demo runner
│
├── scripts/
│   ├── start-servers.sh                     ← Start MCP servers
│   └── run-web-ui.sh                        ← Start Web UI
│
├── logs/                                    ← Session logs (JSON lines)
│   └── agent_session_*.log
│
└── requirements.txt
```

## Dependencies

```txt
claude-agent-sdk>=0.1.10  # Agent SDK with Skills support (verified working)
fastmcp>=0.1.0            # FastMCP server framework
mcp>=1.0.0                # MCP protocol SDK
fastapi>=0.115.0          # Web UI framework
uvicorn>=0.32.0           # ASGI server
rich>=13.9.0              # Terminal output
python-dotenv>=1.0.0      # Environment management
```

**CLI Requirement:**
- Claude Code CLI >= 2.0.55 (includes `Skill` tool)

## Summary

**Agent Skills = High-level workflows (SKILL.md files)**
- How to think about problems
- Multi-step processes
- Best practices
- Model-invoked autonomously

**MCP Tools = Low-level actions (FastMCP servers)**
- What Claude can actually do
- System integrations
- Data operations
- Called explicitly by Claude

**Claude Agent SDK = Orchestration layer**
- Loads Skills from filesystem
- Connects to MCP servers
- Runs agentic loop
- Manages permissions
- Streams results

Together: Powerful autonomous agents that think systematically (Skills) and act effectively (MCP Tools)! 🚀

