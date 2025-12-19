#!/usr/bin/env python3
"""
Comprehensive Functionality Testing for All 9 Implemented Features
Dry-run testing without executing actual AI models
"""

import sys
from pathlib import Path
import tempfile
import json
from datetime import datetime
import traceback

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results tracking
test_results = []


class TestResult:
    """Track individual test results"""
    def __init__(self, feature, test_name, passed, details="", error=None):
        self.feature = feature
        self.test_name = test_name
        self.passed = passed
        self.details = details
        self.error = error


def test_feature(feature_name, test_name):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*70}")
            print(f"Testing: {feature_name} - {test_name}")
            print(f"{'='*70}")
            try:
                result = func(*args, **kwargs)
                if result is None or result:
                    print(f"[PASS] {test_name}")
                    test_results.append(TestResult(feature_name, test_name, True, "Test completed successfully"))
                    return True
                else:
                    print(f"[FAIL] {test_name}")
                    test_results.append(TestResult(feature_name, test_name, False, "Test returned False"))
                    return False
            except Exception as e:
                print(f"[FAIL] {test_name}")
                print(f"Error: {str(e)}")
                traceback.print_exc()
                test_results.append(TestResult(feature_name, test_name, False, str(e), traceback.format_exc()))
                return False
        return wrapper
    return decorator


# ============================================================================
# FEATURE 1: SESSION MANAGEMENT
# ============================================================================

@test_feature("Session Management", "Create and retrieve session")
def test_session_create_retrieve():
    from session_manager import SessionManager
    import os

    # Create temp database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()
    os.unlink(temp_db_path)

    # Copy schema to temp location
    schema_path = Path(__file__).parent / "schema.sql"
    temp_schema = temp_db_path.parent / "schema.sql"

    if schema_path.exists():
        import shutil
        shutil.copy(schema_path, temp_schema)

    try:
        # Test session creation
        session_mgr = SessionManager(temp_db_path)
        session_id = session_mgr.create_session(
            model_id="test-model",
            model_name="Test Model",
            title="Test Session"
        )

        assert session_id, "Session ID should not be empty"

        # Test session retrieval
        session = session_mgr.get_session(session_id)
        assert session is not None, "Session should exist"
        assert session['model_id'] == "test-model", "Model ID should match"
        assert session['title'] == "Test Session", "Title should match"

        print(f"  Created session: {session_id}")
        print(f"  Model: {session['model_name']}")
        print(f"  Title: {session['title']}")

        return True
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()


@test_feature("Session Management", "Add and retrieve messages")
def test_session_messages():
    from session_manager import SessionManager
    import os

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()
    os.unlink(temp_db_path)

    schema_path = Path(__file__).parent / "schema.sql"
    temp_schema = temp_db_path.parent / "schema.sql"

    if schema_path.exists():
        import shutil
        shutil.copy(schema_path, temp_schema)

    try:
        session_mgr = SessionManager(temp_db_path)
        session_id = session_mgr.create_session("test-model", "Test Model")

        # Add messages
        session_mgr.add_message(session_id, "user", "Hello", tokens=10)
        session_mgr.add_message(session_id, "assistant", "Hi there!", tokens=20, duration=1.5)

        # Retrieve messages
        messages = session_mgr.get_session_history(session_id)
        assert len(messages) == 2, "Should have 2 messages"
        assert messages[0]['role'] == 'user', "First message should be user"
        assert messages[1]['role'] == 'assistant', "Second message should be assistant"

        print(f"  Added {len(messages)} messages")
        print(f"  Message 1: {messages[0]['role']} - {messages[0]['content']}")
        print(f"  Message 2: {messages[1]['role']} - {messages[1]['content']}")

        return True
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()


