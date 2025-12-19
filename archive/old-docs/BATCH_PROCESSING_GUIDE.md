# Batch Processing Mode - Implementation Guide

## Overview

The Batch Processing Mode feature enables automated processing of multiple prompts with progress tracking, checkpointing, error handling, and result export functionality.

---

## Files Created

### 1. **batch_processor.py** (D:\models\batch_processor.py)

Main batch processing module containing:

- **BatchJob** dataclass: Represents a batch processing job
  - `job_id`: Unique identifier
  - `model_id`: Model to use
  - `prompts`: List of prompts to process
  - `total_prompts`: Total count
  - `completed`: Number completed
  - `failed`: Number failed
  - `status`: Job status (pending, running, completed, failed)
  - `started_at`, `completed_at`: Timestamps
  - `checkpoint_file`: Path to checkpoint file

- **BatchResult** dataclass: Individual result within a batch
  - `prompt_index`: Index in batch
  - `prompt`: Original prompt text
  - `response_text`: Model response
  - `tokens_input`, `tokens_output`: Token counts
  - `duration`: Processing time
  - `success`: Success flag
  - `error_message`: Error details if failed

- **BatchProcessor** class: Core processing engine
  - `load_prompts_from_file()`: Load from .txt or .json
  - `create_job()`: Initialize new batch job
  - `save_checkpoint()`: Save progress
  - `load_checkpoint()`: Resume from checkpoint
  - `list_checkpoints()`: List all available checkpoints
  - `process_batch()`: Execute batch with callbacks
  - `export_results()`: Export to JSON or CSV

### 2. **examples/batch_prompts.txt** (D:\models\examples\batch_prompts.txt)

Example prompts file with 25 sample prompts covering:
- Data structures and algorithms
- Python programming basics
- Web development concepts
- Database questions
- General computer science

Format:
- One prompt per line
- Lines starting with # are comments
- Empty lines ignored

### 3. **AI Router Integration** (D:\models\ai-router.py)

New menu option [5] for Batch Processing Mode with submenu:
- [1] Process prompts from file
- [2] Enter prompts manually
- [3] Resume from checkpoint
- [4] List checkpoints
- [0] Return to main menu

New methods added:
- `batch_mode()`: Interactive batch processing menu
- `batch_from_file()`: Load and process from file
- `batch_manual_prompts()`: Manual prompt entry
- `batch_resume_checkpoint()`: Resume interrupted jobs
- `batch_list_checkpoints()`: View all checkpoints
- `batch_run_job()`: Execute batch with configuration
- `display_batch_progress()`: Real-time progress display

---

## Features

### 1. Progress Tracking

Real-time progress bar with:
- Visual progress indicator
- Percentage complete
- Current/total count
- Estimated time remaining (ETA)

Example:
```
Progress: [====================----------] 66.7% (4/6) | ETA: 2m 15s
```

### 2. Checkpointing

Automatic checkpoint saving:
- Every 5 prompts processed
- On job completion
- On error (if configured)

Checkpoint contains:
- Complete job state
- All results so far
- Metadata and timestamps

Resume capability:
- Load checkpoint
- Continue from last successful prompt
- Preserve existing results

### 3. Error Handling Strategies

Three error strategies available:

**Continue on error (default)**
- Process all prompts regardless of failures
- Track failed prompts
- Complete the job

**Stop on first error**
- Halt processing on any error
- Save checkpoint
- Mark job as failed

**Threshold (stop after N errors)**
- Continue until error threshold reached
- User-configurable threshold
- Saves checkpoint on threshold

### 4. Result Export

Two export formats:

**JSON (detailed)**
- Complete job metadata
- All prompt/response pairs
- Token counts and timings
- Summary statistics

**CSV (summary)**
- Tabular format
- Columns: index, prompt, response, success, tokens_in, tokens_out, duration, error
- Easy import to Excel/spreadsheet

---

## Usage Examples

### Example 1: Process from File

```bash
# From AI Router main menu
[5] Batch Processing Mode
[1] Process prompts from file

# Enter file path
> D:/models/examples/batch_prompts.txt

# Select model
[1] qwen3-coder-30b
# Choose model...

# Configure error handling
[1] Continue on error

# Start processing
```

### Example 2: Manual Entry

```bash
# From Batch Processing menu
[2] Enter prompts manually

# Enter prompts
Prompt 1: What is Python?
Prompt 2: Explain OOP
Prompt 3: [empty line to finish]

# Select model and run
```

### Example 3: Resume from Checkpoint

```bash
# From Batch Processing menu
[3] Resume from checkpoint

# View available checkpoints
[1] Job ID: abc123de
    Model: qwen3-coder-30b
    Progress: 15/25 (Failed: 2)

# Select and resume
```

---

## Integration Points

### BatchProcessor Initialization

```python
# In AIRouter.__init__()
batch_checkpoint_dir = self.models_dir / "batch_checkpoints"
self.batch_processor = BatchProcessor(batch_checkpoint_dir)
```

### Imports Added

```python
from batch_processor import BatchProcessor, BatchJob, BatchResult
```

### Menu Integration

Main menu option [5] calls `self.batch_mode()`

---

## Output Examples

### JSON Export (batch_abc123.json)

