#!/usr/bin/env python3
"""
Run demonstration scenarios

Usage:
    python demos/run_scenario.py                    # Run default scenario
    python demos/run_scenario.py --compare          # Run comparison
    python demos/run_scenario.py --scenario memory_leak
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import agent - handle hyphen in directory name by importing directly
import importlib.util
agent_path = Path(__file__).parent.parent / "claude-agent" / "agent.py"
spec = importlib.util.spec_from_file_location("claude_agent.agent", agent_path)
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
ClaudeAgent = agent_module.ClaudeAgent
from rich.console import Console

console = Console()


SCENARIOS = {
    "connection_leak": {
        "description": "Our production API seems slow and users are complaining. Error rate is elevated. Please investigate and resolve.",
        "incident_type": "connection_leak",
        "title": "Database Connection Leak"
    },
    "memory_leak": {
        "description": "System memory usage is climbing steadily. Application becoming unresponsive. Need immediate investigation.",
        "incident_type": "memory_leak",
        "title": "Memory Leak Investigation"
    },
    "unknown": {
        "description": "Something is wrong with production. Users reporting issues but not clear what. Please investigate.",
        "incident_type": "connection_leak",  # Will discover this
        "title": "Unknown Incident - Progressive Discovery"
    }
}


async def run_agent_scenario(scenario_name: str = "connection_leak"):
    """Run Claude agent scenario"""
    if scenario_name not in SCENARIOS:
        console.print(f"[red]Unknown scenario: {scenario_name}[/red]")
        console.print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        return
    
    scenario = SCENARIOS[scenario_name]
    
    console.print("\n" + "═" * 60)
    console.print(f"🎯 Scenario: {scenario['title']}", style="bold green")
    console.print("═" * 60)
    
    try:
        agent = ClaudeAgent()
        await agent.handle_query(scenario["description"])
    except Exception as e:
        console.print(f"[red]Error running scenario: {e}[/red]")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run incident response demo scenarios")
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS.keys()),
        default="connection_leak",
        help="Scenario to run"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios"
    )
    
    args = parser.parse_args()
    
    if args.list:
        console.print("\n[bold]Available Scenarios:[/bold]\n")
        for name, scenario in SCENARIOS.items():
            console.print(f"  • [cyan]{name}[/cyan]: {scenario['title']}")
        console.print()
        return
    
    try:
        asyncio.run(run_agent_scenario(args.scenario))
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()

