#!/usr/bin/env python3
"""
Analytics Dashboard - Performance analytics and usage statistics
for AI Router application
"""

from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3


class AnalyticsDashboard:
    """Performance analytics and usage statistics"""

    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.conn = None

    def _get_connection(self):
        """Get database connection from session manager"""
        return sqlite3.connect(str(self.session_manager.db_path))

    def get_usage_statistics(self, days: int = 30) -> Dict:
        """Get usage stats for last N days"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        conn = self._get_connection()
        try:
            stats = conn.execute("""
                SELECT
                    COUNT(DISTINCT m.session_id) as total_sessions,
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN m.role = 'user' THEN 1 ELSE 0 END) as user_messages,
                    SUM(CASE WHEN m.role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
                    SUM(m.tokens_used) as total_tokens,
                    AVG(m.tokens_used) as avg_tokens_per_message
                FROM messages m
                JOIN sessions s ON m.session_id = s.session_id
                WHERE s.created_at >= ?
            """, (cutoff,)).fetchone()

            return {
                "total_sessions": stats[0] or 0,
                "total_messages": stats[1] or 0,
                "user_messages": stats[2] or 0,
                "assistant_messages": stats[3] or 0,
                "total_tokens": stats[4] or 0,
                "avg_tokens": stats[5] or 0
            }
        finally:
            conn.close()

    def get_model_usage(self, days: int = 30) -> List[Tuple[str, int]]:
        """Get usage count by model"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        conn = self._get_connection()
        try:
            results = conn.execute("""
                SELECT model_id, COUNT(*) as usage_count
                FROM sessions
                WHERE created_at >= ?
                GROUP BY model_id
                ORDER BY usage_count DESC
            """, (cutoff,)).fetchall()

            return results
        finally:
            conn.close()

    def get_daily_activity(self, days: int = 30) -> List[Tuple[str, int]]:
        """Get daily message counts for last N days"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        conn = self._get_connection()
        try:
            results = conn.execute("""
                SELECT
                    DATE(s.created_at) as date,
                    COUNT(m.message_id) as message_count
                FROM messages m
                JOIN sessions s ON m.session_id = s.session_id
                WHERE s.created_at >= ?
                GROUP BY DATE(s.created_at)
                ORDER BY date
            """, (cutoff,)).fetchall()

            return results
        finally:
            conn.close()

    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        conn = self._get_connection()
        try:
            result = conn.execute("""
                SELECT AVG(duration_seconds)
                FROM messages
                WHERE duration_seconds IS NOT NULL AND duration_seconds > 0
            """).fetchone()

            return result[0] if result and result[0] else 0.0
        finally:
            conn.close()

    def get_top_models_by_performance(self) -> List[Dict]:
        """Rank models by usage and success"""
        conn = self._get_connection()
        try:
            results = conn.execute("""
                SELECT
                    s.model_id,
                    s.model_name,
                    COUNT(DISTINCT s.session_id) as session_count,
                    COUNT(m.message_id) as message_count,
                    AVG(m.tokens_used) as avg_tokens,
                    SUM(m.tokens_used) as total_tokens,
                    AVG(m.duration_seconds) as avg_duration
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                GROUP BY s.model_id, s.model_name
                ORDER BY session_count DESC
            """).fetchall()

            return [
                {
                    'model_id': r[0],
                    'model_name': r[1],
                    'session_count': r[2] or 0,
                    'message_count': r[3] or 0,
                    'avg_tokens': r[4] or 0,
                    'total_tokens': r[5] or 0,
                    'avg_duration': r[6] or 0
                }
                for r in results
            ]
        finally:
            conn.close()

    def display_dashboard(self, days: int = 30):
        """Display complete analytics dashboard"""
        from datetime import datetime

        print(f"\n{'='*70}")
        print(f"  PERFORMANCE ANALYTICS DASHBOARD")
        print(f"  Period: Last {days} days")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        # Usage Statistics
        stats = self.get_usage_statistics(days)
        self._display_usage_stats(stats)

        # Model Usage Chart
        model_usage = self.get_model_usage(days)
        self._display_model_usage_chart(model_usage)

        # Daily Activity Chart
        daily = self.get_daily_activity(days)
        self._display_daily_activity_chart(daily, days)

        # Performance Metrics
        avg_response = self.get_avg_response_time()
        self._display_performance_metrics(avg_response)

        # Recommendations
        self._display_recommendations(stats, model_usage)

    def _display_usage_stats(self, stats: Dict):
        """Display usage statistics section"""
        print(f"USAGE STATISTICS")
        print(f"{'-'*70}")
        print(f"  Total Sessions:        {stats['total_sessions']:>10,}")
        print(f"  Total Messages:        {stats['total_messages']:>10,}")
        print(f"    |- User Messages:    {stats['user_messages']:>10,}")
        print(f"    +- AI Responses:     {stats['assistant_messages']:>10,}")
        print(f"  Total Tokens:          {stats['total_tokens']:>10,}")
        print(f"  Avg Tokens/Message:    {stats['avg_tokens']:>10,.1f}")
        print()

    def _display_model_usage_chart(self, model_usage: List[Tuple[str, int]]):
        """Display horizontal bar chart of model usage"""
        if not model_usage:
            print(f"MODEL USAGE: No data available\n")
            return

        print(f"MODEL USAGE")
        print(f"{'-'*70}")

        max_usage = max(count for _, count in model_usage)
        bar_width = 40
        total_sessions = sum(c for _, c in model_usage)

        for model_id, count in model_usage[:10]:  # Top 10
            bar_length = int((count / max_usage) * bar_width) if max_usage > 0 else 0
            bar = '#' * bar_length
            percent = (count / total_sessions) * 100 if total_sessions > 0 else 0

            model_name = model_id[:20]  # Truncate long names
            print(f"  {model_name:<20} {bar:<40} {count:>5} ({percent:>5.1f}%)")

        print()

    def _display_daily_activity_chart(self, daily: List[Tuple[str, int]], days: int):
        """Display daily activity sparkline"""
        if not daily:
            print(f"DAILY ACTIVITY: No data available\n")
            return

        print(f"DAILY ACTIVITY (Last {min(len(daily), days)} days)")
        print(f"{'-'*70}")

        if len(daily) == 0:
            print("  No activity recorded")
            print()
            return

        max_messages = max(count for _, count in daily) if daily else 1
        bar_height = 10

        # Create ASCII chart (vertical bars)
        # Show last 14 days if more than 14
        recent_days = daily[-14:] if len(daily) > 14 else daily

        for level in range(bar_height, 0, -1):
            line = "  "
            for date, count in recent_days:
                threshold = (level / bar_height) * max_messages
                if count >= threshold:
                    line += "#"
                else:
                    line += " "
            print(line)

        # X-axis labels (dates)
        print(f"  {'-' * len(recent_days)}")
        dates_line = "  "
        for date, _ in recent_days:
            # Extract day of month (last 2 chars of date)
            day = date[-2:] if len(date) >= 2 else date
            dates_line += day[-1]  # Just show last digit to fit
        print(dates_line)

        # Legend
        print(f"\n  Peak: {max_messages} messages/day")
        print()

    def _display_performance_metrics(self, avg_response: float):
        """Display performance metrics"""
        print(f"PERFORMANCE METRICS")
        print(f"{'-'*70}")
        print(f"  Avg Response Time:     {avg_response:>10.2f} seconds")
        print()

    def _display_recommendations(self, stats: Dict, model_usage: List):
        """Display AI-driven recommendations"""
        print(f"RECOMMENDATIONS")
        print(f"{'-'*70}")

        recommendations = []

        # Low usage recommendation
        if stats['total_sessions'] < 10:
            recommendations.append("Try exploring different models to find your favorites")

        # Token efficiency
        avg_tokens = stats.get('avg_tokens', 0)
        if avg_tokens > 5000:
            recommendations.append("Consider using context management to reduce token usage")

        # Model diversity
        if model_usage and len(model_usage) == 1:
            recommendations.append("Try model comparison mode to explore alternative models")

        # High usage celebration
        if stats['total_sessions'] > 50:
            recommendations.append("Great engagement! Consider exporting analytics for tracking")

        # Batch processing suggestion
        if stats['total_sessions'] > 100:
            recommendations.append("For repetitive tasks, consider batch processing workflows")

        if not recommendations:
            recommendations.append("Great usage patterns! Keep exploring AI Router features")

        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

        print()


def test_analytics_dashboard():
    """Test analytics dashboard with sample data"""
    from session_manager import SessionManager
    from pathlib import Path
    import tempfile
    import os

    # Create temporary database file (doesn't exist yet)
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = Path(temp_db.name)

    # Remove the empty file so SessionManager can create a fresh one
    os.unlink(db_path)

    # Copy schema.sql to parent directory temporarily
    schema_src = Path(__file__).parent / "schema.sql"
    temp_schema = db_path.parent / "schema.sql"

    if schema_src.exists():
        import shutil
        shutil.copy(schema_src, temp_schema)

    try:
        # Initialize session manager
        session_manager = SessionManager(db_path)

        # Create test sessions
        session1 = session_manager.create_session(
            'qwen3-coder-30b',
            'Qwen3 Coder 30B',
            'Test coding session'
        )

        session_manager.add_message(session1, 'user', 'Write a hello world function', tokens=50)
        session_manager.add_message(session1, 'assistant', 'def hello(): print("Hello")', tokens=150, duration=2.5)

        session2 = session_manager.create_session(
            'phi4-14b',
            'Phi-4 14B',
            'Math problem'
        )

        session_manager.add_message(session2, 'user', 'Calculate 2+2', tokens=30)
        session_manager.add_message(session2, 'assistant', 'The answer is 4', tokens=80, duration=1.2)

        # Create analytics dashboard
        analytics = AnalyticsDashboard(session_manager)

        # Display dashboard
        analytics.display_dashboard(days=7)

    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()
        print("\nTest completed successfully!")


if __name__ == "__main__":
    test_analytics_dashboard()
