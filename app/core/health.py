from datetime import datetime
import psutil
import os
from typing import Dict, Any

class HealthCheck:
    def __init__(self):
        self.start_time = datetime.now()

    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Application metrics
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime,
                "system": {
                    "cpu_usage_percent": cpu_percent,
                    "memory": {
                        "total_mb": memory.total / (1024 * 1024),
                        "available_mb": memory.available / (1024 * 1024),
                        "used_percent": memory.percent
                    },
                    "disk": {
                        "total_gb": disk.total / (1024 * 1024 * 1024),
                        "free_gb": disk.free / (1024 * 1024 * 1024),
                        "used_percent": disk.percent
                    }
                },
                "environment": {
                    "python_version": os.environ.get("PYTHON_VERSION", "unknown"),
                    "node_version": os.environ.get("NODE_VERSION", "unknown"),
                    "port": os.environ.get("PORT", "unknown")
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }