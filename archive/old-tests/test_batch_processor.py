#!/usr/bin/env python3
"""
Test script for Batch Processor functionality
"""

from pathlib import Path
from batch_processor import BatchProcessor, BatchJob, BatchResult
from dataclasses import dataclass
from typing import Optional
import time

# Mock ModelResponse for testing
@dataclass
class MockModelResponse:
    text: str
    tokens_input: int = 10
    tokens_output: int = 50
    duration_seconds: float = 0.5

def main():
    # Initialize batch processor
    checkpoint_dir = Path("D:/models/batch_checkpoints")
    batch_processor = BatchProcessor(checkpoint_dir)

    print("=" * 60)
    print("BATCH PROCESSOR TEST")
    print("=" * 60)

    # Test 1: Load prompts from file
    print("\n[TEST 1] Loading prompts from file...")
    prompts_file = Path("D:/models/examples/batch_prompts.txt")
    prompts = batch_processor.load_prompts_from_file(prompts_file)
    print(f"[OK] Loaded {len(prompts)} prompts")
    print(f"  First prompt: {prompts[0]}")

    # Test 2: Create a batch job
    print("\n[TEST 2] Creating batch job...")
    test_prompts = prompts[:5]  # Use first 5 prompts for testing
    job = batch_processor.create_job("test-model", test_prompts)
    print(f"[OK] Created job: {job.job_id}")
    print(f"  Model: {job.model_id}")
    print(f"  Total prompts: {job.total_prompts}")

    # Test 3: Mock batch processing
    print("\n[TEST 3] Processing batch (mock execution)...")

    def mock_execute(prompt: str) -> MockModelResponse:
        """Mock model execution"""
        time.sleep(0.1)  # Simulate processing time
        return MockModelResponse(
            text=f"Response to: {prompt[:30]}...",
            tokens_input=len(prompt.split()),
            tokens_output=50,
            duration_seconds=0.1
        )

    def progress_callback(current_job: BatchJob, current: int):
        """Display progress"""
        percent = (current / current_job.total_prompts) * 100
        bar_length = 30
        filled = int(bar_length * current / current_job.total_prompts)
        bar = '=' * filled + '-' * (bar_length - filled)
        print(f"\r  Progress: [{bar}] {percent:.0f}% ({current}/{current_job.total_prompts})", end='', flush=True)

    results = batch_processor.process_batch(
        job,
        mock_execute,
        progress_callback=progress_callback,
        error_strategy="continue"
    )

    print()  # New line after progress
    print(f"[OK] Batch completed")
    print(f"  Completed: {job.completed}")
    print(f"  Failed: {job.failed}")
    print(f"  Status: {job.status}")

    # Test 4: Save checkpoint
    print("\n[TEST 4] Testing checkpoint functionality...")
    batch_processor.save_checkpoint(job, results)
    print(f"[OK] Checkpoint saved: {job.checkpoint_file}")

    # Test 5: Load checkpoint
    print("\n[TEST 5] Loading checkpoint...")
    loaded_job, loaded_results = batch_processor.load_checkpoint(job.checkpoint_file)
    print(f"[OK] Checkpoint loaded")
    print(f"  Job ID: {loaded_job.job_id}")
    print(f"  Results count: {len(loaded_results)}")

    # Test 6: List checkpoints
    print("\n[TEST 6] Listing checkpoints...")
    checkpoints = batch_processor.list_checkpoints()
    print(f"[OK] Found {len(checkpoints)} checkpoint(s)")
    for cp in checkpoints:
        print(f"  - {cp['job_id']}: {cp['status']} ({cp['completed']}/{cp['total']})")

    # Test 7: Export results
    print("\n[TEST 7] Exporting results...")
    output_dir = Path("D:/models/outputs")
    output_dir.mkdir(exist_ok=True, parents=True)

    # Export as JSON
    json_file = output_dir / f"test_batch_{job.job_id}.json"
    batch_processor.export_results(job, results, json_file, format='json')
    print(f"[OK] JSON export: {json_file}")

    # Export as CSV
    csv_file = output_dir / f"test_batch_{job.job_id}.csv"
    batch_processor.export_results(job, results, csv_file, format='csv')
    print(f"[OK] CSV export: {csv_file}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nCheckpoint directory: {checkpoint_dir}")
    print(f"Output directory: {output_dir}")
    print("\nYou can now use the batch processing feature in AI Router!")

if __name__ == "__main__":
    main()
