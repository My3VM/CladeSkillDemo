#!/usr/bin/env python3
"""
Simple Web UI for Claude Agent Demo
Left: Incident input and agent conversation
Right: Live Todo tracker and tool execution results
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import agent types for message handling
from claude_agent_sdk import AssistantMessage, UserMessage, ToolUseBlock, ToolResultBlock

# Import the actual agent
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "claude-agent"))
from agent import ClaudeAgent

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


class IncidentRequest(BaseModel):
    description: str


async def broadcast_message(message: Dict[str, Any]):
    """Broadcast message to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the main UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Incident Response Agent</title>
    <!-- Markdown parser -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #0f172a;
            color: #e2e8f0;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        header p {
            margin-top: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.95rem;
        }
        
        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .left-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            border-right: 2px solid #334155;
            background: #1e293b;
        }
        
        .right-panel {
            width: 480px;
            display: flex;
            flex-direction: column;
            background: #0f172a;
        }
        
        .panel-header {
            padding: 1rem 1.5rem;
            background: #1e293b;
            border-bottom: 2px solid #334155;
            font-weight: 600;
            font-size: 0.95rem;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .conversation {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
        }
        
        .message {
            margin-bottom: 1.25rem;
            padding: 1rem 1.25rem;
            border-radius: 0.75rem;
            line-height: 1.6;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            background: #334155;
            border-left: 4px solid #667eea;
        }
        
        .message.assistant {
            background: #1e293b;
            border-left: 4px solid #10b981;
        }
        
        /* Markdown styling for assistant messages */
        .message-content h1, .message-content h2, .message-content h3 {
            margin-top: 1em;
            margin-bottom: 0.5em;
            color: #f1f5f9;
        }
        
        .message-content h1 { font-size: 1.5em; border-bottom: 2px solid #10b981; padding-bottom: 0.3em; }
        .message-content h2 { font-size: 1.3em; color: #a7f3d0; }
        .message-content h3 { font-size: 1.1em; color: #6ee7b7; }
        
        .message-content ul, .message-content ol {
            margin-left: 1.5em;
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }
        
        .message-content li {
            margin-bottom: 0.3em;
            line-height: 1.6;
        }
        
        .message-content code {
            background: #0f172a;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #fbbf24;
        }
        
        .message-content pre {
            background: #0f172a;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            margin: 0.5em 0;
        }
        
        .message-content pre code {
            background: none;
            padding: 0;
        }
        
        .message-content blockquote {
            border-left: 3px solid #10b981;
            padding-left: 1em;
            margin: 0.5em 0;
            color: #cbd5e1;
        }
        
        .message-content strong {
            color: #f1f5f9;
            font-weight: 600;
        }
        
        .message-content p {
            margin-bottom: 0.75em;
            line-height: 1.6;
        }
        
        .message-content a {
            color: #60a5fa;
            text-decoration: none;
        }
        
        .message-content a:hover {
            text-decoration: underline;
        }
        
        .message.tool {
            background: #172033;
            border-left: 4px solid #f59e0b;
            font-size: 0.9rem;
        }
        
        .message.system {
            background: #1a1f2e;
            border-left: 4px solid #8b5cf6;
            font-style: italic;
            color: #a78bfa;
        }
        
        .message-label {
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.8;
        }
        
        .input-area {
            padding: 1.5rem;
            background: #1e293b;
            border-top: 2px solid #334155;
        }
        
        .input-group {
            display: flex;
            gap: 0.75rem;
        }
        
        #incidentInput {
            flex: 1;
            padding: 0.875rem 1.125rem;
            background: #0f172a;
            border: 2px solid #334155;
            border-radius: 0.5rem;
            color: #e2e8f0;
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s;
        }
        
        #incidentInput:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            padding: 0.875rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 0.5rem;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.95rem;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .todo-container, .tools-container {
            flex: 1;
            overflow-y: auto;
            padding: 1.25rem;
        }
        
        .todo-item {
            padding: 0.875rem 1rem;
            margin-bottom: 0.75rem;
            background: #1e293b;
            border-radius: 0.5rem;
            border-left: 3px solid #475569;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            transition: all 0.2s;
        }
        
        .todo-item:hover {
            background: #27364b;
        }
        
        .todo-item.completed {
            border-left-color: #10b981;
            opacity: 0.7;
        }
        
        .todo-item.in_progress {
            border-left-color: #f59e0b;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .todo-icon {
            font-size: 1.25rem;
            flex-shrink: 0;
        }
        
        .todo-text {
            flex: 1;
            font-size: 0.9rem;
        }
        
        .tool-exec {
            padding: 1rem;
            margin-bottom: 1rem;
            background: #1e293b;
            border-radius: 0.5rem;
            border-left: 3px solid #f59e0b;
            font-size: 0.875rem;
            animation: slideIn 0.3s ease-out;
        }
        
        .tool-name {
            font-weight: 700;
            color: #fbbf24;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .tool-result {
            color: #94a3b8;
            font-family: 'Monaco', 'Courier New', monospace;
            white-space: pre-wrap;
            margin-top: 0.5rem;
            padding: 0.75rem;
            background: #0f172a;
            border-radius: 0.375rem;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        .status-indicator.connected {
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
        }
        
        .status-indicator.disconnected {
            background: #ef4444;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem 1.5rem;
            color: #64748b;
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
    </style>
</head>
<body>
    <header>
        <h1>🤖 Claude Incident Response Agent</h1>
        <p>Autonomous incident investigation with progressive disclosure & MCP tools</p>
    </header>
    
    <div class="container">
        <div class="left-panel">
            <div class="panel-header">
                <span class="status-indicator connected" id="statusIndicator"></span>
                Agent Conversation
            </div>
            <div class="conversation" id="conversation">
                <div class="empty-state">
                    <div class="empty-state-icon">💬</div>
                    <p>Describe an incident to start the investigation</p>
                </div>
            </div>
            <div class="input-area">
                <div class="input-group">
                    <input 
                        type="text" 
                        id="incidentInput" 
                        placeholder="e.g., Production API is slow, error rate elevated, users complaining..."
                        autocomplete="off"
                    />
                    <button id="submitBtn" onclick="submitIncident()">Investigate</button>
                </div>
            </div>
        </div>
        
        <div class="right-panel">
            <div class="panel-header">📋 Todo Progress</div>
            <div class="todo-container" id="todoContainer">
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <p>Tasks will appear here</p>
                </div>
            </div>
            
            <div class="panel-header">
                🔧 Tool Executions
                <span id="toolCount" style="font-size: 0.9em; opacity: 0.8; margin-left: 0.5rem;">(0)</span>
            </div>
            <div class="tools-container" id="toolsContainer">
                <div class="empty-state">
                    <div class="empty-state-icon">⚙️</div>
                    <p>Tool calls will appear here</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let toolExecutionCount = 0;
        const conversation = document.getElementById('conversation');
        const todoContainer = document.getElementById('todoContainer');
        const toolsContainer = document.getElementById('toolsContainer');
        const toolCount = document.getElementById('toolCount');
        const incidentInput = document.getElementById('incidentInput');
        const submitBtn = document.getElementById('submitBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                statusIndicator.className = 'status-indicator connected';
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                statusIndicator.className = 'status-indicator disconnected';
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        function handleMessage(data) {
            switch(data.type) {
                case 'conversation':
                    addConversationMessage(data.role, data.content);
                    break;
                case 'todo_update':
                    updateTodos(data.todos);
                    break;
                case 'tool_execution':
                    // Only increment counter when result is null (initial call)
                    addToolExecution(data.tool_name, data.input, data.result, data.result === null);
                    break;
                case 'system':
                    addSystemMessage(data.content);
                    break;
            }
        }
        
        function addConversationMessage(role, content) {
            if (conversation.querySelector('.empty-state')) {
                conversation.innerHTML = '';
            }
            
            const message = document.createElement('div');
            message.className = `message ${role}`;
            
            const label = document.createElement('div');
            label.className = 'message-label';
            label.textContent = role === 'user' ? '👤 You' : '🤖 Claude Agent';
            
            const text = document.createElement('div');
            text.className = 'message-content';
            // Render markdown for assistant messages
            if (role === 'assistant') {
                text.innerHTML = marked.parse(content);
            } else {
                text.textContent = content;
            }
            
            message.appendChild(label);
            message.appendChild(text);
            conversation.appendChild(message);
            conversation.scrollTop = conversation.scrollHeight;
        }
        
        function addSystemMessage(content) {
            if (conversation.querySelector('.empty-state')) {
                conversation.innerHTML = '';
            }
            
            const message = document.createElement('div');
            message.className = 'message system';
            
            const label = document.createElement('div');
            label.className = 'message-label';
            label.textContent = '⚡ System';
            
            const text = document.createElement('div');
            text.textContent = content;
            
            message.appendChild(label);
            message.appendChild(text);
            conversation.appendChild(message);
            conversation.scrollTop = conversation.scrollHeight;
        }
        
        function updateTodos(todos) {
            if (todoContainer.querySelector('.empty-state')) {
                todoContainer.innerHTML = '';
            }
            
            todoContainer.innerHTML = '';
            todos.forEach(todo => {
                const item = document.createElement('div');
                item.className = `todo-item ${todo.status}`;
                
                const icon = document.createElement('div');
                icon.className = 'todo-icon';
                icon.textContent = getStatusIcon(todo.status);
                
                const text = document.createElement('div');
                text.className = 'todo-text';
                text.textContent = todo.content;
                
                item.appendChild(icon);
                item.appendChild(text);
                todoContainer.appendChild(item);
            });
        }
        
        function getStatusIcon(status) {
            switch(status) {
                case 'completed': return '✅';
                case 'in_progress': return '🔧';
                case 'cancelled': return '❌';
                default: return '⏳';
            }
        }
        
        function addToolExecution(toolName, input, result, incrementCounter = true) {
            if (toolsContainer.querySelector('.empty-state')) {
                toolsContainer.innerHTML = '';
            }
            
            // Only increment counter for new tool calls, not results
            if (incrementCounter) {
                toolExecutionCount++;
                toolCount.textContent = `(${toolExecutionCount})`;
            }
            
            const exec = document.createElement('div');
            exec.className = 'tool-exec';
            
            const name = document.createElement('div');
            name.className = 'tool-name';
            name.innerHTML = `⚙️ ${toolName}`;
            
            const resultDiv = document.createElement('div');
            resultDiv.className = 'tool-result';
            resultDiv.textContent = typeof result === 'string' ? result : JSON.stringify(result, null, 2);
            
            exec.appendChild(name);
            if (result) {
                exec.appendChild(resultDiv);
            }
            
            toolsContainer.insertBefore(exec, toolsContainer.firstChild);
        }
        
        function submitIncident() {
            const description = incidentInput.value.trim();
            if (!description) return;
            
            submitBtn.disabled = true;
            incidentInput.disabled = true;
            
            ws.send(JSON.stringify({
                type: 'incident',
                description: description
            }));
            
            incidentInput.value = '';
        }
        
        incidentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitIncident();
            }
        });
        
        connectWebSocket();
    </script>
</body>
</html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['type'] == 'incident':
                # Start query processing
                await handle_query(data['description'])
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def handle_query(description: str):
    """
    Handle user query with live streaming.
    This is a DUMB UI - just calls agent.handle_query() and streams responses to browser.
    """
    
    # Set Bedrock environment variable
    os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
    
    # Send initial message
    await broadcast_message({
        'type': 'conversation',
        'role': 'user',
        'content': description
    })
    
    await broadcast_message({
        'type': 'system',
        'content': '🚀 Claude Agent starting investigation...'
    })
    
    # Create agent instance (all logic is in agent.py - includes logging)
    agent = ClaudeAgent()
    
    # Track tool calls by ID (to match results properly)
    tool_calls = {}
    
    # Callback function to handle each message from the agent
    async def message_callback(message, todo_tracker):
        
        # Update todos in UI
        if todo_tracker.process_message(message):
            await broadcast_message({
                'type': 'todo_update',
                'todos': todo_tracker.todos
            })
        
        # Handle assistant messages
        if isinstance(message, AssistantMessage):
            text_content = []
            for block in message.content:
                if hasattr(block, 'text'):
                    text_content.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    # Skip TodoWrite entirely (shown in todo_update instead)
                    if block.name != 'TodoWrite':
                        tool_calls[block.id] = {
                            'name': block.name,
                            'input': block.input
                        }
                        await broadcast_message({
                            'type': 'tool_execution',
                            'tool_name': block.name,
                            'input': block.input,
                            'result': None
                        })
            
            if text_content:
                await broadcast_message({
                    'type': 'conversation',
                    'role': 'assistant',
                    'content': '\n'.join(text_content)
                })
        
        # Handle user messages (tool results)
        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    # Match result to tool call by ID (skip if TodoWrite)
                    tool_call = tool_calls.get(block.tool_use_id)
                    if tool_call:
                        result = str(block.content)[:500] if len(str(block.content)) > 500 else block.content
                        await broadcast_message({
                            'type': 'tool_execution',
                            'tool_name': tool_call['name'],
                            'input': tool_call['input'],
                            'result': result
                        })
                        # Clean up
                        del tool_calls[block.tool_use_id]
    
    # Call the agent (all the real work happens here!)
    await agent.handle_query(description, callback=message_callback)
    
    # Done!
    await broadcast_message({
        'type': 'system',
        'content': "✅ Investigation complete!"
    })


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting Claude Agent Web UI")
    print("="*60)
    print("\n📍 Open your browser to: http://localhost:8000")
    print("⚡ Make sure MCP servers are running on ports 9001 & 9002\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

