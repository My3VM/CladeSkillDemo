#!/usr/bin/env python3
"""Monitoring & Analysis MCP Server - Streamable HTTP transport on port 9001."""

import asyncio
from mcp.server.fastmcp import FastMCP
from typing import Any, Optional
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP Server
mcp_server = FastMCP("monitoring-analysis", host="127.0.0.1", port=9001)


@mcp_server.tool()
async def get_system_metrics(incident_type: Optional[str] = None) -> str:
    """Get current system metrics including API response time, error rate, CPU, memory, and database connections"""
    logger.info(f"Tool called: get_system_metrics with incident_type={incident_type}")
    
    try:
        if incident_type == "connection_leak":
            metrics = {
                "api_response_time_ms": 2300,
                "error_rate_percent": 8.5,
                "cpu_percent": 45,
                "memory_percent": 78,
                "database_connections": 95,
                "database_max_connections": 100,
                "timestamp": datetime.now().isoformat(),
                "status": "degraded"
            }
        else:
            metrics = {
                "api_response_time_ms": 200,
                "error_rate_percent": 0.1,
                "cpu_percent": 45,
                "memory_percent": 65,
                "database_connections": 50,
                "database_max_connections": 100,
                "timestamp": datetime.now().isoformat(),
                "status": "healthy"
            }
        
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp_server.tool()
async def analyze_logs(timeframe: str, filter: Optional[str] = None, incident_type: Optional[str] = None) -> str:
    """Analyze application logs for error patterns, anomalies, and correlations"""
    logger.info(f"Tool called: analyze_logs with timeframe={timeframe}, filter={filter}")
    
    try:
        if incident_type == "connection_leak":
            result = {
                "timeframe": timeframe,
                "filter": filter or "all",
                "total_entries": 45237,
                "errors_found": 1247,
                "error_types": {
                    "connection_timeout": 1247,
                    "slow_query": 23,
                    "rate_limit": 5
                },
                "pattern": {
                    "started": "23 minutes ago",
                    "correlation": "deployment_v2.3.1",
                    "affected_service": "UserProfileService",
                    "error_message": "Database connection timeout after 30s"
                }
            }
        else:
            result = {
                "timeframe": timeframe,
                "filter": filter or "all",
                "total_entries": 12543,
                "errors_found": 3,
                "status": "normal"
            }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp_server.tool()
async def root_cause_analysis(incident_type: str, deployment: Optional[str] = None) -> str:
    """Perform deep root cause analysis based on symptoms and context"""
    logger.info(f"Tool called: root_cause_analysis with incident_type={incident_type}, deployment={deployment}")
    
    try:
        if incident_type == "connection_leak" and deployment == "v2.3.1":
            result = {
                "root_cause_identified": True,
                "confidence": 95,
                "issue": {
                    "type": "connection_leak",
                    "component": "UserProfileService",
                    "file": "services/user_profile.py",
                    "line": 234,
                    "problem": "Missing connection.close() in error handling path",
                    "introduced_in": "v2.3.1",
                    "deployed_at": "2024-11-28T14:37:00Z",
                    "time_since_deploy": "23 minutes"
                },
                "evidence": [
                    "Connection pool exhaustion correlates with v2.3.1 deployment",
                    "Code review shows missing cleanup in error path",
                    "Error spike started exactly at deployment time"
                ]
            }
        else:
            result = {
                "root_cause_identified": False,
                "message": "Insufficient data for root cause analysis"
            }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp_server.tool()
async def verify_health(after_remediation: bool = False) -> str:
    """Verify overall system health and check if issues are resolved"""
    logger.info(f"Tool called: verify_health with after_remediation={after_remediation}")
    
    try:
        if after_remediation:
            result = {
                "status": "healthy",
                "checks": {
                    "api_response_time": {"value": 190, "baseline": 200, "status": "✅ healthy"},
                    "error_rate": {"value": 0.08, "baseline": 0.1, "status": "✅ healthy"},
                    "database_connections": {"value": 12, "max": 200, "status": "✅ healthy"}
                }
            }
        else:
            result = {"status": "degraded"}
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Monitoring & Analysis MCP Server on port 9001...")
    
    # Run FastMCP server with streamable HTTP async
    asyncio.run(mcp_server.run_streamable_http_async())
