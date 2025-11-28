#!/usr/bin/env python3
"""Log Analytics MCP Server - Streamable HTTP transport on port 9003."""

import asyncio
from mcp.server.fastmcp import FastMCP
from typing import Optional
import json
import logging
import sys
import subprocess
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP Server
mcp_server = FastMCP("log-analytics", host="127.0.0.1", port=9003)


@mcp_server.tool()
async def get_raw_logs(
    incident_id: str,
    timeframe: str = "1h",
    service_filter: str = "all"
) -> str:
    """
    Fetch raw log data for analysis. Returns 1000+ log entries as JSON.
    Use this to get large datasets for pattern analysis.
    
    Args:
        incident_id: Incident ID to fetch logs for
        timeframe: Time range (e.g., '1h', '24h', '7d')
        service_filter: Optional service name filter
    """
    logger.info(f"Tool called: get_raw_logs(incident_id={incident_id}, timeframe={timeframe}, service_filter={service_filter})")
    
    log_entries = []
    
    # Generate 1200 log entries with realistic patterns
    for i in range(1200):
        timestamp = datetime.now() - timedelta(minutes=i)
        
        # Create realistic log patterns
        if i % 40 == 0:  # Authentication timeout errors (~3%)
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "ERROR",
                "service": "auth-service",
                "message": "Authentication failed: token validation timeout",
                "user_id": f"user_{1000 + (i % 500)}",
                "endpoint": "/api/v1/login",
                "response_time_ms": 5000 + (i % 1000),
                "error_code": "AUTH_TIMEOUT",
                "stack_trace": "TimeoutError: Token validation exceeded 5s limit"
            }
        
        elif i % 80 == 0:  # Session store Redis errors (~1.25%)
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "ERROR",
                "service": "session-store",
                "message": "Redis connection failed: ETIMEDOUT",
                "endpoint": "/api/v1/session/validate",
                "response_time_ms": 3000 + (i % 500),
                "error_code": "REDIS_TIMEOUT",
                "redis_host": "redis-cluster-01.internal",
                "stack_trace": "ConnectionError: Redis connection pool exhausted"
            }
        
        elif i % 150 == 0:  # Database connection pool errors (~0.67%)
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "ERROR",
                "service": "api-gateway",
                "message": "Database query timeout: connection pool exhausted",
                "endpoint": "/api/v1/users/profile",
                "response_time_ms": 10000,
                "error_code": "DB_POOL_EXHAUSTED",
                "db_pool_size": 100,
                "db_active_connections": 100
            }
        
        elif i % 200 == 0:  # Payment gateway errors (~0.5%)
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "ERROR",
                "service": "payment-service",
                "message": "Payment processing failed: gateway timeout",
                "endpoint": "/api/v1/payments/process",
                "response_time_ms": 15000,
                "error_code": "PAYMENT_GATEWAY_TIMEOUT",
                "amount_usd": 99.99,
                "payment_provider": "stripe"
            }
        
        elif i % 10 == 0:  # Slow requests (10%)
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "WARN",
                "service": "api-gateway",
                "message": "Request processing slow",
                "endpoint": "/api/v1/users",
                "response_time_ms": 800 + (i % 200),
                "user_id": f"user_{i % 1000}"
            }
        
        else:  # Normal traffic (majority)
            endpoints = [
                "/api/v1/users",
                "/api/v1/products",
                "/api/v1/orders",
                "/api/v1/search",
                "/api/v1/recommendations"
            ]
            services = ["api-gateway", "product-service", "user-service", "search-service"]
            
            entry = {
                "timestamp": timestamp.isoformat(),
                "level": "INFO",
                "service": services[i % len(services)],
                "message": "Request processed successfully",
                "endpoint": endpoints[i % len(endpoints)],
                "response_time_ms": 50 + (i % 100),
                "user_id": f"user_{i % 1000}",
                "status_code": 200
            }
        
        log_entries.append(entry)
    
    # Calculate summary stats
    error_count = len([e for e in log_entries if e["level"] == "ERROR"])
    warn_count = len([e for e in log_entries if e["level"] == "WARN"])
    
    result = {
        "incident_id": incident_id,
        "timeframe": timeframe,
        "service_filter": service_filter,
        "total_entries": len(log_entries),
        "summary": {
            "errors": error_count,
            "warnings": warn_count,
            "info": len(log_entries) - error_count - warn_count,
            "error_rate_percent": round((error_count / len(log_entries)) * 100, 2)
        },
        "logs": log_entries,
        "metadata": {
            "fetched_at": datetime.now().isoformat(),
            "note": "This is RAW log data. Generate Python code to analyze patterns, count errors, detect anomalies, and extract insights."
        }
    }
    
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def execute_analysis_script(
    script_path: str,
    log_data_path: str = "analytics/incident_logs.json"
) -> str:
    """
    Execute a Python analysis script against log data.
    
    Runs the generated analysis code and returns results.
    
    Args:
        script_path: Path to the Python script to execute
        log_data_path: Path to JSON file containing log data
    """
    logger.info(f"Tool called: execute_analysis_script(script_path={script_path}, log_data_path={log_data_path})")
    
    try:
        # Execute the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = {
                "status": "success",
                "script": script_path,
                "output": result.stdout,
                "execution_time": "< 30s"
            }
        else:
            output = {
                "status": "error",
                "script": script_path,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        
        return json.dumps(output, indent=2)
    
    except subprocess.TimeoutExpired:
        return json.dumps({
            "status": "error",
            "error": "Script execution timeout (30s limit)",
            "script": script_path
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "script": script_path
        }, indent=2)


if __name__ == "__main__":
    logger.info("Starting Log Analytics MCP Server on port 9003...")
    mcp_server.run(transport="streamable-http")
