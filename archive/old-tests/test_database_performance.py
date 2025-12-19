#!/usr/bin/env python3
"""
Performance and Stress Testing for AI Router Database
Tests database performance under various load scenarios
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import random


class PerformanceTester:
    """Tests database performance and stress scenarios"""

    def __init__(self, base_path: str = "D:/models"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / ".ai-router-sessions.db"
        self.results = []

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def log_result(self, test_name: str, duration: float, operations: int, details: str = ""):
        """Log performance test result"""
        ops_per_sec = operations / duration if duration > 0 else 0
        result = {
            "test": test_name,
            "duration_seconds": round(duration, 3),
            "operations": operations,
            "ops_per_second": round(ops_per_sec, 2),
            "details": details
        }
        self.results.append(result)
        print(f"[{test_name}] {operations} ops in {duration:.3f}s = {ops_per_sec:.2f} ops/sec | {details}")

    def test_bulk_insert_sessions(self, count: int = 100) -> float:
        """Test 1: Bulk insert sessions"""
        conn = self._get_connection()
        start = time.time()

        for i in range(count):
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, title)
                VALUES (?, ?, ?, ?)
            """, (f"perf_session_{i}", "qwen2.5:14b", "Qwen 2.5 14B", f"Performance Test {i}"))

        conn.commit()
        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'perf_session_%'")
        conn.commit()
        conn.close()

        self.log_result("Bulk Insert Sessions", duration, count)
        return duration

    def test_bulk_insert_messages(self, sessions: int = 10, messages_per_session: int = 50) -> float:
        """Test 2: Bulk insert messages"""
        conn = self._get_connection()

        # Create test sessions
        session_ids = []
        for i in range(sessions):
            session_id = f"perf_msg_session_{i}"
            session_ids.append(session_id)
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name)
                VALUES (?, ?, ?)
            """, (session_id, "qwen2.5:14b", "Qwen 2.5 14B"))
        conn.commit()

        # Insert messages
        start = time.time()
        total_messages = 0

        for session_id in session_ids:
            for seq in range(1, messages_per_session + 1):
                role = "user" if seq % 2 == 1 else "assistant"
                content = f"Test message {seq} content " * 10  # Make it longer
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content, tokens_used, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, seq, role, content, random.randint(50, 200), random.uniform(1.0, 5.0)))
                total_messages += 1

        conn.commit()
        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'perf_msg_session_%'")
        conn.commit()
        conn.close()

        self.log_result("Bulk Insert Messages", duration, total_messages,
                       f"{sessions} sessions x {messages_per_session} msgs")
        return duration

    def test_complex_query_performance(self, num_queries: int = 20) -> float:
        """Test 3: Complex query performance"""
        conn = self._get_connection()

        # Create test data
        for i in range(20):
            session_id = f"query_test_{i}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, total_tokens)
                VALUES (?, ?, ?, ?)
            """, (session_id, f"model_{i % 5}", f"Model {i % 5}", random.randint(1000, 5000)))

            for seq in range(1, 11):
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content, tokens_used, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, seq, "user" if seq % 2 == 1 else "assistant",
                      f"Query test message {seq}", random.randint(50, 200), random.uniform(1.0, 3.0)))
        conn.commit()

        # Run complex queries
        start = time.time()

        for _ in range(num_queries):
            # Query 1: Model performance aggregation
            conn.execute("""
                SELECT model_id, COUNT(*) as session_count, AVG(total_tokens) as avg_tokens
                FROM sessions
                GROUP BY model_id
                ORDER BY session_count DESC
            """).fetchall()

            # Query 2: Join sessions and messages
            conn.execute("""
                SELECT s.session_id, s.model_id, COUNT(m.message_id) as msg_count,
                       AVG(m.tokens_used) as avg_tokens
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                WHERE s.session_id LIKE 'query_test_%'
                GROUP BY s.session_id
            """).fetchall()

            # Query 3: Recent sessions view
            conn.execute("""
                SELECT * FROM recent_sessions
                WHERE session_id LIKE 'query_test_%'
                LIMIT 10
            """).fetchall()

        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'query_test_%'")
        conn.commit()
        conn.close()

        self.log_result("Complex Query Performance", duration, num_queries * 3,
                       f"{num_queries} iterations x 3 queries")
        return duration

    def test_fts5_search_performance(self, num_searches: int = 50) -> float:
        """Test 4: Full-text search performance"""
        conn = self._get_connection()

        # Create test data with searchable content
        search_terms = ["database", "performance", "optimization", "testing", "query", "index"]
        for i in range(30):
            session_id = f"fts_test_{i}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, title)
                VALUES (?, ?, ?, ?)
            """, (session_id, "test-model", "Test Model", f"Session about {random.choice(search_terms)}"))

            for seq in range(1, 6):
                content = f"This is a test message about {random.choice(search_terms)} " * 5
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content)
                    VALUES (?, ?, ?, ?)
                """, (session_id, seq, "user", content))
        conn.commit()

        # Perform searches
        start = time.time()
        total_results = 0

        for _ in range(num_searches):
            term = random.choice(search_terms)
            cursor = conn.execute("""
                SELECT session_id, content FROM sessions_fts
                WHERE content MATCH ?
                LIMIT 10
            """, (term,))
            results = cursor.fetchall()
            total_results += len(results)

        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'fts_test_%'")
        conn.commit()
        conn.close()

        self.log_result("FTS5 Search Performance", duration, num_searches,
                       f"{total_results} total results found")
        return duration

    def test_analytics_view_performance(self, num_queries: int = 30) -> float:
        """Test 5: Analytics view query performance"""
        conn = self._get_connection()

        # Ensure we have some data
        for i in range(20):
            session_id = f"analytics_test_{i}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, total_tokens)
                VALUES (?, ?, ?, ?)
            """, (session_id, f"model_{i % 3}", f"Model {i % 3}", random.randint(1000, 5000)))

            for seq in range(1, 6):
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content, tokens_used, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, seq, "user", f"Test {seq}", random.randint(50, 200), random.uniform(1.0, 3.0)))
        conn.commit()

        # Query analytics views
        analytics_views = [
            "model_performance",
            "daily_stats",
            "session_quality",
            "token_usage_trends",
            "response_time_analysis",
            "model_comparison"
        ]

        start = time.time()

        for _ in range(num_queries):
            for view in analytics_views:
                conn.execute(f"SELECT * FROM {view} LIMIT 10").fetchall()

        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'analytics_test_%'")
        conn.commit()
        conn.close()

        self.log_result("Analytics View Performance", duration, num_queries * len(analytics_views),
                       f"{num_queries} iterations x {len(analytics_views)} views")
        return duration

    def test_concurrent_operations(self, operations: int = 100) -> float:
        """Test 6: Mixed concurrent-style operations"""
        conn = self._get_connection()

        start = time.time()

        for i in range(operations):
            # Simulate mixed workload
            if i % 3 == 0:
                # Insert session
                conn.execute("""
                    INSERT INTO sessions (session_id, model_id, model_name)
                    VALUES (?, ?, ?)
                """, (f"concurrent_{i}", "test-model", "Test Model"))
            elif i % 3 == 1:
                # Query sessions
                conn.execute("SELECT * FROM sessions WHERE session_id LIKE 'concurrent_%' LIMIT 10").fetchall()
            else:
                # Update session
                conn.execute("""
                    UPDATE sessions SET title = ?
                    WHERE session_id LIKE 'concurrent_%'
                """, (f"Updated {i}",))

            if i % 10 == 0:
                conn.commit()

        conn.commit()
        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'concurrent_%'")
        conn.commit()
        conn.close()

        self.log_result("Concurrent Operations", duration, operations,
                       "Mixed INSERT/SELECT/UPDATE")
        return duration

    def test_trigger_overhead(self, operations: int = 50) -> float:
        """Test 7: Measure trigger execution overhead"""
        conn = self._get_connection()

        # Create test session
        session_id = "trigger_test_session"
        conn.execute("""
            INSERT INTO sessions (session_id, model_id, model_name, message_count)
            VALUES (?, ?, ?, ?)
        """, (session_id, "test-model", "Test Model", 0))
        conn.commit()

        # Insert messages (triggers auto-increment count, update timestamp, FTS)
        start = time.time()

        for i in range(1, operations + 1):
            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (session_id, i, "user", f"Trigger test message {i}"))

        conn.commit()
        duration = time.time() - start

        # Verify trigger worked
        cursor = conn.execute("""
            SELECT message_count FROM sessions WHERE session_id = ?
        """, (session_id,))
        count = cursor.fetchone()[0]

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

        self.log_result("Trigger Overhead", duration, operations,
                       f"Message count updated to {count}")
        return duration

    def test_large_content_handling(self, num_messages: int = 20) -> float:
        """Test 8: Large content blob handling"""
        conn = self._get_connection()

        session_id = "large_content_test"
        conn.execute("""
            INSERT INTO sessions (session_id, model_id, model_name)
            VALUES (?, ?, ?)
        """, (session_id, "test-model", "Test Model"))

        # Create large content (simulate long AI responses)
        large_content = "This is a very long AI response. " * 500  # ~17KB

        start = time.time()

        for i in range(1, num_messages + 1):
            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, i, "assistant", large_content, 2000))

        conn.commit()
        duration = time.time() - start

        # Verify storage
        cursor = conn.execute("""
            SELECT COUNT(*), SUM(LENGTH(content)) as total_bytes
            FROM messages WHERE session_id = ?
        """, (session_id,))
        count, total_bytes = cursor.fetchone()

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

        self.log_result("Large Content Handling", duration, num_messages,
                       f"{total_bytes / 1024:.1f} KB total")
        return duration

    def test_index_efficiency(self, num_queries: int = 100) -> float:
        """Test 9: Index usage and efficiency"""
        conn = self._get_connection()

        # Create test data
        for i in range(50):
            session_id = f"index_test_{i}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, f"model_{i % 5}", f"Model {i % 5}",
                  (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()))
        conn.commit()

        # Run indexed queries
        start = time.time()

        for _ in range(num_queries):
            # Query using idx_sessions_model
            conn.execute("""
                SELECT * FROM sessions WHERE model_id = ? LIMIT 5
            """, (f"model_{random.randint(0, 4)}",)).fetchall()

            # Query using idx_sessions_created
            conn.execute("""
                SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10
            """).fetchall()

            # Query using idx_sessions_activity
            conn.execute("""
                SELECT * FROM sessions ORDER BY last_activity DESC LIMIT 10
            """).fetchall()

        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM sessions WHERE session_id LIKE 'index_test_%'")
        conn.commit()
        conn.close()

        self.log_result("Index Efficiency", duration, num_queries * 3,
                       f"{num_queries} iterations x 3 indexed queries")
        return duration

    def test_comparison_operations(self, num_comparisons: int = 20) -> float:
        """Test 10: Comparison table operations"""
        conn = self._get_connection()

        start = time.time()

        for i in range(num_comparisons):
            comp_id = f"perf_comp_{i}"

            # Insert comparison
            conn.execute("""
                INSERT INTO comparison_results (comparison_id, prompt, model_count)
                VALUES (?, ?, ?)
            """, (comp_id, f"Performance test prompt {i}", 3))

            # Insert responses
            for j in range(3):
                conn.execute("""
                    INSERT INTO comparison_responses
                    (comparison_id, model_id, model_name, response_text, tokens_output, duration_seconds, rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (comp_id, f"model_{j}", f"Model {j}", f"Response {j} " * 50,
                      random.randint(100, 500), random.uniform(2.0, 5.0), j + 1))

            # Query comparison
            conn.execute("""
                SELECT c.*, r.model_name, r.tokens_output
                FROM comparison_results c
                JOIN comparison_responses r ON c.comparison_id = r.comparison_id
                WHERE c.comparison_id = ?
            """, (comp_id,)).fetchall()

        conn.commit()
        duration = time.time() - start

        # Cleanup
        conn.execute("DELETE FROM comparison_results WHERE comparison_id LIKE 'perf_comp_%'")
        conn.commit()
        conn.close()

        self.log_result("Comparison Operations", duration, num_comparisons * 4,
                       f"{num_comparisons} comparisons x 3 responses + query")
        return duration

    def run_all_tests(self):
        """Execute all performance tests"""
        print("="*80)
        print("DATABASE PERFORMANCE AND STRESS TESTING")
        print("="*80)
        print()

        self.test_bulk_insert_sessions(100)
        self.test_bulk_insert_messages(10, 50)
        self.test_complex_query_performance(20)
        self.test_fts5_search_performance(50)
        self.test_analytics_view_performance(30)
        self.test_concurrent_operations(100)
        self.test_trigger_overhead(50)
        self.test_large_content_handling(20)
        self.test_index_efficiency(100)
        self.test_comparison_operations(20)

        self.generate_report()

    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUMMARY")
        print("="*80)

        total_ops = sum(r["operations"] for r in self.results)
        total_duration = sum(r["duration_seconds"] for r in self.results)
        avg_ops_per_sec = sum(r["ops_per_second"] for r in self.results) / len(self.results)

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"Total Operations: {total_ops}")
        print(f"Total Duration: {total_duration:.3f} seconds")
        print(f"Average Throughput: {avg_ops_per_sec:.2f} ops/sec")

        # Find fastest and slowest tests
        fastest = max(self.results, key=lambda x: x["ops_per_second"])
        slowest = min(self.results, key=lambda x: x["ops_per_second"])

        print(f"\nFastest Test: {fastest['test']} ({fastest['ops_per_second']:.2f} ops/sec)")
        print(f"Slowest Test: {slowest['test']} ({slowest['ops_per_second']:.2f} ops/sec)")

        # Performance rating
        if avg_ops_per_sec > 1000:
            rating = "Excellent"
        elif avg_ops_per_sec > 500:
            rating = "Good"
        elif avg_ops_per_sec > 100:
            rating = "Acceptable"
        else:
            rating = "Needs Optimization"

        print(f"\nOverall Performance Rating: {rating}")
        print("="*80)


def main():
    """Main test execution"""
    tester = PerformanceTester("D:/models")
    tester.run_all_tests()


if __name__ == "__main__":
    main()
