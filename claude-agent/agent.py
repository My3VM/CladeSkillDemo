#!/usr/bin/env python3
"""
Claude Agent with Skills and MCP

Uses Claude Agent SDK with:
- Agent Skills (filesystem-based workflows)
- MCP Servers (decoupled tool providers)
- Autonomous execution
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, UserMessage, ToolUseBlock, ToolResultBlock

# Import TodoTracker from utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.todo_tracker import TodoTracker

load_dotenv()
os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
console = Console()


class ClaudeAgent:
    """Claude Agent with Skills + MCP for autonomous task execution"""
    
    def __init__(self):
        # Create logs directory
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"agent_session_{timestamp}.log"
        
        # Generic system prompt - let Skills handle specialized workflows
        self.system_prompt = """You are a helpful AI assistant with access to specialized skills and tools.

IMPORTANT: For ANY multi-step task (3+ steps):
1. ALWAYS use TodoWrite at the start to create a structured task list
2. Update TodoWrite as you progress (mark tasks as 'in_progress' then 'completed')
3. This applies whether using a Skill or just regular tools

When responding to user requests:
- Evaluate if there's a relevant Skill that matches the request (check Skill descriptions)
- If a Skill matches, invoke it to handle the request systematically
- If no Skill matches, use available tools to help with the task
- Always explain your reasoning and provide clear, helpful responses

Available capabilities:
- TodoWrite tool - USE THIS for tracking any multi-step task progress
- Agent Skills for specialized workflows (will be invoked automatically when relevant)
- MCP Tools for various operations (diagnostics, remediation, data access, etc.)"""
        
        # MCP servers (decoupled - they expose their own tools)
        self.mcp_servers = {
            'monitoring-analysis': {
                'type': 'http',
                'url': 'http://127.0.0.1:9001/mcp'
            },
            'workflow-orchestration': {
                'type': 'http',
                'url': 'http://127.0.0.1:9002/mcp'
            },
            'log-analytics': {
                'type': 'http',
                'url': 'http://127.0.0.1:9003/mcp'
            }
        }
    
    def _log_message(self, message_type: str, data: dict):
        """Log message to file (JSON lines format)"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': message_type,
            'data': data
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to log message: {e}[/yellow]")
    
    async def handle_query(self, user_query: str, callback=None):
        """
        Handle user query using Claude Agent SDK
        
        Args:
            user_query: The user's query/request
            callback: Optional async function called for each message (for web UI streaming)
                     If None, prints to console (CLI mode)
        
        Yields:
            Messages from the agent (when used as async generator)
        """
        
        # Log session start
        self._log_message('session_start', {
            'query': user_query,
            'log_file': str(self.log_file)
        })
        
        # Initialize todo tracker
        todo_tracker = TodoTracker()
        
        # Get project root for Skills
        project_root = Path(__file__).parent.parent
        
        # Configure Claude Agent SDK
        options = ClaudeAgentOptions(
            cwd=str(project_root),              # .claude/skills/ location
            setting_sources=["user", "project"], # Load Skills from user + project
            system_prompt=self.system_prompt,
            model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            permission_mode='bypassPermissions',
            mcp_servers=self.mcp_servers,       # MCP servers auto-expose their tools
            allowed_tools=["Skill", "Read", "TodoWrite", "Bash"],  # Enable Skills + TodoWrite
            # allowed_tools=[ "Write",]  # Enable Skill tool

            max_turns=100
        )
        
        # CLI mode - print to console
        if callback is None:
            console.print("\n" + "═" * 60, style="bold cyan")
            console.print("🤖 Claude Agent Starting...", style="bold green")
            console.print("═" * 60, style="bold cyan")
            console.print(f"\n{user_query}\n")
        
        # Run agent - SDK handles everything
        current_tool_call = {}
        tool_calls_summary = []
        
        async for message in query(
            prompt=user_query,
            options=options
        ):
            # Log all messages
            self._log_message('agent_message', {
                'message_type': type(message).__name__,
                'message': message
            })
            
            # Extract and log tool calls
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        tool_call_entry = {
                            'tool_name': block.name,
                            'input': block.input,
                            'id': block.id,
                            'timestamp': datetime.now().isoformat()
                        }
                        current_tool_call[block.id] = tool_call_entry
                        tool_calls_summary.append(tool_call_entry)
                        
                        self._log_message('tool_call', {
                            'tool_name': block.name,
                            'tool_id': block.id,
                            'input': block.input
                        })
            
            # Extract and log tool results
            if isinstance(message, UserMessage):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        tool_info = current_tool_call.get(block.tool_use_id, {})
                        
                        # Update summary with result
                        for entry in tool_calls_summary:
                            if entry.get('id') == block.tool_use_id:
                                entry['result'] = block.content
                                entry['is_error'] = block.is_error
                                entry['result_timestamp'] = datetime.now().isoformat()
                        
                        self._log_message('tool_result', {
                            'tool_name': tool_info.get('tool_name', 'unknown'),
                            'tool_id': block.tool_use_id,
                            'result': block.content,
                            'is_error': block.is_error
                        })
            
            # Track todos
            todo_tracker.process_message(message)
            
            # Either call callback (web UI) or print (CLI)
            if callback:
                await callback(message, todo_tracker)
            else:
                console.print(message)
        
        # Log session end with tool calls summary
        summary = todo_tracker.get_summary()
        self._log_message('session_end', {
            'todo_summary': summary,
            'total_tool_calls': len(tool_calls_summary),
            'tool_calls_summary': tool_calls_summary,
            'log_file': str(self.log_file)
        })
        
        # Display final summary (CLI mode only)
        if callback is None:
            console.print("\n" + "=" * 60)
            
            # Todo summary
            if summary['total'] > 0:
                console.print(f"📊 Todo Summary: {summary['completed']}/{summary['total']} completed ({summary['completion_rate']:.0f}%)")
            
            # Tool calls summary
            if tool_calls_summary:
                console.print(f"\n🔧 Tool Calls Executed: {len(tool_calls_summary)}")
                for i, call in enumerate(tool_calls_summary, 1):
                    status = "❌ ERROR" if call.get('is_error') else "✅"
                    console.print(f"  {i}. {status} {call['tool_name']}")
            
            console.print("=" * 60)


