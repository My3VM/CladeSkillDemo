# Quick Start Guide

Get the incident response agent running in 5 minutes!

## ⚙️ Prerequisites

**Required:** Claude Code CLI **2.0.55 or later**

```bash
# Check version
claude --version  # Must show 2.0.55+

# Upgrade if needed
claude update
```

## 🚀 Quick Setup

```bash
# 1. Setup Python environment
python3 -m venv cenv
source cenv/bin/activate
pip install -r requirements.txt

# 2. Start MCP servers (Terminal 1)
./scripts/start-servers.sh

# 3. Start Web UI (Terminal 2)
./scripts/run-web-ui.sh

# 4. Open browser to http://localhost:8000
```

That's it! ✨

## 💻 CLI Mode (Alternative)

If you prefer CLI over Web UI:

```bash
# Start MCP servers (Terminal 1)
./scripts/start-servers.sh

# Run incident scenario (Terminal 2)
source cenv/bin/activate
python demos/run_scenario.py --scenario connection_leak
```

## 🎯 What You'll See

### Web UI (http://localhost:8000)
- **Real-time Chat:** Conversation with the agent
- **Todo Progress:** Live updates as phases complete (6/6)
- **Tool Executions:** MCP tool calls with inputs/outputs
- **Structured Workflow:** 6 phases from triage to documentation

### Execution Flow
1. **Skill Invocation:** Agent detects incident and invokes `incident-analysis` skill
2. **Progressive Disclosure:** Reads phase files sequentially:
   - Phase 1: Triage (gather metrics, create incident)
   - Phase 2: Investigation (analyze logs, form hypotheses)
   - Phase 3: RCA (confirm root cause with 90%+ confidence)
   - Phase 4: Remediation Planning (design fix strategy)
   - Phase 5: Execution (execute and verify remediation)
   - Phase 6: Documentation (document and notify)
3. **Phase Transitions:** Structured summaries before each phase
4. **MCP Tool Calls:** `get_system_metrics`, `analyze_logs`, `execute_remediation`, etc.
5. **Complete Resolution:** Full audit trail in logs

## 🎬 Available Scenarios

```bash
# Connection leak (default)
python demos/run_scenario.py --scenario connection_leak

# Memory leak
python demos/run_scenario.py --scenario memory_leak

# Unknown issue
python demos/run_scenario.py --scenario unknown

# List all scenarios
python demos/run_scenario.py --list
```

## 🔧 Viewing Logs

All sessions are logged with full audit trail:

```bash
# View latest session
ls -lt logs/*.log | head -1

# Analyze with jq
cat logs/agent_session_*.log | jq '.type, .data.tool_name' -c

# Check for Skill tool usage
grep '"tool_name": "Skill"' logs/agent_session_*.log

# View phase transitions
grep -i "phase.*complete" logs/agent_session_*.log
```

## Next Steps

- 📖 Read [DEMO_GUIDE.md](./DEMO_GUIDE.md) for presentation tips
- 🏗️ Read [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- 🔧 Read [SETUP.md](./SETUP.md) for advanced setup
- 💡 Customize for your use case

## 🐛 Troubleshooting

**Skill tool not working?**
```bash
# Check Claude CLI version (must be 2.0.55+)
claude --version

# Upgrade if needed
claude update
```

**MCP servers not starting?**
```bash
# Check if ports 9001 and 9002 are free
lsof -i:9001
lsof -i:9002

# Kill if needed
kill $(lsof -t -i:9001)
kill $(lsof -t -i:9002)
```

**Web UI showing port 8000 in use?**
```bash
# Kill process using port 8000
kill $(lsof -t -i:8000)

# Restart web UI
./scripts/run-web-ui.sh
```

**Python dependencies issues?**
```bash
source cenv/bin/activate
pip install --upgrade claude-agent-sdk
pip install -r requirements.txt
```

## 📖 Quick Reference

| Command | What it does |
|---------|-------------|
| `claude --version` | Check CLI version (need 2.0.55+) |
| `claude update` | Upgrade Claude CLI |
| `./scripts/start-servers.sh` | Start MCP servers (ports 9001, 9002) |
| `./scripts/run-web-ui.sh` | Start Web UI (port 8000) |
| `python demos/run_scenario.py` | Run CLI mode |
| `python demos/run_scenario.py --list` | List scenarios |

## 📚 Next Steps

- 📖 Read [README.md](./README.md) for project overview
- 🏗️ Read [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- 🎯 Read [SKILLS_README.md](./SKILLS_README.md) for Skills deep-dive
- 🔧 Read [MCP_SERVERS.md](./MCP_SERVERS.md) for MCP tool details

---

**Ready? Ensure CLI 2.0.55+, then:**
```bash
source cenv/bin/activate
./scripts/start-servers.sh  # Terminal 1
./scripts/run-web-ui.sh     # Terminal 2
# Open http://localhost:8000
```

