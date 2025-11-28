# Claude Agent SDK Demo: Skills + MCP

> Autonomous incident response using Claude Agent SDK with Skills and Model Context Protocol

## 🎯 What This Demonstrates

Transform incident response from a **45-minute manual process** into a **3-5 minute autonomous resolution** using:

- **Agent Skills** (`.claude/skills/` - filesystem-based instructions with progressive disclosure)
- **MCP Servers** (FastMCP - tool integrations)
- **Claude Agent SDK** (Autonomous agentic execution)
- **Structured Workflows** (6-phase incident response with phase transition summaries)

## ⚙️ Prerequisites

**Required:** Claude Code CLI **2.0.55 or later** (for Skill tool support)

```bash
# Check version
claude --version  # Should show 2.0.55 or higher

# Upgrade if needed
claude update
```

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/My3VM/CladeSkillDemo.git
cd CladeSkillDemo
```

**Note:** Throughout the documentation, paths like `/Users/<username>/CladeSkillDemo/analytics/` are shown with `<username>` as a placeholder. Replace `<username>` with your actual username. For example:

## ⚡ Quick Start

### Option 1: Web UI (Recommended)

```bash
# 1. Setup
python3 -m venv cenv
source cenv/bin/activate
pip install -r requirements.txt

# 2. Start MCP servers (Terminal 1)
./scripts/start-servers.sh

# 3. Start Web UI (Terminal 2)
./scripts/run-web-ui.sh

# 4. Open browser to http://localhost:8000
```

### Option 2: CLI Demo

```bash
# 1. Setup
python3 -m venv cenv
source cenv/bin/activate
pip install -r requirements.txt

# 2. Start MCP servers (Terminal 1)
./scripts/start-servers.sh

# 3. Run demo (Terminal 2)
python demos/run_scenario.py
```

## 📁 Project Structure

```
ClaudeSkillsSDK/
├── .claude/skills/              # Agent Skills (SKILL.md files)
│   ├── incident-analysis/       # 6-phase incident response workflow
│   └── log-analytics/           # Code generation for log analysis
│
├── mcp-servers/                           # FastMCP servers
│   ├── monitoring-analysis-server.py     # Port 9001
│   ├── workflow-orchestration-server.py  # Port 9002
│   └── log-analytics-server.py           # Port 9003
│
├── claude-agent/
│   ├── agent.py                 # Agent SDK integration
│   └── utils/
│       └── todo_tracker.py      # Live progress tracking
│
├── analytics/                   # Generated log analysis outputs
│
├── web_ui.py                    # Web UI (localhost:8000)
│
├── demos/
│   └── run_scenario.py          # CLI demo runner
│
└── scripts/
    ├── setup.sh
    ├── run-demo.sh
    ├── run-web-ui.sh            # Web UI launcher
    └── start-servers.sh
```

## 🔑 Key Concepts

### Agent Skills (.claude/skills/)

Filesystem-based instructions that Claude autonomously invokes:

```markdown
---
name: incident-analysis
description: Analyze and resolve production incidents
---

# Incident Analysis Skill
[Instructions for Claude...]
```

**When Claude sees:** "Our API is slow, investigate and resolve"  
**It automatically uses:** `incident-analysis` Skill

### MCP Servers

FastMCP tools that Claude calls explicitly:

```python
@mcp_server.tool()
async def get_system_metrics(incident_type: Optional[str] = None) -> str:
    """Get current system metrics"""
    return json.dumps(metrics)
```

### Agent SDK Integration

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    cwd=str(project_root),                      # .claude/skills/ location
    setting_sources=["user", "project"],        # Load Skills from filesystem
    mcp_servers=mcp_servers,                    # Connect to MCP servers
    allowed_tools=["Skill", "Read", "TodoWrite", "Bash"],  # Enable core tools
    permission_mode='bypassPermissions',        # Autonomous execution
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    max_turns=100                               # Allow full workflow completion
)

async for message in query(prompt=user_prompt, options=options):
    # Agent autonomously:
    # 1. Invokes Skill tool for incident-analysis
    # 2. Reads phase files progressively
    # 3. Calls MCP tools as instructed
    # 4. Tracks progress with TodoWrite
    print(message)
```