async def main():
    """Main entry point"""
    agent = ClaudeAgent()
        
    # ========================================
    # INCIDENT-ANALYSIS SKILL QUERIES
    # ========================================
    # (Match: "production incidents", "users reporting", "investigate and resolve")
    
    # user_query = "Our production API seems slow and users are complaining. Error rate is elevated. Please investigate and resolve."
    # user_query = "Database connections at 95/100 and response times spiking. Investigate the issue."
    # user_query = "Users reporting 500 errors during checkout. Fix this urgently."
    user_query = "Production system is degraded. Users can't log in."
    
    
    # ========================================
    # LOG-ANALYTICS SKILL QUERIES
    # ========================================
    # (Match: "generate Python code", "analyze large log datasets", "1000+ entries")
    
    # user_query = "Generate Python code to analyze logs for incident INC-2025-001. I need error counts, time-series patterns, and anomaly detection."
    # user_query = "I have 1000+ log entries. Write code to parse them, count errors by type, calculate response time percentiles, and detect anomalies."
    # user_query = "Create a Python script to analyze log patterns for the past 2 hours. Include error frequency, service breakdown, and statistical analysis."
    # user_query = "Analyze logs for incident INC-2025-001. Generate code to detect patterns, calculate error rates, and identify anomalies."
    # user_query = "Write Python code to parse 1200 log entries and provide detailed analytics on errors, response times, and service health."
    # user_query = "I have 1000+ log entries. Write code to parse them, count errors by type, calculate response time percentiles, and detect anomalies."
    
    # ========================================
    # GENERAL QUERIES (No skill invocation)
    # ========================================
    # user_query = "Explain how MCP servers work"
    # user_query = "Create a Python function that calculates fibonacci numbers"
    # user_query = "How many employees does Cisco have?"
    # user_query = "List all Python files in this project"
    
    await agent.handle_query(user_query)


if __name__ == "__main__":
    asyncio.run(main())
