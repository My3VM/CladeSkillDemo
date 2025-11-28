"""
Todo Tracker for Agentic Execution

Tracks and displays todo items as they're created and updated during SDK query execution.
"""

from typing import List, Dict, Any
from claude_agent_sdk import AssistantMessage, ToolUseBlock


class TodoTracker:
    """
    Tracks todo items during agentic execution.
    
    Monitors SDK query messages for TodoWrite tool uses and displays progress.
    """
    
    def __init__(self):
        self.todos: List[Dict[str, Any]] = []
        self.enabled = True
    
    def update_todos(self, todos: List[Dict[str, Any]]) -> None:
        """
        Update the todo list with deduplication logic.
        Merges new todos with existing ones, preventing duplicate phases.
        
        Args:
            todos: List of todo items with 'id', 'content', 'status' fields
        """
        if not todos:
            return
        
        # Extract phase name from content (e.g., "PHASE 1: ..." -> "PHASE 1")
        def get_phase_key(todo: Dict[str, Any]) -> str:
            content = todo.get("content", "")
            # Extract phase prefix (PHASE 1, PHASE 2, etc.)
            if ":" in content:
                phase_part = content.split(":")[0].strip()
                # Normalize (remove extra spaces, make uppercase)
                return phase_part.upper()
            # If no phase prefix, use content as key
            return content[:50]  # Use first 50 chars as key
        
        # If we have existing todos, merge intelligently
        if self.todos:
            # Create a map of existing todos by phase key
            existing_map = {}
            for todo in self.todos:
                key = get_phase_key(todo)
                existing_map[key] = todo
            
            # Merge new todos with existing ones
            merged = []
            seen_keys = set()
            
            for new_todo in todos:
                key = get_phase_key(new_todo)
                
                if key in existing_map:
                    # Update existing todo with new status/content if provided
                    existing = existing_map[key]
                    # Preserve existing status unless new one is more advanced
                    status_priority = {"completed": 3, "in_progress": 2, "pending": 1, "cancelled": 0}
                    existing_status_priority = status_priority.get(existing.get("status", "pending"), 1)
                    new_status_priority = status_priority.get(new_todo.get("status", "pending"), 1)
                    
                    # Update if new status is more advanced or if content is more specific
                    if new_status_priority > existing_status_priority:
                        existing["status"] = new_todo.get("status", existing.get("status"))
                    
                    # Update content/activeForm if new one is more specific
                    if "activeForm" in new_todo and len(new_todo.get("activeForm", "")) > len(existing.get("activeForm", "")):
                        existing["activeForm"] = new_todo.get("activeForm")
                    if len(new_todo.get("content", "")) > len(existing.get("content", "")):
                        existing["content"] = new_todo.get("content", existing.get("content"))
                    
                    merged.append(existing)
                    seen_keys.add(key)
                else:
                    # New todo, add it
                    merged.append(new_todo)
                    seen_keys.add(key)
            
            # Add any existing todos that weren't in the new list (preserve them)
            for key, existing in existing_map.items():
                if key not in seen_keys:
                    merged.append(existing)
            
            self.todos = merged
        else:
            # First time, just set the todos
            self.todos = todos
        
        if self.enabled:
            self.display_progress()
    
    def display_progress(self, return_string: bool = False) -> str:
        """
        Display current todo progress with icons and status.
        
        Args:
            return_string: If True, return formatted string instead of printing
        
        Returns:
            Formatted progress string if return_string=True, otherwise None
        """
        if not self.todos:
            return "" if return_string else None
        
        completed = len([t for t in self.todos if t.get("status") == "completed"])
        in_progress = len([t for t in self.todos if t.get("status") == "in_progress"])
        total = len(self.todos)
        completion_pct = (completed / total * 100) if total > 0 else 0
        
        # Build output string
        lines = []
        lines.append("\n" + "🔔" + "=" * 68 + "🔔")
        lines.append(f"📋 TODO PROGRESS: {completed}/{total} completed ({completion_pct:.0f}%)")
        
        # Alert based on progress
        if completion_pct == 100:
            lines.append("🎉✨ ALL TASKS COMPLETED! ✨🎉")
        elif completion_pct >= 75:
            lines.append("🚀 Almost done! Keep going!")
        elif completion_pct >= 50:
            lines.append("💪 Halfway there!")
        elif in_progress > 0:
            lines.append(f"🔧 Currently working on: {in_progress} task(s)")
        else:
            lines.append("⏸️  Ready to start!")
        
        lines.append("🔔" + "=" * 68 + "🔔")
        
        for i, todo in enumerate(self.todos, 1):
            status = todo.get("status", "pending")
            
            # Choose icon based on status
            if status == "completed":
                icon = "✅"
            elif status == "in_progress":
                icon = "🔧⚡"
            elif status == "cancelled":
                icon = "❌"
            else:
                icon = "⏳"
            
            # Use activeForm for in_progress items, content otherwise
            if status == "in_progress" and "activeForm" in todo:
                text = todo["activeForm"]
            else:
                text = todo.get("content", "Unknown task")
            
            lines.append(f"{i}. {icon} {text}")
        
        lines.append("🔔" + "=" * 68 + "🔔\n")
        
        output = "\n".join(lines)
        
        if return_string:
            return output
        else:
            print(output)
            return None
    
    def process_message(self, message: Any) -> bool:
        """
        Process a message from the SDK query stream.
        
        Checks for TodoWrite tool uses and updates the todo list.
        
        Args:
            message: Message from SDK query stream (AssistantMessage, UserMessage, etc.)
        
        Returns:
            True if todos were updated, False otherwise
        """
        # Check if it's an AssistantMessage with content blocks
        if isinstance(message, AssistantMessage) and hasattr(message, 'content'):
            for block in message.content:
                # Check for ToolUseBlock instances
                if isinstance(block, ToolUseBlock):
                    # Check if it's a TodoWrite tool
                    if block.name == 'TodoWrite' or block.name == 'todo_write':
                        if hasattr(block, 'input') and 'todos' in block.input:
                            self.update_todos(block.input['todos'])
                            return True
        
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of todo progress.
        
        Returns:
            Dictionary with completion stats
        """
        if not self.todos:
            return {
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0,
                'cancelled': 0,
                'completion_rate': 0.0
            }
        
        completed = len([t for t in self.todos if t.get("status") == "completed"])
        in_progress = len([t for t in self.todos if t.get("status") == "in_progress"])
        pending = len([t for t in self.todos if t.get("status") == "pending"])
        cancelled = len([t for t in self.todos if t.get("status") == "cancelled"])
        total = len(self.todos)
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'pending': pending,
            'cancelled': cancelled,
            'completion_rate': (completed / total * 100) if total > 0 else 0.0
        }