## 🎬 Demo Scenarios

### Connection Leak (Default)
```bash
python demos/run_scenario.py --scenario connection_leak
```

### Memory Leak
```bash
python demos/run_scenario.py --scenario memory_leak
```


## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architecture
- **[SKILLS_README.md](SKILLS_README.md)** - Agent Skills guide
- **[MCP_SERVERS.md](MCP_SERVERS.md)** - MCP server details
- **[QUICKSTART.md](QUICKSTART.md)** - 2-minute quick start

## 🔧 How It Works

1. **User prompt:** "Production system is degraded. Users can't log in."
2. **Claude invokes:** `Skill` tool with `incident-analysis` skill
3. **Progressive disclosure:** Reads phase files sequentially:
   - Phase 1: `phases/triage.md` → Gathers metrics, creates incident
   - Phase 2: `phases/investigation.md` → Analyzes logs, forms hypotheses
   - Phase 3: `phases/rca.md` → Confirms root cause with 90%+ confidence
   - Phase 4: `phases/remediation.md` → Plans fix strategy
   - Phase 5: `phases/execution.md` → Executes and verifies remediation
   - Phase 6: `phases/documentation.md` → Documents and notifies team
4. **Structured transitions:** Provides summary before each phase transition
5. **MCP tool calls:** `get_system_metrics()`, `analyze_logs()`, `execute_remediation()`, etc.
6. **Autonomous resolution:** Complete incident lifecycle with audit trail

## 💡 Key Differentiators

### 🎯 Skills = High-level workflows (how to think)
- **Progressive Disclosure:** Phase instructions revealed incrementally
- **Structured Transitions:** Mandated summaries between phases
- **Domain Expertise:** Codified incident response best practices
- **Autonomous Invocation:** Model-invoked based on description matching
- **Audit Trail:** Each phase creates documented decision points

### 🔧 MCP Tools = Low-level actions (what to do)
- **System Integrations:** Monitoring, logging, remediation
- **Data Operations:** Metrics collection, log analysis
- **Concrete Actions:** Health checks, incident creation, notifications
- **Explicit Invocation:** Called by Claude as instructed by Skills

### 📋 TodoWrite = Progress tracking
- **Real-time Updates:** Phase completion tracking
- **Structured Task List:** 6 todos matching 6 phases
- **Status Transitions:** pending → in_progress → completed
- **Completion Rate:** Visual progress indicator

## 🔒 Security

### File Path Enforcement

**CRITICAL:** The `log-analytics` skill enforces secure file paths to prevent sensitive data exposure.

**✅ Allowed:**
- `analytics/incident_logs.json` - Raw log data
- `analytics/parse_logs_*.py` - Generated analysis scripts
- `analytics/analysis_results_*.json` - Analysis outputs

**❌ Forbidden:**
- `/tmp/` - Temporary files accessible to other processes
- `/private/tmp/` - Same security risk
- Any path outside the project workspace

**Why:** Incident logs contain sensitive production data. Saving to `/tmp/` exposes this data to other system processes, creating a security vulnerability.

**Enforcement:** Each phase file in `.claude/skills/log-analytics/phases/` explicitly warns against temp directory usage and requires verification of file paths.

## 🚀 Extending the Demo

### Add a New Skill

```bash
mkdir -p .claude/skills/your-skill
```

Create `.claude/skills/your-skill/SKILL.md`:
```markdown
---
name: your-skill
description: When to use this skill
---

# Your Skill
Instructions for Claude...
```

### Add MCP Tools

In `mcp-servers/*/server.py`:
```python
@mcp_server.tool()
async def your_tool(param: str) -> str:
    """Tool description"""
    return json.dumps(result)
```

## 📖 Resources

- [Agent Skills Docs](https://platform.claude.com/docs/en/agent-sdk/skills)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)

## 📄 License

MIT License - see LICENSE file

---

**Built to demonstrate autonomous AI agents with Claude Skills + MCP** 🚀