```json
{
  "job": {
    "job_id": "abc123",
    "model_id": "qwen3-coder-30b",
    "total_prompts": 5,
    "completed": 5,
    "failed": 0,
    "status": "completed"
  },
  "results": [
    {
      "prompt_index": 0,
      "prompt": "Explain linked lists",
      "response_text": "A linked list is...",
      "tokens_input": 10,
      "tokens_output": 150,
      "duration": 2.5,
      "success": true
    }
  ],
  "summary": {
    "total": 5,
    "completed": 5,
    "failed": 0,
    "success_rate": 100.0
  }
}
```

### CSV Export (batch_abc123.csv)

```csv
index,prompt,response,success,tokens_in,tokens_out,duration,error
0,Explain linked lists,A linked list is...,True,10,150,2.50,
1,Write reverse function,Here's a function...,True,8,200,3.20,
```

### Checkpoint File (batch_abc123.json)

Similar to JSON export but includes:
- Full prompts list (for resume)
- All intermediate results
- Complete job state

---

## Testing

### Test Script (test_batch_processor.py)

Validates:
- Prompt loading from file
- Job creation
- Batch processing with mock execution
- Checkpoint save/load
- Checkpoint listing
- JSON/CSV export

Run test:
```bash
cd D:/models
python test_batch_processor.py
```

Expected output:
```
============================================================
BATCH PROCESSOR TEST
============================================================

[TEST 1] Loading prompts from file...
[OK] Loaded 25 prompts

[TEST 2] Creating batch job...
[OK] Created job: abc123

... (all 7 tests)

ALL TESTS PASSED!
```

---

## Directory Structure

```
D:/models/
├── ai-router.py                    # Main application (updated)
├── batch_processor.py              # Batch processing module (NEW)
├── test_batch_processor.py         # Test script (NEW)
├── examples/
│   └── batch_prompts.txt          # Example prompts (NEW)
├── batch_checkpoints/              # Checkpoint storage (auto-created)
│   └── batch_*.json               # Checkpoint files
└── outputs/                        # Export directory
    ├── batch_*.json               # JSON exports
    └── batch_*.csv                # CSV exports
```

---

## Error Handling

### Common Issues

**1. File not found**
```
Error: Prompts file not found: /path/to/file.txt
```
Solution: Verify file path, use absolute paths

**2. Unicode encoding (Windows)**
Progress bars use ASCII characters (=, -) for compatibility

**3. Checkpoint corruption**
Checkpoints include timestamp for verification
Invalid checkpoints are skipped during listing

**4. Model execution failure**
Error captured in BatchResult with:
- `success: false`
- `error_message: "error details"`

---

## Performance Notes

### Checkpoint Frequency

Checkpoints saved every 5 prompts to balance:
- Progress preservation
- I/O overhead
- Resume granularity

Adjust in `batch_processor.py`:
```python
if (idx + 1) % 5 == 0:  # Change 5 to desired frequency
    self.save_checkpoint(job, results)
```

### Progress Updates

Real-time progress displayed on each prompt completion
ETA calculated based on average time per prompt

---

## Future Enhancements

Potential improvements:
1. **Parallel processing**: Process multiple prompts concurrently
2. **Rate limiting**: Add delays between prompts
3. **Retry logic**: Auto-retry failed prompts
4. **Batch templates**: Save/load job configurations
5. **Analytics**: Track batch performance metrics
6. **Notifications**: Alert on completion/errors
7. **Streaming results**: Write results as processed
8. **Prompt validation**: Pre-validate prompts before processing

---

## Troubleshooting

### Issue: Batch stuck/frozen
- Check model execution logs
- Look for checkpoint file updates
- Verify model availability

### Issue: High failure rate
- Review error messages in results
- Check model compatibility with prompts
- Verify system resources (memory, GPU)

### Issue: Checkpoint not saving
- Verify write permissions
- Check disk space
- Review checkpoint_dir path

### Issue: Resume not working
- Ensure checkpoint file exists
- Verify job.prompts list intact
- Check checkpoint timestamp

---

## API Reference

### BatchProcessor Methods

```python
# Initialize
processor = BatchProcessor(checkpoint_dir: Path)

# Load prompts
prompts = processor.load_prompts_from_file(file_path: Path) -> List[str]

# Create job
job = processor.create_job(model_id: str, prompts: List[str]) -> BatchJob

# Process batch
results = processor.process_batch(
    job: BatchJob,
    execute_fn: Callable,              # Function that executes model
    progress_callback: Optional[Callable] = None,
    error_strategy: str = "continue"   # "continue", "stop", "threshold:N"
) -> List[BatchResult]

# Checkpoint operations
processor.save_checkpoint(job: BatchJob, results: List[BatchResult])
job, results = processor.load_checkpoint(checkpoint_file: Path)
checkpoints = processor.list_checkpoints() -> List[Dict]

# Export results
processor.export_results(
    job: BatchJob,
    results: List[BatchResult],
    output_file: Path,
    format: str = 'json'  # 'json' or 'csv'
)
```

---

## Conclusion

The Batch Processing Mode provides a robust, production-ready system for processing multiple prompts with:
- Reliable checkpointing
- Flexible error handling
- Real-time progress tracking
- Multiple export formats
- Easy integration with AI Router

All tests passing. Feature ready for use.