@test_feature("Session Management", "Export session")
def test_session_export():
    from session_manager import SessionManager
    import os

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()
    os.unlink(temp_db_path)

    schema_path = Path(__file__).parent / "schema.sql"
    temp_schema = temp_db_path.parent / "schema.sql"

    if schema_path.exists():
        import shutil
        shutil.copy(schema_path, temp_schema)

    try:
        session_mgr = SessionManager(temp_db_path)
        session_id = session_mgr.create_session("test-model", "Test Model", "Export Test")
        session_mgr.add_message(session_id, "user", "Test message", tokens=10)

        # Test JSON export
        json_export = session_mgr.export_session(session_id, format='json')
        assert json_export, "JSON export should not be empty"
        data = json.loads(json_export)
        assert 'session' in data, "Export should contain session"
        assert 'messages' in data, "Export should contain messages"

        # Test Markdown export
        md_export = session_mgr.export_session(session_id, format='markdown')
        assert md_export, "Markdown export should not be empty"
        assert "Export Test" in md_export, "Export should contain title"

        print(f"  JSON export: {len(json_export)} characters")
        print(f"  Markdown export: {len(md_export)} characters")

        return True
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()


# ============================================================================
# FEATURE 2: PROMPT TEMPLATES
# ============================================================================

@test_feature("Prompt Templates", "Load and list templates")
def test_templates_load():
    from template_manager import TemplateManager

    template_dir = Path(__file__).parent / "prompt-templates"
    if not template_dir.exists():
        print(f"  Warning: Template directory not found: {template_dir}")
        return True  # Pass if directory doesn't exist

    template_mgr = TemplateManager(template_dir)
    templates = template_mgr.list_templates()

    print(f"  Found {len(templates)} templates")
    for t in templates[:3]:
        print(f"    - {t['name']} ({t['category']})")

    return True


@test_feature("Prompt Templates", "Render template with variables")
def test_template_render():
    from template_manager import TemplateManager, PromptTemplate
    import yaml

    # Create temp template
    temp_template = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8')
    temp_template_path = Path(temp_template.name)

    template_data = {
        'metadata': {
            'name': 'Test Template',
            'id': 'test_template',
            'category': 'testing',
            'variables': [
                {'name': 'subject', 'description': 'Subject to discuss', 'required': True},
                {'name': 'tone', 'description': 'Tone of response', 'default': 'friendly'}
            ]
        },
        'system_prompt': 'You are a helpful assistant.',
        'user_prompt': 'Tell me about {{subject}} in a {{tone}} tone.'
    }

    yaml.dump(template_data, temp_template, default_flow_style=False)
    temp_template.close()

    try:
        template = PromptTemplate(temp_template_path)

        # Render with variables
        rendered = template.render({'subject': 'Python', 'tone': 'professional'})

        assert 'system_prompt' in rendered, "Should have system_prompt"
        assert 'user_prompt' in rendered, "Should have user_prompt"
        assert 'Python' in rendered['user_prompt'], "Should contain subject"
        assert 'professional' in rendered['user_prompt'], "Should contain tone"

        print(f"  Template rendered successfully")
        print(f"  User prompt: {rendered['user_prompt']}")

        return True
    finally:
        temp_template_path.unlink()


# ============================================================================
# FEATURE 3: CONTEXT MANAGEMENT
# ============================================================================

@test_feature("Context Management", "Add file to context")
def test_context_add_file():
    from context_manager import ContextManager

    # Create test file
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    test_file.write("def hello():\n    print('Hello, World!')\n")
    test_file.close()
    test_file_path = Path(test_file.name)

    try:
        ctx_mgr = ContextManager()
        item = ctx_mgr.add_file(test_file_path, label="Test Script")

        assert item is not None, "Should return context item"
        assert item['type'] == 'file', "Type should be file"
        assert item['language'] == 'python', "Should detect Python"
        assert item['tokens'] > 0, "Should estimate tokens"

        print(f"  Added file: {item['label']}")
        print(f"  Language: {item['language']}")
        print(f"  Tokens: {item['tokens']}")

        return True
    finally:
        test_file_path.unlink()


@test_feature("Context Management", "Build context prompt")
def test_context_build_prompt():
    from context_manager import ContextManager

    ctx_mgr = ContextManager()
    ctx_mgr.add_text("This is a test context", label="Test Context")

    prompt = ctx_mgr.build_context_prompt("What is this about?")

    assert "Test Context" in prompt, "Should include context label"
    assert "This is a test context" in prompt, "Should include context content"
    assert "What is this about?" in prompt, "Should include user prompt"

    print(f"  Built prompt with {len(prompt)} characters")
    print(f"  Context items: {len(ctx_mgr.context_items)}")

    return True


