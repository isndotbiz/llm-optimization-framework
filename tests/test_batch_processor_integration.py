#!/usr/bin/env python3
"""
Batch Processor Integration Tests
Comprehensive testing for batch processing system
"""

import sys
from pathlib import Path
import unittest
import shutil
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from batch_processor import BatchProcessor, BatchJob, BatchResult


class TestBatchProcessorIntegration(unittest.TestCase):
    """Integration tests for BatchProcessor"""

    def setUp(self):
        """Set up test checkpoint directory"""
        self.checkpoint_dir = Path(__file__).parent.parent / "test_batch_checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.bp = BatchProcessor(self.checkpoint_dir)

    def tearDown(self):
        """Clean up test checkpoints"""
        if self.checkpoint_dir.exists():
            shutil.rmtree(self.checkpoint_dir)

    def test_create_batch_job(self):
        """Test creating a batch job"""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        job = self.bp.create_job("test_model", prompts)

        self.assertIsNotNone(job.job_id)
        self.assertEqual(job.total_prompts, 3)
        self.assertEqual(job.status, "pending")

    def test_save_and_load_checkpoint(self):
        """Test checkpoint persistence"""
        prompts = ["Prompt 1", "Prompt 2"]
        job = self.bp.create_job("test_model", prompts)

        # Save checkpoint
        self.bp.save_checkpoint(job)

        # Load checkpoint
        loaded_job = self.bp.load_checkpoint(job.job_id)

        self.assertIsNotNone(loaded_job)
        self.assertEqual(loaded_job.job_id, job.job_id)
        self.assertEqual(loaded_job.total_prompts, job.total_prompts)

    def test_update_job_progress(self):
        """Test updating job progress"""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        job = self.bp.create_job("test_model", prompts)

        # Mark as running
        job.status = "running"
        job.completed = 1

        # Save updated state
        self.bp.save_checkpoint(job)

        # Load and verify
        loaded_job = self.bp.load_checkpoint(job.job_id)
        self.assertEqual(loaded_job.status, "running")
        self.assertEqual(loaded_job.completed, 1)

    def test_batch_results(self):
        """Test storing batch results"""
        prompts = ["Prompt 1", "Prompt 2"]
        job = self.bp.create_job("test_model", prompts)

        # Create results
        result1 = BatchResult(
            prompt_index=0,
            prompt="Prompt 1",
            response_text="Response 1",
            tokens_input=10,
            tokens_output=20,
            duration=1.5,
            success=True
        )

        result2 = BatchResult(
            prompt_index=1,
            prompt="Prompt 2",
            response_text="Response 2",
            tokens_input=15,
            tokens_output=25,
            duration=2.0,
            success=True
        )

        # Save results
        self.bp.save_result(job.job_id, result1)
        self.bp.save_result(job.job_id, result2)

        # Load results
        results = self.bp.load_results(job.job_id)
        self.assertEqual(len(results), 2)

    def test_resume_batch_job(self):
        """Test resuming a partially completed batch"""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        job = self.bp.create_job("test_model", prompts)

        # Simulate partial completion
        job.status = "paused"
        job.completed = 1
        self.bp.save_checkpoint(job)

        # Resume
        loaded_job = self.bp.load_checkpoint(job.job_id)
        self.assertEqual(loaded_job.completed, 1)
        self.assertEqual(len(loaded_job.prompts), 3)

    def test_failed_prompt_handling(self):
        """Test handling failed prompts"""
        prompts = ["Prompt 1", "Prompt 2"]
        job = self.bp.create_job("test_model", prompts)

        # Create failed result
        failed_result = BatchResult(
            prompt_index=0,
            prompt="Prompt 1",
            response_text="",
            tokens_input=10,
            tokens_output=0,
            duration=0.5,
            success=False,
            error_message="API Error"
        )

        self.bp.save_result(job.job_id, failed_result)

        # Load and verify
        results = self.bp.load_results(job.job_id)
        self.assertEqual(results[0].success, False)
        self.assertIsNotNone(results[0].error_message)

    def test_list_batch_jobs(self):
        """Test listing all batch jobs"""
        # Create multiple jobs
        for i in range(3):
            prompts = [f"Prompt {i}-{j}" for j in range(2)]
            job = self.bp.create_job(f"model_{i}", prompts)
            self.bp.save_checkpoint(job)

        # List jobs
        jobs = self.bp.list_jobs()
        self.assertGreaterEqual(len(jobs), 3)

    def test_delete_batch_job(self):
        """Test deleting a batch job"""
        prompts = ["Prompt 1", "Prompt 2"]
        job = self.bp.create_job("test_model", prompts)
        self.bp.save_checkpoint(job)

        # Delete job
        self.bp.delete_job(job.job_id)

        # Verify deleted
        with self.assertRaises(Exception):
            self.bp.load_checkpoint(job.job_id)

    def test_batch_statistics(self):
        """Test computing batch statistics"""
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        job = self.bp.create_job("test_model", prompts)

        # Add results
        for i in range(3):
            result = BatchResult(
                prompt_index=i,
                prompt=f"Prompt {i+1}",
                response_text=f"Response {i+1}",
                tokens_input=10 + i,
                tokens_output=20 + i,
                duration=1.0 + i * 0.5,
                success=True
            )
            self.bp.save_result(job.job_id, result)

        # Get statistics
        stats = self.bp.get_job_statistics(job.job_id)

        self.assertEqual(stats['total_prompts'], 3)
        self.assertEqual(stats['completed'], 3)
        self.assertEqual(stats['success_rate'], 100.0)

    def test_large_batch(self):
        """Test handling large batch"""
        prompts = [f"Prompt {i}" for i in range(100)]
        job = self.bp.create_job("test_model", prompts)

        self.assertEqual(job.total_prompts, 100)

        # Simulate processing
        job.status = "running"
        for i in range(50):
            job.completed += 1

        self.bp.save_checkpoint(job)

        # Verify progress
        loaded_job = self.bp.load_checkpoint(job.job_id)
        self.assertEqual(loaded_job.completed, 50)


if __name__ == "__main__":
    unittest.main()
