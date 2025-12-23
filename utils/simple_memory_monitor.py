"""
Simple Memory Monitor - Lightweight system memory tracking
Monitors RAM usage and triggers alerts on memory pressure
Author: Performance Optimization
Date: 2025-12-22
"""

import psutil
import threading
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Callable, List
from datetime import datetime, timedelta
from collections import deque
import json

logger = logging.getLogger(__name__)


class MemoryMetrics:
    """Track memory metrics over time"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.memory_readings: deque = deque(maxlen=window_size)
        self.timestamps: deque = deque(maxlen=window_size)
        self.peak_memory = 0.0
        self.peak_time = None
        self.alert_count = 0

    def record(self, memory_percent: float) -> None:
        """Record memory reading"""
        self.memory_readings.append(memory_percent)
        self.timestamps.append(datetime.now())

        if memory_percent > self.peak_memory:
            self.peak_memory = memory_percent
            self.peak_time = datetime.now()

    def get_average(self) -> float:
        """Get average memory usage"""
        return (sum(self.memory_readings) / len(self.memory_readings)
                if self.memory_readings else 0.0)

    def get_trend(self) -> str:
        """Get memory trend (increasing/decreasing/stable)"""
        if len(self.memory_readings) < 5:
            return "insufficient_data"

        recent = list(self.memory_readings)[-5:]
        avg_recent = sum(recent) / len(recent)

        older = list(self.memory_readings)[:-5]
        avg_older = sum(older) / len(older) if older else avg_recent

        if avg_recent > avg_older * 1.1:  # 10% increase
            return "increasing"
        elif avg_recent < avg_older * 0.9:  # 10% decrease
            return "decreasing"
        else:
            return "stable"

    def get_summary(self) -> Dict[str, any]:
        """Get metrics summary"""
        return {
            "current": f"{self.memory_readings[-1]:.1f}%" if self.memory_readings else "N/A",
            "average": f"{self.get_average():.1f}%",
            "peak": f"{self.peak_memory:.1f}%",
            "peak_time": self.peak_time.isoformat() if self.peak_time else None,
            "trend": self.get_trend(),
            "readings": len(self.memory_readings)
        }


class MemoryAlert:
    """Memory alert configuration and tracking"""

    def __init__(self, threshold_percent: float = 80.0, alert_callback: Optional[Callable] = None):
        self.threshold_percent = threshold_percent
        self.alert_callback = alert_callback
        self.last_alert_time = None
        self.alert_cooldown_seconds = 60  # Don't spam alerts

    def check(self, memory_percent: float) -> bool:
        """Check if alert should be triggered"""
        if memory_percent >= self.threshold_percent:
            now = datetime.now()
            if (self.last_alert_time is None or
                (now - self.last_alert_time).total_seconds() > self.alert_cooldown_seconds):
                self.last_alert_time = now
                if self.alert_callback:
                    self.alert_callback(memory_percent)
                return True
        return False


class SimpleMemoryMonitor:
    """
    Lightweight memory monitor for system RAM usage.

    Features:
    - Monitor memory usage every 5 minutes
    - Detect memory growth trends
    - Alert on high memory usage (>80% default)
    - Log metrics to file
    - Thread-safe background monitoring

    Usage:
        monitor = SimpleMemoryMonitor(check_interval_seconds=300)
        monitor.start()
        # ... do work ...
        monitor.print_stats()
        monitor.stop()
    """

    def __init__(
        self,
        check_interval_seconds: int = 300,
        alert_threshold_percent: float = 80.0,
        log_file: Optional[Path] = None
    ):
        """
        Initialize memory monitor.

        Args:
            check_interval_seconds: Interval between memory checks (default: 300s = 5 min)
            alert_threshold_percent: Alert when memory exceeds this % (default: 80%)
            log_file: Optional file to log metrics to
        """
        self.check_interval_seconds = check_interval_seconds
        self.alert_threshold_percent = alert_threshold_percent
        self.log_file = log_file or Path("/tmp/memory_monitor.log")

        self.metrics = MemoryMetrics()
        self.alert = MemoryAlert(
            threshold_percent=alert_threshold_percent,
            alert_callback=self._on_alert
        )

        self.running = False
        self.monitor_thread = None
        self.start_time = datetime.now()

    def _on_alert(self, memory_percent: float) -> None:
        """Alert callback"""
        message = (f"MEMORY ALERT: {memory_percent:.1f}% of RAM in use "
                  f"(threshold: {self.alert_threshold_percent:.0f}%)")
        logger.warning(message)
        self._log_event("ALERT", message)
        self.metrics.alert_count += 1

    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        while self.running:
            try:
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                self.metrics.record(memory_percent)
                self.alert.check(memory_percent)

                self._log_check(memory)

                time.sleep(self.check_interval_seconds)

            except Exception as e:
                logger.error(f"Memory monitor error: {e}")
                time.sleep(self.check_interval_seconds)

    def _log_check(self, memory: psutil.virtual_memory) -> None:
        """Log memory check result"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "percent": f"{memory.percent:.1f}",
                "used_mb": f"{memory.used / (1024 * 1024):.0f}",
                "available_mb": f"{memory.available / (1024 * 1024):.0f}",
                "total_mb": f"{memory.total / (1024 * 1024):.0f}",
                "trend": self.metrics.get_trend()
            }

            # Append to log file (JSON lines format)
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Error logging memory check: {e}")

    def _log_event(self, event_type: str, message: str) -> None:
        """Log an event"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "message": message
            }

            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error(f"Error logging event: {e}")

    def start(self) -> None:
        """Start background monitoring"""
        if self.running:
            logger.warning("Memory monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MemoryMonitor"
        )
        self.monitor_thread.start()

        logger.info(f"Memory monitor started (interval: {self.check_interval_seconds}s, "
                   f"alert threshold: {self.alert_threshold_percent:.0f}%, "
                   f"log: {self.log_file})")

        # Trigger initial check
        memory = psutil.virtual_memory()
        self.metrics.record(memory.percent)
        self._log_event("START", f"Memory monitor started")

    def stop(self) -> None:
        """Stop background monitoring"""
        if not self.running:
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("Memory monitor stopped")
        self._log_event("STOP", "Memory monitor stopped")

    def get_status(self) -> Dict[str, any]:
        """Get current memory status"""
        memory = psutil.virtual_memory()
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_percent": f"{memory.percent:.1f}%",
            "memory_used_mb": f"{memory.used / (1024 * 1024):.0f}",
            "memory_available_mb": f"{memory.available / (1024 * 1024):.0f}",
            "memory_total_mb": f"{memory.total / (1024 * 1024):.0f}",
            "status": "high" if memory.percent > 80 else "normal",
            "monitoring": self.running,
            "uptime": str(datetime.now() - self.start_time).split('.')[0]
        }

    def print_stats(self) -> None:
        """Print formatted statistics"""
        memory = psutil.virtual_memory()
        metrics = self.metrics.get_summary()
        status = self.get_status()

        print("\n" + "=" * 70)
        print("MEMORY MONITOR STATISTICS")
        print("=" * 70)
        print(f"Current Memory: {status['memory_percent']} "
              f"({status['memory_used_mb']}MB / {status['memory_total_mb']}MB)")
        print(f"Available: {status['memory_available_mb']}MB")
        print(f"Status: {status['status'].upper()}")
        print()
        print("METRICS")
        print("-" * 70)
        print(f"Average: {metrics['average']}")
        print(f"Peak: {metrics['peak']} at {metrics['peak_time']}")
        print(f"Trend: {metrics['trend'].upper()}")
        print(f"Readings: {metrics['readings']}")
        print(f"Alerts Triggered: {self.metrics.alert_count}")
        print()
        print(f"Monitoring: {status['monitoring']}")
        print(f"Uptime: {status['uptime']}")
        print(f"Log File: {self.log_file}")
        print("=" * 70 + "\n")

    def get_detailed_status(self) -> Dict[str, any]:
        """Get detailed status including process info"""
        memory = psutil.virtual_memory()

        # Get top memory consuming processes
        processes = psutil.process_iter(['pid', 'name', 'memory_percent'])
        top_processes = sorted(
            processes,
            key=lambda p: p.info['memory_percent'],
            reverse=True
        )[:5]

        return {
            "system_memory": {
                "percent": f"{memory.percent:.1f}%",
                "used_mb": f"{memory.used / (1024 * 1024):.0f}",
                "available_mb": f"{memory.available / (1024 * 1024):.0f}",
                "total_mb": f"{memory.total / (1024 * 1024):.0f}"
            },
            "metrics": self.metrics.get_summary(),
            "top_processes": [
                {
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "memory_percent": f"{p.info['memory_percent']:.1f}%"
                }
                for p in top_processes
            ]
        }


# Global monitor instance
_global_monitor: Optional[SimpleMemoryMonitor] = None


def get_monitor(
    check_interval_seconds: int = 300,
    alert_threshold_percent: float = 80.0,
    log_file: Optional[Path] = None
) -> SimpleMemoryMonitor:
    """
    Get or create global memory monitor instance.

    Args:
        check_interval_seconds: Interval between checks
        alert_threshold_percent: Alert threshold
        log_file: Log file path

    Returns:
        SimpleMemoryMonitor instance
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SimpleMemoryMonitor(
            check_interval_seconds=check_interval_seconds,
            alert_threshold_percent=alert_threshold_percent,
            log_file=log_file
        )
    return _global_monitor


def reset_monitor() -> None:
    """Reset global monitor instance"""
    global _global_monitor
    if _global_monitor is not None:
        _global_monitor.stop()
        _global_monitor = None
