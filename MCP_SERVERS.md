# MCP Servers Architecture

## Overview

This project uses **FastMCP** with **streamable HTTP transport** for MCP servers, enabling real-time communication with the Claude Agent SDK.

## Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Claude Agent SDK                                    │
│  - query() function                                              │
│  - ClaudeAgentOptions                                            │
│  - permission_mode: 'bypassPermissions'                          │
└──────────┬──────────────┬────────────────┬──────────────────────┘
           │              │                │
   SSE     │              │ SSE            │ SSE
(port 9001)│              │ (port 9002)    │ (port 9003)
           │              │                │
┌──────────▼─────┐  ┌─────▼───────────┐ ┌─▼──────────────┐
│ Monitoring &   │  │ Workflow        │ │ Log Analytics  │
│ Analysis       │  │ Orchestration   │ │ Server         │
│ Server         │  │ Server          │ │                │
│ FastMCP        │  │ FastMCP         │ │ FastMCP        │
│ Port: 9001     │  │ Port: 9002      │ │ Port: 9003     │
└────────────────┘  └─────────────────┘ └────────────────┘
```

## MCP Servers

### 1. Monitoring & Analysis Server (Port 9001)

**Location:** `mcp-servers/monitoring-analysis-server.py`

**Endpoint:** `http://127.0.0.1:9001/mcp`

**Tools:**
- `get_system_metrics()` - Retrieve current system metrics
- `analyze_logs()` - Analyze application logs for patterns
- `root_cause_analysis()` - Perform deep RCA
- `verify_health()` - Verify system health status

### 2. Workflow Orchestration Server (Port 9002)

**Location:** `mcp-servers/workflow-orchestration-server.py`

**Endpoint:** `http://127.0.0.1:9002/mcp`

**Tools:**
- `create_incident()` - Create incident tickets
- `execute_remediation()` - Execute remediation steps
- `document_resolution()` - Document incident resolution
- `notify_team()` - Send team notifications

### 3. Log Analytics Server (Port 9003)

**Location:** `mcp-servers/log-analytics-server.py`

**Endpoint:** `http://127.0.0.1:9003/mcp`

**Tools:**
- `get_raw_logs(incident_id, timeframe, service_filter)` - Fetch 1000+ log entries as JSON
- `execute_analysis_script(script_path, log_data_path)` - Run generated Python analysis code

**Purpose:** Enables the `log-analytics` Agent Skill to generate and execute custom Python code for parsing large log datasets, detecting error patterns, calculating statistics, and identifying anomalies.

**🔒 Security:**
- Agent is enforced (via phase files) to save all files to `analytics/` directory
- Forbidden: `/tmp/`, `/private/tmp/` - these expose sensitive log data to other processes
- All analysis artifacts (logs, scripts, results) remain in secure project workspace

## FastMCP Pattern

All servers follow this pattern:

```python
from mcp.server.fastmcp import FastMCP

# Create server
mcp_server = FastMCP("server-name", host="0.0.0.0", port=PORT)

# Define tools with decorator
@mcp_server.tool()
async def my_tool(param: str) -> str:
    """Tool description"""
    # Tool logic
    return json.dumps(result)

# Run with streamable HTTP
if __name__ == "__main__":
    mcp_server.run(transport="streamable-http")
```

## Agent Configuration

The Claude Agent SDK connects via SSE:

```python
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

options = ClaudeAgentOptions(
    system_prompt=base_system_prompt,
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    permission_mode='bypassPermissions',
    mcp_servers=mcp_servers,
    max_turns=20
)

async for message in query(prompt=user_prompt, options=options):
    # Process streaming messages
    pass
```

## Starting the Servers

### Manual Start

```bash
# Terminal 1: Monitoring & Analysis
python mcp-servers/monitoring-analysis-server.py

# Terminal 2: Workflow Orchestration  
python mcp-servers/workflow-orchestration-server.py

# Terminal 3: Log Analytics
python mcp-servers/log-analytics-server.py
```

### Automated Start

```bash
# Start all three servers in background
./scripts/start-servers.sh
```

This script:
- ✅ Activates virtual environment
- ✅ Checks for port conflicts
- ✅ Starts all three servers (ports 9001, 9002, 9003)
- ✅ Provides cleanup on Ctrl+C

## Endpoints

### Monitoring & Analysis

- **Main:** `http://127.0.0.1:9001/mcp`
- **SSE:** `http://127.0.0.1:9001/sse`
- **Health:** `http://127.0.0.1:9001/health`

### Workflow Orchestration

- **Main:** `http://127.0.0.1:9002/mcp`
- **SSE:** `http://127.0.0.1:9002/sse`
- **Health:** `http://127.0.0.1:9002/health`

### Log Analytics

- **Main:** `http://127.0.0.1:9003/mcp`
- **SSE:** `http://127.0.0.1:9003/sse`
- **Health:** `http://127.0.0.1:9003/health`

## Testing

### Test Server Availability

```bash
# Check if servers are running
curl http://127.0.0.1:9001/health
curl http://127.0.0.1:9002/health
curl http://127.0.0.1:9003/health
```

### Test Tool Invocation

```bash
# Via MCP protocol (requires MCP client)
# The Claude Agent SDK handles this automatically
```

## Key Features

1. **Streamable HTTP Transport**
   - Real-time bidirectional communication
   - Server-Sent Events (SSE) for streaming
   - No stdio complexity

2. **FastMCP Framework**
   - Simple `@mcp_server.tool()` decorator
   - Automatic schema generation
   - Built-in logging

3. **Autonomous Execution**
   - `permission_mode='bypassPermissions'`
   - Agent runs without human approval
   - Full audit trail maintained

4. **Progressive Disclosure**
   - Streaming messages from Claude
   - Real-time tool execution visibility
   - Step-by-step reasoning display

## Dependencies

```txt
mcp>=1.0.0                # MCP Protocol SDK
fastmcp>=0.1.0            # FastMCP server framework
claude-agent-sdk>=0.1.0   # Claude Agent SDK
```

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port
lsof -ti:9001 | xargs kill -9
lsof -ti:9002 | xargs kill -9
lsof -ti:9003 | xargs kill -9
```

### Server Won't Start

```bash
# Check logs
python mcp-servers/monitoring-analysis/server.py
# Look for error messages
```

### Agent Can't Connect

```bash
# Verify servers are running
curl http://127.0.0.1:9001/sse
curl http://127.0.0.1:9002/sse
curl http://127.0.0.1:9003/sse

# Check firewall settings
# Ensure ports 9001, 9002, and 9003 are open
```

## Production Considerations

### Security

- [ ] Add authentication/authorization
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add input validation

### Monitoring

- [ ] Add metrics collection
- [ ] Implement health checks
- [ ] Log aggregation
- [ ] Error tracking

### Scalability

- [ ] Load balancing
- [ ] Horizontal scaling
- [ ] Caching layer
- [ ] Connection pooling

---

**Ready to run?**

```bash
# 1. Start MCP servers
./scripts/start-servers.sh

# 2. In another terminal, run the agent
python demos/run_scenario.py
```