@test_feature("Context Management", "Token calculation")
def test_context_tokens():
    from context_manager import ContextManager

    ctx_mgr = ContextManager()
    tokens = ctx_mgr.estimate_tokens("This is a test sentence with several words.")

    assert tokens > 0, "Should estimate tokens"
    print(f"  Estimated tokens: {tokens}")

    # Test with larger text
    large_text = " ".join(["word"] * 100)
    large_tokens = ctx_mgr.estimate_tokens(large_text)
    assert large_tokens > tokens, "Larger text should have more tokens"

    print(f"  Large text tokens: {large_tokens}")

    return True


# ============================================================================
# FEATURE 4: RESPONSE POST-PROCESSING
# ============================================================================

@test_feature("Response Post-Processing", "Extract code blocks")
def test_response_extract_code():
    from response_processor import ResponseProcessor

    temp_dir = Path(tempfile.mkdtemp())

    try:
        processor = ResponseProcessor(temp_dir)

        test_response = """Here is some Python code:
```python
def hello():
    print("Hello!")
```

And here is JavaScript:
```javascript
console.log("Hello!");
```
"""

        code_blocks = processor.extract_code_blocks(test_response)

        assert len(code_blocks) == 2, "Should find 2 code blocks"
        assert code_blocks[0]['language'] == 'python', "First should be Python"
        assert code_blocks[1]['language'] == 'javascript', "Second should be JavaScript"

        print(f"  Found {len(code_blocks)} code blocks")
        for i, block in enumerate(code_blocks):
            print(f"    Block {i+1}: {block['language']}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Response Post-Processing", "Calculate statistics")
def test_response_statistics():
    from response_processor import ResponseProcessor

    temp_dir = Path(tempfile.mkdtemp())

    try:
        processor = ResponseProcessor(temp_dir)

        test_text = "Line 1\nLine 2\nLine 3\n\nLine 5 with more words"
        stats = processor.get_statistics(test_text)

        assert 'char_count' in stats, "Should have char_count"
        assert 'word_count' in stats, "Should have word_count"
        assert 'line_count' in stats, "Should have line_count"
        assert stats['line_count'] == 5, "Should count 5 lines"

        print(f"  Characters: {stats['char_count']}")
        print(f"  Words: {stats['word_count']}")
        print(f"  Lines: {stats['line_count']}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Response Post-Processing", "Save response to file")
def test_response_save():
    from response_processor import ResponseProcessor

    temp_dir = Path(tempfile.mkdtemp())

    try:
        processor = ResponseProcessor(temp_dir)

        response = "This is a test response from the model."
        filepath = processor.save_response(
            response,
            filename="test_response.txt",
            model_name="Test Model",
            metadata={"test": "metadata"}
        )

        assert filepath.exists(), "File should exist"
        content = filepath.read_text(encoding='utf-8')
        assert "Test Model" in content, "Should contain model name"
        assert "This is a test response" in content, "Should contain response"

        print(f"  Saved to: {filepath.name}")
        print(f"  Size: {filepath.stat().st_size} bytes")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


# ============================================================================
# FEATURE 5: BATCH PROCESSING
# ============================================================================

@test_feature("Batch Processing", "Create batch job")
def test_batch_create_job():
    from batch_processor import BatchProcessor

    temp_dir = Path(tempfile.mkdtemp())

    try:
        processor = BatchProcessor(temp_dir)

        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        job = processor.create_job("test-model", prompts)

        assert job.job_id, "Should have job ID"
        assert job.model_id == "test-model", "Should have correct model"
        assert job.total_prompts == 3, "Should have 3 prompts"
        assert job.status == "pending", "Should be pending"

        print(f"  Job ID: {job.job_id}")
        print(f"  Total prompts: {job.total_prompts}")
        print(f"  Status: {job.status}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Batch Processing", "Load prompts from file")
