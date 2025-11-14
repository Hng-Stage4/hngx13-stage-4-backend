#!/usr/bin/env python3
"""
Simple Template Service Test
Tests the service without database dependencies
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI
from datetime import datetime

# Create a simple test app without database
app = FastAPI(
    title="Template Service Test",
    description="Simple test without database dependencies",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Template Service is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "template-service",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {
            "database": "skipped",
            "redis": "skipped"
        }
    }

@app.get("/api/metrics")
async def metrics():
    return "# Template Service Metrics\ntemplate_service_uptime_seconds 1.0\n"

if __name__ == "__main__":
    import uvicorn
    print("Starting Template Service Test on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)