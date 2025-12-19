#!/usr/bin/env python3
"""
Benchmark Features - Performance testing for AI Router Enhanced
Measures execution time for each feature with various input sizes
"""

import sys
from pathlib import Path
import time
from typing import Dict, List, Callable
import json


class FeatureBenchmark:
    """Performance benchmarking for features"""

    def __init__(self):
        self.models_dir = Path(__file__).parent
        sys.path.insert(0, str(self.models_dir))
        self.results = []

    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("=" * 70)
        print("AI ROUTER ENHANCED - PERFORMANCE BENCHMARKS")
        print("=" * 70)
        print()

        # Session Manager benchmarks
        self.section("SESSION MANAGER")
        self.benchmark_session_creation()
        self.benchmark_message_insertion()
        self.benchmark_session_search()

        # Template Manager benchmarks
        self.section("TEMPLATE MANAGER")
        self.benchmark_template_loading()
        self.benchmark_template_rendering()

        # Context Manager benchmarks
        self.section("CONTEXT MANAGER")
        self.benchmark_file_loading()
        self.benchmark_token_estimation()

        # Batch Processor benchmarks
        self.section("BATCH PROCESSOR")
        self.benchmark_batch_creation()
        self.benchmark_checkpoint_operations()

        # Analytics benchmarks
        self.section("ANALYTICS")
        self.benchmark_analytics_queries()

        # Generate report
        self.generate_report()

    def section(self, title: str):
        """Print section header"""
        print()
        print(f"[{title}]")
        print("-" * 70)

    def benchmark(self, name: str, func: Callable, iterations: int = 100):
        """Run a benchmark test"""
        print(f"\n{name}...")

        # Warmup
        func()

        # Actual benchmark
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        # Statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        total_time = sum(times)

        result = {
            'name': name,
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'min_time_ms': min_time * 1000,
            'max_time_ms': max_time * 1000,
            'total_time_s': total_time,
            'ops_per_sec': iterations / total_time if total_time > 0 else 0
        }

        self.results.append(result)

        print(f"  Avg: {result['avg_time_ms']:.3f}ms")
        print(f"  Min: {result['min_time_ms']:.3f}ms")
        print(f"  Max: {result['max_time_ms']:.3f}ms")
        print(f"  Ops/sec: {result['ops_per_sec']:.1f}")

    def benchmark_session_creation(self):
        """Benchmark session creation"""
        from session_manager import SessionManager

        test_db = self.models_dir / "bench_sessions.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)

        def create_session():
            session_id = sm.create_session("test_model")
            # Clean up immediately
            sm.delete_session(session_id)

        self.benchmark("Session Creation", create_session, iterations=50)

        # Cleanup
        test_db.unlink()

    def benchmark_message_insertion(self):
        """Benchmark message insertion"""
        from session_manager import SessionManager

        test_db = self.models_dir / "bench_messages.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)
        session_id = sm.create_session("test_model")

        def add_message():
            sm.add_message(session_id, "user", "Test message", 100)

        self.benchmark("Message Insertion", add_message, iterations=100)

        # Cleanup
        test_db.unlink()

    def benchmark_session_search(self):
        """Benchmark session search"""
        from session_manager import SessionManager

        test_db = self.models_dir / "bench_search.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)

        # Create test data
        for i in range(10):
            sid = sm.create_session(f"model_{i}")
            for j in range(5):
                sm.add_message(sid, "user", f"Message {i}-{j} searchterm", 10)

        def search():
            results = sm.search_messages("searchterm")

        self.benchmark("Session Search", search, iterations=50)

        # Cleanup
        test_db.unlink()

    def benchmark_template_loading(self):
        """Benchmark template loading"""
        from template_manager import TemplateManager

        templates_dir = self.models_dir / "bench_templates"
        templates_dir.mkdir(exist_ok=True)

        # Create test templates
        for i in range(5):
            template = templates_dir / f"template_{i}.yaml"
            template.write_text(f"""
metadata:
  name: Template {i}
  description: Test

user_prompt: |
  Template {i} content
""")

        def load_templates():
            tm = TemplateManager(templates_dir)
            templates = tm.list_templates()

        self.benchmark("Template Loading (5 files)", load_templates, iterations=50)

        # Cleanup
        import shutil
        shutil.rmtree(templates_dir)

    def benchmark_template_rendering(self):
        """Benchmark template rendering"""
        from template_manager import PromptTemplate

        templates_dir = self.models_dir / "bench_render"
        templates_dir.mkdir(exist_ok=True)

        template_file = templates_dir / "test.yaml"
        template_file.write_text("""
metadata:
  name: Render Test
  variables:
    - name: var1
    - name: var2
    - name: var3

user_prompt: |
  {{ var1 }} {{ var2 }} {{ var3 }}
""")

        pt = PromptTemplate(template_file)

        def render():
            pt.render(var1="test1", var2="test2", var3="test3")

        self.benchmark("Template Rendering (3 vars)", render, iterations=100)

        # Cleanup
        import shutil
        shutil.rmtree(templates_dir)

    def benchmark_file_loading(self):
        """Benchmark file loading"""
        from context_manager import ContextManager

        cm = ContextManager()

        # Create test file
        test_file = self.models_dir / "bench_context.txt"
        test_content = "Test content " * 100  # ~1.3KB
        test_file.write_text(test_content)

        def load_file():
            cm.load_file(test_file)

        self.benchmark("File Loading (1.3KB)", load_file, iterations=100)

        # Test with larger file
        large_content = "Test content " * 10000  # ~130KB
        test_file.write_text(large_content)

        def load_large_file():
            cm.load_file(test_file)

        self.benchmark("File Loading (130KB)", load_large_file, iterations=50)

        # Cleanup
        test_file.unlink()

    def benchmark_token_estimation(self):
        """Benchmark token estimation"""
        from context_manager import ContextManager

        cm = ContextManager()
        text = "This is a test sentence for token estimation. " * 20

        def estimate():
            cm.estimate_tokens(text)

        self.benchmark("Token Estimation (~200 words)", estimate, iterations=100)

    def benchmark_batch_creation(self):
        """Benchmark batch job creation"""
        from batch_processor import BatchProcessor

        checkpoint_dir = self.models_dir / "bench_batch"
        checkpoint_dir.mkdir(exist_ok=True)

        bp = BatchProcessor(checkpoint_dir)
        prompts = [f"Prompt {i}" for i in range(10)]

        def create_batch():
            job = bp.create_job("test_model", prompts)

        self.benchmark("Batch Job Creation (10 prompts)", create_batch, iterations=50)

        # Cleanup
        import shutil
        shutil.rmtree(checkpoint_dir)

    def benchmark_checkpoint_operations(self):
        """Benchmark checkpoint save/load"""
        from batch_processor import BatchProcessor

        checkpoint_dir = self.models_dir / "bench_checkpoint"
        checkpoint_dir.mkdir(exist_ok=True)

        bp = BatchProcessor(checkpoint_dir)
        prompts = [f"Prompt {i}" for i in range(10)]
        job = bp.create_job("test_model", prompts)

        def save_checkpoint():
            bp.save_checkpoint(job)

        self.benchmark("Checkpoint Save", save_checkpoint, iterations=50)

        def load_checkpoint():
            bp.load_checkpoint(job.job_id)

        self.benchmark("Checkpoint Load", load_checkpoint, iterations=50)

        # Cleanup
        import shutil
        shutil.rmtree(checkpoint_dir)

    def benchmark_analytics_queries(self):
        """Benchmark analytics queries"""
        from session_manager import SessionManager
        from analytics_dashboard import AnalyticsDashboard

        test_db = self.models_dir / "bench_analytics.db"
        if test_db.exists():
            test_db.unlink()

        sm = SessionManager(test_db)

        # Create test data
        for i in range(20):
            sid = sm.create_session(f"model_{i % 3}")
            for j in range(10):
                sm.add_message(sid, "user", f"Message {j}", 100)
                sm.add_message(sid, "assistant", f"Response {j}", 150)

        dashboard = AnalyticsDashboard(sm)

        def get_stats():
            dashboard.get_usage_statistics(days=30)

        self.benchmark("Usage Statistics Query", get_stats, iterations=50)

        def get_model_stats():
            dashboard.get_model_statistics()

        self.benchmark("Model Statistics Query", get_model_stats, iterations=50)

        # Cleanup
        test_db.unlink()

    def generate_report(self):
        """Generate performance report"""
        print()
        print("=" * 70)
        print("PERFORMANCE REPORT")
        print("=" * 70)
        print()

        # Sort by average time
        sorted_results = sorted(self.results, key=lambda x: x['avg_time_ms'])

        print("Ranked by Average Time (fastest to slowest):")
        print()
        print(f"{'Rank':<5} {'Benchmark':<40} {'Avg Time':<15} {'Ops/sec':<10}")
        print("-" * 70)

        for i, result in enumerate(sorted_results, 1):
            print(f"{i:<5} {result['name']:<40} {result['avg_time_ms']:>10.3f}ms {result['ops_per_sec']:>10.1f}")

        print()

        # Save to JSON
        report_file = self.models_dir / "benchmark_results.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': self.results,
                'summary': {
                    'total_benchmarks': len(self.results),
                    'fastest': sorted_results[0]['name'] if sorted_results else None,
                    'slowest': sorted_results[-1]['name'] if sorted_results else None
                }
            }, f, indent=2)

        print(f"Report saved to: {report_file}")
        print("=" * 70)


def main():
    """Main entry point"""
    benchmark = FeatureBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