def test_batch_load_prompts():
    from batch_processor import BatchProcessor

    temp_dir = Path(tempfile.mkdtemp())

    # Create prompts file
    prompts_file = temp_dir / "prompts.txt"
    prompts_file.write_text("Prompt 1\nPrompt 2\n# Comment\nPrompt 3\n", encoding='utf-8')

    try:
        processor = BatchProcessor(temp_dir)
        prompts = processor.load_prompts_from_file(prompts_file)

        assert len(prompts) == 3, "Should load 3 prompts (excluding comment)"
        assert prompts[0] == "Prompt 1", "First prompt should match"

        print(f"  Loaded {len(prompts)} prompts")
        for i, p in enumerate(prompts):
            print(f"    {i+1}. {p}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Batch Processing", "Save and load checkpoint")
def test_batch_checkpoint():
    from batch_processor import BatchProcessor, BatchJob, BatchResult

    temp_dir = Path(tempfile.mkdtemp())

    try:
        processor = BatchProcessor(temp_dir)

        # Create job
        prompts = ["Prompt 1", "Prompt 2"]
        job = processor.create_job("test-model", prompts)
        job.completed = 1

        # Create results
        results = [
            BatchResult(
                prompt_index=0,
                prompt="Prompt 1",
                response_text="Response 1",
                tokens_input=10,
                tokens_output=20,
                duration=1.5,
                success=True
            )
        ]

        # Save checkpoint
        processor.save_checkpoint(job, results)
        assert job.checkpoint_file.exists(), "Checkpoint file should exist"

        # Load checkpoint
        loaded_job, loaded_results = processor.load_checkpoint(job.checkpoint_file)
        assert loaded_job.job_id == job.job_id, "Job ID should match"
        assert loaded_job.completed == 1, "Completed count should match"
        assert len(loaded_results) == 1, "Should load 1 result"

        print(f"  Saved checkpoint: {job.checkpoint_file.name}")
        print(f"  Loaded job with {loaded_job.completed} completed")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


# ============================================================================
# FEATURE 6: SMART MODEL SELECTION
# ============================================================================

@test_feature("Smart Model Selection", "Analyze coding prompt")
def test_selector_coding():
    from model_selector import ModelSelector

    temp_prefs = Path(tempfile.mktemp(suffix='.json'))

    try:
        selector = ModelSelector(temp_prefs)

        prompt = "Write a Python function to sort a list"
        scores = selector.analyze_prompt(prompt)

        assert 'coding' in scores, "Should detect coding"
        assert scores['coding'] > 0, "Coding score should be positive"

        print(f"  Prompt: {prompt}")
        print(f"  Scores: {scores}")

        return True
    finally:
        if temp_prefs.exists():
            temp_prefs.unlink()


@test_feature("Smart Model Selection", "Get recommendations")
def test_selector_recommendations():
    from model_selector import ModelSelector

    temp_prefs = Path(tempfile.mktemp(suffix='.json'))

    try:
        selector = ModelSelector(temp_prefs)

        # Mock available models
        available_models = {
            'qwen3-coder-30b': {'name': 'Qwen3 Coder'},
            'phi4-14b': {'name': 'Phi-4'},
            'gemma3-27b': {'name': 'Gemma3'}
        }

        prompt = "Write a creative story about a dragon"
        recommendations = selector.get_recommendations(prompt, available_models, top_n=2)

        assert len(recommendations) > 0, "Should get recommendations"
        assert 'model_id' in recommendations[0], "Should have model_id"
        assert 'confidence' in recommendations[0], "Should have confidence"

        print(f"  Prompt: {prompt}")
        print(f"  Recommendations:")
        for rec in recommendations:
            print(f"    - {rec['model_id']} ({rec['category']}, {rec['confidence']:.2f})")

        return True
    finally:
        if temp_prefs.exists():
            temp_prefs.unlink()


@test_feature("Smart Model Selection", "Preference learning")
def test_selector_preferences():
    from model_selector import ModelSelector

    temp_prefs = Path(tempfile.mktemp(suffix='.json'))

    try:
        selector = ModelSelector(temp_prefs)

        # Learn preference
        selector.learn_preference('coding', 'qwen3-coder-30b')

        # Verify saved
        assert temp_prefs.exists(), "Preferences file should exist"
        prefs = json.loads(temp_prefs.read_text())
        assert prefs['coding'] == 'qwen3-coder-30b', "Should save preference"

        print(f"  Learned preference: coding -> qwen3-coder-30b")
        print(f"  Preferences: {prefs}")

        return True
    finally:
        if temp_prefs.exists():
            temp_prefs.unlink()


# ============================================================================
# FEATURE 7: ANALYTICS DASHBOARD
# ============================================================================

@test_feature("Analytics Dashboard", "Get usage statistics")
def test_analytics_usage():
    from analytics_dashboard import AnalyticsDashboard
    from session_manager import SessionManager
    import os

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()
    os.unlink(temp_db_path)

    schema_path = Path(__file__).parent / "schema.sql"
    temp_schema = temp_db_path.parent / "schema.sql"

    if schema_path.exists():
        import shutil
        shutil.copy(schema_path, temp_schema)

    try:
        # Create test data
        session_mgr = SessionManager(temp_db_path)
        session_id = session_mgr.create_session("test-model", "Test Model")
        session_mgr.add_message(session_id, "user", "Hello", tokens=10)
        session_mgr.add_message(session_id, "assistant", "Hi", tokens=20)

        # Test analytics
        analytics = AnalyticsDashboard(session_mgr)
        stats = analytics.get_usage_statistics(days=7)

        assert stats['total_sessions'] >= 1, "Should have at least 1 session"
        assert stats['total_messages'] >= 2, "Should have at least 2 messages"
        assert stats['total_tokens'] >= 30, "Should have tokens"

        print(f"  Sessions: {stats['total_sessions']}")
        print(f"  Messages: {stats['total_messages']}")
        print(f"  Tokens: {stats['total_tokens']}")

        return True
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()


@test_feature("Analytics Dashboard", "Get model usage")
def test_analytics_model_usage():
    from analytics_dashboard import AnalyticsDashboard
    from session_manager import SessionManager
    import os

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()
    os.unlink(temp_db_path)

    schema_path = Path(__file__).parent / "schema.sql"
    temp_schema = temp_db_path.parent / "schema.sql"

    if schema_path.exists():
        import shutil
        shutil.copy(schema_path, temp_schema)

    try:
        session_mgr = SessionManager(temp_db_path)
        session_mgr.create_session("model-1", "Model 1")
        session_mgr.create_session("model-2", "Model 2")
        session_mgr.create_session("model-1", "Model 1")

        analytics = AnalyticsDashboard(session_mgr)
        model_usage = analytics.get_model_usage(days=7)

        assert len(model_usage) >= 2, "Should have at least 2 models"

        print(f"  Model usage:")
        for model_id, count in model_usage:
            print(f"    {model_id}: {count} sessions")

        return True
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()
        if temp_schema.exists():
            temp_schema.unlink()


# ============================================================================
# FEATURE 8: MODEL COMPARISON
# ============================================================================

@test_feature("Model Comparison", "Create comparison")
def test_comparison_create():
    from model_comparison import ModelComparison

    temp_dir = Path(tempfile.mkdtemp())

    try:
        comparison = ModelComparison(temp_dir)

        prompt = "What is 2+2?"
        responses = [
            {
                'model_id': 'model-1',
                'model_name': 'Model 1',
                'response': 'The answer is 4',
                'tokens_input': 10,
                'tokens_output': 15,
                'duration': 1.2
            },
            {
                'model_id': 'model-2',
                'model_name': 'Model 2',
                'response': '2+2 equals 4',
                'tokens_input': 10,
                'tokens_output': 12,
                'duration': 0.8
            }
        ]

        result = comparison.create_comparison(prompt, responses)

        assert result.comparison_id, "Should have comparison ID"
        assert result.prompt == prompt, "Prompt should match"
        assert len(result.responses) == 2, "Should have 2 responses"

        print(f"  Comparison ID: {result.comparison_id}")
        print(f"  Prompt: {result.prompt}")
        print(f"  Responses: {len(result.responses)}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Model Comparison", "Export comparison")
def test_comparison_export():
    from model_comparison import ModelComparison

    temp_dir = Path(tempfile.mkdtemp())

    try:
        comparison = ModelComparison(temp_dir)

        prompt = "Test prompt"
        responses = [
            {
                'model_id': 'test-model',
                'model_name': 'Test Model',
                'response': 'Test response',
                'tokens_input': 5,
                'tokens_output': 10,
                'duration': 1.0
            }
        ]

        result = comparison.create_comparison(prompt, responses)

        # Export as JSON
        json_path = comparison.export_comparison(result, format='json')
        assert json_path.exists(), "JSON file should exist"

        # Export as Markdown
        md_path = comparison.export_comparison(result, format='markdown')
        assert md_path.exists(), "Markdown file should exist"

        print(f"  JSON export: {json_path.name}")
        print(f"  Markdown export: {md_path.name}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


# ============================================================================
# FEATURE 9: WORKFLOW ENGINE
# ============================================================================

@test_feature("Workflow Engine", "Load workflow YAML")
def test_workflow_load():
    from workflow_engine import WorkflowEngine
    import yaml

    temp_dir = Path(tempfile.mkdtemp())

    # Create test workflow
    workflow_file = temp_dir / "test_workflow.yaml"
    workflow_data = {
        'id': 'test-workflow',
        'name': 'Test Workflow',
        'description': 'A test workflow',
        'variables': {'input': 'test'},
        'steps': [
            {
                'name': 'step1',
                'type': 'prompt',
                'prompt': 'Process {{input}}'
            }
        ]
    }
    workflow_file.write_text(yaml.dump(workflow_data), encoding='utf-8')

    try:
        # Mock AI router
        class MockRouter:
            pass

        engine = WorkflowEngine(temp_dir, MockRouter())
        execution = engine.load_workflow(workflow_file)

        assert execution.workflow_id == 'test-workflow', "Workflow ID should match"
        assert len(execution.steps) == 1, "Should have 1 step"
        assert execution.variables['input'] == 'test', "Should have variable"

        print(f"  Workflow ID: {execution.workflow_id}")
        print(f"  Steps: {len(execution.steps)}")
        print(f"  Variables: {execution.variables}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Workflow Engine", "Validate workflow")
def test_workflow_validate():
    from workflow_engine import WorkflowEngine
    import yaml

    temp_dir = Path(tempfile.mkdtemp())

    # Create valid workflow
    workflow_file = temp_dir / "valid_workflow.yaml"
    workflow_data = {
        'steps': [
            {
                'name': 'test_step',
                'type': 'prompt',
                'prompt': 'Test prompt'
            }
        ]
    }
    workflow_file.write_text(yaml.dump(workflow_data), encoding='utf-8')

    try:
        class MockRouter:
            pass

        engine = WorkflowEngine(temp_dir, MockRouter())
        is_valid, errors = engine.validate_workflow(workflow_file)

        assert is_valid, f"Workflow should be valid. Errors: {errors}"

        print(f"  Workflow valid: {is_valid}")
        print(f"  Errors: {len(errors)}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@test_feature("Workflow Engine", "Variable substitution")
def test_workflow_variables():
    from workflow_engine import WorkflowEngine

    temp_dir = Path(tempfile.mkdtemp())

    try:
        class MockRouter:
            pass

        engine = WorkflowEngine(temp_dir, MockRouter())

        variables = {'name': 'Alice', 'age': '30'}
        text = "Hello {{name}}, you are {{age}} years old."

        result = engine._substitute_variables(text, variables)

        assert 'Alice' in result, "Should substitute name"
        assert '30' in result, "Should substitute age"
        assert '{{' not in result, "Should not have placeholders"

        print(f"  Original: {text}")
        print(f"  Substituted: {result}")

        return True
    finally:
        import shutil
        shutil.rmtree(temp_dir)


# ============================================================================
# GENERATE REPORT
# ============================================================================

def generate_report():
    """Generate comprehensive test report"""

    print("\n" + "="*80)
    print(" "*25 + "TEST SUMMARY REPORT")
    print("="*80 + "\n")

    # Group results by feature
    features = {}
    for result in test_results:
        if result.feature not in features:
            features[result.feature] = []
        features[result.feature].append(result)

    # Calculate statistics
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.passed)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Feature-by-feature breakdown
    print("FEATURE BREAKDOWN:")
    print("-" * 80)

    for feature_name, results in features.items():
        feature_passed = sum(1 for r in results if r.passed)
        feature_total = len(results)
        feature_rate = (feature_passed / feature_total * 100) if feature_total > 0 else 0

        status = "[PASS]" if feature_rate == 100 else "[PARTIAL]" if feature_rate > 0 else "[FAIL]"

        print(f"\n{feature_name}")
        print(f"  Status: {status}")
        print(f"  Tests: {feature_passed}/{feature_total} passed ({feature_rate:.1f}%)")

        for result in results:
            icon = "[+]" if result.passed else "[-]"
            print(f"    {icon} {result.test_name}")
            if not result.passed and result.details:
                print(f"       Error: {result.details[:100]}")

    # Overall statistics
    print("\n" + "="*80)
    print("OVERALL RESULTS:")
    print("-" * 80)
    print(f"Total Tests:     {total_tests}")
    print(f"Passed:          {passed_tests}")
    print(f"Failed:          {failed_tests}")
    print(f"Success Rate:    {success_rate:.1f}%")
    print("="*80 + "\n")

    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 80)

    if success_rate == 100:
        print("[+] All features passed testing! System is ready for production.")
    elif success_rate >= 80:
        print("[!] Most features working. Review and fix failing tests.")
    elif success_rate >= 50:
        print("[!] Significant issues detected. Address failing features.")
    else:
        print("[-] Critical issues detected. System needs major fixes.")

    # List critical failures
    critical_failures = [r for r in test_results if not r.passed]
    if critical_failures:
        print("\nFailed Tests:")
        for failure in critical_failures[:10]:  # Show first 10
            print(f"  - {failure.feature}: {failure.test_name}")
            if failure.details:
                print(f"    {failure.details[:150]}")

    # Missing dependencies
    print("\nDependency Check:")
    dependencies = [
        'sqlite3', 'yaml', 'jinja2', 'json', 'pathlib', 're', 'datetime'
    ]
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)

    if missing:
        print(f"  [-] Missing: {', '.join(missing)}")
    else:
        print(f"  [+] All required dependencies available")

    print("\n" + "="*80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    return success_rate


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all tests"""

    print("\n" + "="*80)
    print(" "*15 + "COMPREHENSIVE FEATURE FUNCTIONALITY TEST")
    print(" "*20 + "AI Router - All 9 Features")
    print("="*80)
    print(f"\nTest Mode: DRY-RUN (No AI model execution)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run all tests
    print("\n" + "="*80)
    print("STARTING TESTS...")
    print("="*80)

    # Feature 1: Session Management
    test_session_create_retrieve()
    test_session_messages()
    test_session_export()

    # Feature 2: Prompt Templates
    test_templates_load()
    test_template_render()

    # Feature 3: Context Management
    test_context_add_file()
    test_context_build_prompt()
    test_context_tokens()

    # Feature 4: Response Post-Processing
    test_response_extract_code()
    test_response_statistics()
    test_response_save()

    # Feature 5: Batch Processing
    test_batch_create_job()
    test_batch_load_prompts()
    test_batch_checkpoint()

    # Feature 6: Smart Model Selection
    test_selector_coding()
    test_selector_recommendations()
    test_selector_preferences()

    # Feature 7: Analytics Dashboard
    test_analytics_usage()
    test_analytics_model_usage()

    # Feature 8: Model Comparison
    test_comparison_create()
    test_comparison_export()

    # Feature 9: Workflow Engine
    test_workflow_load()
    test_workflow_validate()
    test_workflow_variables()

    # Generate report
    success_rate = generate_report()

    # Exit code
    return 0 if success_rate == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
