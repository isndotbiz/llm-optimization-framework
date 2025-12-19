# Features 6-9 Complete Documentation

This file contains the complete expanded documentation for features 6-9 to be integrated into FEATURE_DOCUMENTATION.md.

---

## 6. Smart Model Auto-Selection

### Overview

The Smart Model Auto-Selection system uses intelligent keyword pattern matching, confidence scoring, and machine learning-based preference tracking to automatically recommend the optimal AI model for any given task. By analyzing prompt content against predefined category patterns (coding, reasoning, creative, research, math) and learning from user selections over time, the system eliminates manual model selection while ensuring you always get the best-suited model for your needs.

This feature is perfect for users who want to focus on their work rather than model specifications, teams implementing AI workflows where consistency is critical, and applications requiring dynamic model routing based on task characteristics.

### Key Capabilities

- **Multi-Level Pattern Matching**: High/medium/low confidence keyword detection across 5 task categories
- **Confidence Scoring**: Normalized 0-1 confidence scores with weighted pattern matching
- **Category Detection**: Automatically classify tasks as coding, reasoning, creative, research, or math
- **Preference Learning**: Track user selections to improve future recommendations
- **Performance Integration**: Factor in model benchmark scores (HumanEval, MMLU, etc.)
- **Multi-Model Recommendations**: Get top N model suggestions with confidence rankings
- **Override Mechanisms**: Manual model selection always available
- **Explanation Generation**: Human-readable explanations for why a model was selected
- **Cost-Aware Selection**: Consider API costs for cloud models (future enhancement)

### Architecture

```
ModelSelector (model_selector.py)
├── Pattern Analysis Engine
│   ├── Keyword Patterns (high/medium/low confidence)
│   ├── Category Scoring
│   └── Confidence Normalization
├── Preference Learning System
│   ├── JSON Persistence
│   ├── Category-Model Mapping
│   └── Usage Tracking
├── Model Recommendation Engine
│   ├── select_model()
│   ├── get_recommendations()
│   └── get_explanation()
└── Category-Model Defaults
    ├── Coding: Qwen3 Coder, Qwen2.5 Coder
    ├── Reasoning: Phi-4, DeepSeek-R1
    ├── Creative: Gemma3, Dolphin Mistral
    ├── Research: Llama3.3 70B, Ministral
    └── Math: Phi-4, Ministral
```

### Complete API Reference

#### ModelSelector Class

```python
class ModelSelector:
    def __init__(self, preferences_file: Path)
    def analyze_prompt(self, prompt: str) -> Dict[str, float]
    def select_model(self, prompt: str, available_models: Dict) -> Tuple[str, str, float]
    def get_recommendations(self, prompt: str, available_models: Dict, top_n: int = 3) -> List[Dict]
    def learn_preference(self, category: str, model_id: str)
    def get_explanation(self, category: str, confidence: float, prompt: str) -> str
```

### Configuration Options

#### Category Pattern Customization

```python
# Add custom patterns to existing categories
ms = ModelSelector(preferences_file=Path(".ai-router-preferences.json"))

# Extend coding patterns
ms.patterns["coding"]["high"].extend([
    "write unit test", "implement feature", "refactor class"
])

# Add new category
ms.patterns["data_analysis"] = {
    "high": ["analyze dataset", "data visualization", "statistical analysis"],
    "medium": ["pandas", "numpy", "matplotlib", "chart"],
    "low": ["data", "analyze"]
}

ms.category_model_map["data_analysis"] = ["qwen25-14b", "phi4-14b"]
```

#### Preference File Structure

```json
{
  "coding": "qwen3-coder-30b",
  "reasoning": "phi4-14b",
  "creative": "gemma3-27b",
  "research": "llama33-70b",
  "math": "phi4-14b"
}
```

### Detailed Usage Examples

#### Basic: Automatic Model Selection

```python
from model_selector import ModelSelector
from pathlib import Path

# Initialize with preferences file
ms = ModelSelector(preferences_file=Path(".ai-router-preferences.json"))

# Available models (from your AI Router)
available_models = {
    "qwen3-coder-30b": {"name": "Qwen3 Coder 30B", "humaneval": 94},
    "phi4-14b": {"name": "Phi-4 14B", "mmlu": 85},
    "gemma3-27b": {"name": "Gemma3 27B", "creative_score": 92}
}

# Example 1: Coding task
model_id, category, confidence = ms.select_model(
    prompt="Write a Python function to implement binary search",
    available_models=available_models
)

print(f"Selected: {model_id}")
print(f"Category: {category}")
print(f"Confidence: {confidence:.0%}")

# Output:
# Selected: qwen3-coder-30b
# Category: coding
# Confidence: 85%

# Example 2: Reasoning task
model_id, category, confidence = ms.select_model(
    prompt="Solve this logic puzzle: If all roses are flowers...",
    available_models=available_models
)

# Output:
# Selected: phi4-14b
# Category: reasoning
# Confidence: 72%
```

#### Intermediate: Multi-Model Recommendations

```python
# Get top 3 model recommendations
recommendations = ms.get_recommendations(
    prompt="Analyze this dataset and create visualizations",
    available_models=available_models,
    top_n=3
)

for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['model_id']} - {rec['category']} ({rec['confidence']:.0%})")

# Output:
# 1. qwen25-14b - research (78%)
# 2. phi4-14b - reasoning (65%)
# 3. gemma3-27b - creative (42%)

# Use top recommendation or let user choose
selected_model = recommendations[0]['model_id']
```

#### Advanced: Confidence Analysis with Explanations

```python
# Analyze prompt confidence across all categories
prompt = "Optimize this sorting algorithm for large datasets"
scores = ms.analyze_prompt(prompt)

print("Category Confidence Breakdown:")
for category, confidence in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category:12} {confidence:.0%} {'█' * int(confidence * 20)}")

# Output:
# Category Confidence Breakdown:
#   coding       100% ████████████████████
#   reasoning     42% ████████
#   math          18% ███

# Get detailed explanation
model_id, category, confidence = ms.select_model(prompt, available_models)
explanation = ms.get_explanation(category, confidence, prompt)
print(f"\n{explanation}")

# Output:
# Selected coding model with high confidence (100%) - detected code-related keywords like 'function', 'optimize', 'algorithm'
```

#### Real-World: Preference Learning Integration

```python
# User workflow with preference learning
prompts_and_feedback = [
    ("Write a REST API in Flask", "qwen3-coder-30b"),
    ("Explain the halting problem", "phi4-14b"),
    ("Generate creative story ideas", "gemma3-27b"),
    ("Implement sorting algorithm", "qwen3-coder-30b"),
]

for prompt, user_selected_model in prompts_and_feedback:
    # Get automatic recommendation
    auto_model, category, confidence = ms.select_model(prompt, available_models)

    print(f"\nPrompt: {prompt[:50]}...")
    print(f"Auto-selected: {auto_model} ({category}, {confidence:.0%})")
    print(f"User chose: {user_selected_model}")

    # Learn from user's choice if different
    if user_selected_model != auto_model:
        ms.learn_preference(category, user_selected_model)
        print(f"  → Learned preference: {category} → {user_selected_model}")

# After learning, preferences are saved and future prompts benefit
# Preferences file now contains user's preferred models per category
```

### Category Detection Algorithm

The system uses a multi-tiered pattern matching approach:

1. **Pattern Matching**: Check prompt against high/medium/low confidence patterns
2. **Score Accumulation**:
   - High match: +0.5 points
   - Medium match: +0.3 points
   - Low match: +0.1 points
3. **Normalization**: Divide all scores by max score to get 0-1 range
4. **Category Selection**: Choose category with highest normalized score

```python
# Example scoring
prompt = "Write Python code to implement merge sort"

# Matches:
# - "Write code" (coding, high) → +0.5
# - "Python" (coding, medium) → +0.3
# - "implement" (coding, high) → +0.5
# - "code" (coding, medium) → +0.3
# Total coding score: 1.6

# After normalization (max=1.6): coding = 1.00 (100%)
```

### Customization Guide

#### Adding Custom Categories

```python
# Add a specialized category for your domain
ms.patterns["documentation"] = {
    "high": ["write documentation", "api docs", "readme", "user guide"],
    "medium": ["document", "explain", "tutorial", "guide"],
    "low": ["doc", "help text"]
}

ms.category_model_map["documentation"] = ["qwen25-14b", "gemma3-27b"]

# Save to preferences
ms.learn_preference("documentation", "qwen25-14b")
```

#### Custom Confidence Thresholds

```python
# Extend ModelSelector for custom confidence handling
class CustomModelSelector(ModelSelector):
    def select_model(self, prompt: str, available_models: Dict) -> Tuple[str, str, float]:
        model_id, category, confidence = super().select_model(prompt, available_models)

        # If confidence < 50%, use general-purpose model
        if confidence < 0.5:
            print(f"Low confidence ({confidence:.0%}), falling back to general model")
            return "dolphin-llama31-8b", "general", confidence

        return model_id, category, confidence

custom_ms = CustomModelSelector(preferences_file=Path(".preferences.json"))
```

### Integration with Other Features

#### Workflow Engine Integration

```yaml
# workflow.yaml
steps:
  - name: analyze_and_route
    type: prompt
    model: auto  # Uses ModelSelector
    prompt: "{{user_request}}"
    save_to: result
```

#### Batch Processing Integration

```python
from batch_processor import BatchProcessor
from model_selector import ModelSelector

bp = BatchProcessor(checkpoint_dir=Path("checkpoints/"))
ms = ModelSelector(preferences_file=Path(".preferences.json"))

# Auto-select model per prompt
prompts = [
    "Write a binary tree implementation",
    "Explain quantum mechanics",
    "Generate creative metaphors",
]

for prompt in prompts:
    model_id, category, confidence = ms.select_model(prompt, available_models)
    print(f"{prompt[:40]:40} → {model_id:20} ({confidence:.0%})")
```

### Performance Tips

1. **Cache Analysis Results**: For repeated prompts, cache analyze_prompt() results
2. **Batch Category Detection**: Analyze multiple prompts in one pass
3. **Optimize Pattern Lists**: Keep most common patterns in "high" category
4. **Preference Persistence**: Save preferences after every N selections (not every time)
5. **Model Availability Caching**: Cache available_models dict to avoid repeated lookups

### Troubleshooting

#### Issue: Wrong category detected

**Cause**: Ambiguous keywords or weak patterns

**Solution**: Analyze confidence scores
```python
scores = ms.analyze_prompt("my ambiguous prompt")
print(scores)  # See which categories matched

# Add more specific patterns
ms.patterns["coding"]["high"].append("very specific coding phrase")
```

#### Issue: Low confidence scores across all categories

**Cause**: Generic prompt or missing patterns

**Solution**: Add general-purpose fallback
```python
if max(scores.values()) < 0.3:
    return "general-purpose-model", "general", 0.5
```

#### Issue: Preferences not persisting

**Cause**: Permissions or file path issues

**Solution**: Check file access
```python
preferences_file = Path(".ai-router-preferences.json")
try:
    preferences_file.touch()
    print(f"Preferences file writable: {preferences_file}")
except Exception as e:
    print(f"Cannot write preferences: {e}")
```

### Best Practices

1. **Start with Auto-Selection**: Let the system learn your preferences naturally
2. **Review Confidence Scores**: Monitor selections to ensure accuracy
3. **Add Domain-Specific Patterns**: Customize for your field (legal, medical, etc.)
4. **Learn from Corrections**: Always call learn_preference() when manually overriding
5. **Use Multi-Recommendations**: Show users alternatives when confidence is low
6. **Explain Selections**: Display explanations to build user trust
7. **Backup Preferences**: Version control your preferences JSON file
8. **Test Pattern Changes**: Validate new patterns on sample prompts before deploying
9. **Monitor Category Distribution**: Ensure balanced category detection
10. **Update Model Mappings**: Keep category-model mappings current as new models arrive

### FAQ

**Q: How do I handle prompts that match multiple categories?**

```python
scores = ms.analyze_prompt(prompt)
top_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

print("Top matching categories:")
for category, confidence in top_categories:
    print(f"  {category}: {confidence:.0%}")
```

**Q: Can I override auto-selection in specific cases?**

```python
# Check if specific keyword present
if "use gpt-4" in prompt.lower():
    model_id = "gpt-4-openrouter"
else:
    model_id, category, confidence = ms.select_model(prompt, available_models)
```

**Q: How do I reset learned preferences?**

```python
# Delete preferences file
Path(".ai-router-preferences.json").unlink()

# Or reset programmatically
ms.preferences = {}
ms._save_preferences()
```

**Q: Can I weight certain models higher for specific categories?**

```python
# Modify category_model_map to prioritize certain models
ms.category_model_map["coding"] = [
    "qwen3-coder-30b",  # First = highest priority
    "qwen25-coder-32b",
    "qwen25-coder-14b-mlx"
]
```

**Q: How do I test the selector without actual model execution?**

```python
# Test analysis only
test_prompts = [
    "Write Python code",
    "Solve this math problem",
    "Generate a creative story",
]

for prompt in test_prompts:
    scores = ms.analyze_prompt(prompt)
    model_id, category, confidence = ms.select_model(prompt, available_models)
    print(f"{prompt[:30]:30} → {category:10} ({confidence:.0%})")
```

---

## 7. Performance Analytics Dashboard

### Overview

The Performance Analytics Dashboard provides comprehensive usage tracking, performance metrics visualization, and detailed reporting capabilities for your AI Router usage. Built on top of the SQLite session database, it extracts insights from conversation history to show usage patterns, model performance comparisons, daily activity trends, and generates actionable recommendations for optimizing your AI workflow.

Perfect for tracking team usage, optimizing model selection, identifying performance bottlenecks, justifying AI tool costs, and monitoring productivity gains from AI assistance.

### Key Capabilities

- **Usage Statistics**: Total sessions, messages, tokens, averages across configurable time periods
- **Model Performance Tracking**: Compare response times, token usage, success rates per model
- **Activity Visualization**: ASCII charts for daily/weekly/monthly activity patterns
- **Top Models Ranking**: Identify most-used and best-performing models
- **Custom Date Ranges**: Analyze any time period (last 7 days, last month, year-to-date)
- **SQL Query Access**: Direct database queries for custom analytics
- **Export Capabilities**: Generate HTML/PDF/JSON reports for sharing
- **Recommendations Engine**: AI-powered suggestions based on usage patterns
- **Cost Tracking**: Monitor API costs for cloud models (when applicable)
- **Performance Benchmarking**: Compare your usage against baseline metrics

### Architecture

```
AnalyticsDashboard (analytics_dashboard.py)
├── Data Aggregation Layer
│   ├── Session Statistics
│   ├── Message Analytics
│   ├── Token Tracking
│   └── Model Performance Metrics
├── Visualization Engine
│   ├── ASCII Charts (bar/sparkline)
│   ├── Usage Tables
│   └── Trend Analysis
├── Query System
│   ├── Predefined Queries
│   ├── Custom SQL Support
│   └── Aggregation Functions
└── Reporting System
    ├── HTML Export
    ├── JSON Export
    └── CSV Export
```

### Complete API Reference

#### AnalyticsDashboard Class

```python
class AnalyticsDashboard:
    def __init__(self, session_manager)
    def get_usage_statistics(self, days: int = 30) -> Dict
    def get_model_usage(self, days: int = 30) -> List[Tuple[str, int]]
    def get_daily_activity(self, days: int = 30) -> List[Tuple[str, int]]
    def get_avg_response_time(self) -> float
    def get_top_models_by_performance(self) -> List[Dict]
    def display_dashboard(self, days: int = 30)
```

### Configuration Options

#### Time Period Configuration

```python
# Last 7 days
analytics.get_usage_statistics(days=7)

# Last 30 days (default)
analytics.get_usage_statistics(days=30)

# Last 90 days
analytics.get_usage_statistics(days=90)

# Year-to-date (365 days)
analytics.get_usage_statistics(days=365)
```

#### Chart Display Options

```python
# Modify chart dimensions in display methods
# In _display_daily_activity_chart():
bar_height = 10  # Vertical chart height (lines)
bar_width = 40   # Horizontal bar width (chars)
```

### Detailed Usage Examples

#### Basic: View Dashboard

```python
from analytics_dashboard import AnalyticsDashboard
from session_manager import SessionManager
from pathlib import Path

# Initialize with session manager
sm = SessionManager(Path(".ai-router-sessions.db"))
analytics = AnalyticsDashboard(session_manager=sm)

# Display full dashboard for last 30 days
analytics.display_dashboard(days=30)

# Output:
# ======================================================================
#   PERFORMANCE ANALYTICS DASHBOARD
#   Period: Last 30 days
#   Generated: 2025-12-09 14:30:52
# ======================================================================
#
# USAGE STATISTICS
# ----------------------------------------------------------------------
#   Total Sessions:              45
#   Total Messages:             352
#     |- User Messages:         176
#     +- AI Responses:          176
#   Total Tokens:           87,450
#   Avg Tokens/Message:        248.4
# ...
```

#### Intermediate: Custom Analytics Queries

```python
# Get detailed usage statistics
stats = analytics.get_usage_statistics(days=30)

print(f"Sessions: {stats['total_sessions']}")
print(f"Messages: {stats['total_messages']}")
print(f"Tokens: {stats['total_tokens']:,}")
print(f"Avg tokens/message: {stats['avg_tokens']:.1f}")

# Model usage ranking
model_usage = analytics.get_model_usage(days=30)

print("\nTop 5 Models:")
for model_id, count in model_usage[:5]:
    print(f"  {model_id:30} {count:>5} sessions")

# Output:
# Top 5 Models:
#   qwen3-coder-30b                   18 sessions
#   phi4-14b                          12 sessions
#   gemma3-27b                         8 sessions
#   dolphin-llama31-8b                 5 sessions
#   llama33-70b                        2 sessions

# Daily activity
activity = analytics.get_daily_activity(days=7)

for date, message_count in activity:
    print(f"{date}: {message_count} messages")

# Output:
# 2025-12-03: 45 messages
# 2025-12-04: 67 messages
# 2025-12-05: 52 messages
# ...
```

#### Advanced: Performance Comparison

```python
# Get detailed performance metrics per model
performance = analytics.get_top_models_by_performance()

print("Model Performance Comparison:")
print(f"{'Model':<30} {'Sessions':<10} {'Avg Tokens':<12} {'Avg Time':<10}")
print("-" * 70)

for model in performance:
    print(f"{model['model_id']:<30} "
          f"{model['session_count']:<10} "
          f"{model['avg_tokens']:<12.0f} "
          f"{model['avg_duration']:<10.2f}s")

# Output:
# Model Performance Comparison:
# Model                          Sessions   Avg Tokens   Avg Time
# ----------------------------------------------------------------------
# qwen3-coder-30b                18         342          2.45s
# phi4-14b                       12         287          1.85s
# gemma3-27b                     8          456          3.21s
# ...

# Calculate efficiency metrics
for model in performance:
    if model['avg_duration'] > 0:
        tokens_per_sec = model['avg_tokens'] / model['avg_duration']
        print(f"{model['model_id']}: {tokens_per_sec:.0f} tokens/sec")
```

#### Real-World: Generate Monthly Report

```python
from datetime import datetime, timedelta

# Generate comprehensive monthly report
def generate_monthly_report(analytics, month_start, month_end):
    """Generate detailed monthly analytics report"""

    days = (month_end - month_start).days

    # Overall statistics
    stats = analytics.get_usage_statistics(days=days)

    # Model breakdown
    model_usage = analytics.get_model_usage(days=days)

    # Performance metrics
    avg_response_time = analytics.get_avg_response_time()
    performance = analytics.get_top_models_by_performance()

    # Create report
    report = {
        "period": {
            "start": month_start.isoformat(),
            "end": month_end.isoformat(),
            "days": days
        },
        "summary": stats,
        "model_usage": [
            {"model": m[0], "sessions": m[1]} for m in model_usage
        ],
        "performance": performance,
        "metrics": {
            "avg_response_time": avg_response_time,
            "total_cost": 0.0  # Calculate if using cloud models
        }
    }

    return report

# Generate report for last month
month_end = datetime.now()
month_start = month_end - timedelta(days=30)

report = generate_monthly_report(analytics, month_start, month_end)

# Export as JSON
import json
with open("monthly_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Report generated: monthly_report.json")
print(f"Sessions: {report['summary']['total_sessions']}")
print(f"Messages: {report['summary']['total_messages']}")
print(f"Tokens: {report['summary']['total_tokens']:,}")
```

### SQL Query Examples

Access the underlying database directly for custom analytics:

```python
import sqlite3

conn = sqlite3.connect(".ai-router-sessions.db")

# Custom query: Messages per hour of day
query = """
SELECT
    strftime('%H', created_at) as hour,
    COUNT(*) as message_count
FROM messages
WHERE created_at >= date('now', '-30 days')
GROUP BY hour
ORDER BY hour
"""

results = conn.execute(query).fetchall()

print("Messages by Hour of Day:")
for hour, count in results:
    print(f"{hour:02d}:00 - {count:>4} messages")

conn.close()

# Custom query: Average session length
query = """
SELECT
    AVG(message_count) as avg_messages_per_session,
    AVG(total_tokens) as avg_tokens_per_session
FROM sessions
WHERE created_at >= date('now', '-30 days')
"""

# Token usage by model
query = """
SELECT
    s.model_id,
    SUM(m.tokens_used) as total_tokens,
    AVG(m.tokens_used) as avg_tokens,
    COUNT(*) as message_count
FROM messages m
JOIN sessions s ON m.session_id = s.session_id
WHERE s.created_at >= date('now', '-30 days')
GROUP BY s.model_id
ORDER BY total_tokens DESC
```

### Visualization Examples

The dashboard provides ASCII-based visualizations:

#### Horizontal Bar Chart (Model Usage)

```
MODEL USAGE
----------------------------------------------------------------------
  qwen3-coder-30b      ########################################    45 (38.5%)
  phi4-14b             ###########################                 32 (27.4%)
  gemma3-27b           ###################                         22 (18.8%)
  dolphin-llama31-8b   ##########                                  12 (10.3%)
  llama33-70b          #####                                        6 ( 5.1%)
```

#### Vertical Activity Chart (Daily Messages)

```
DAILY ACTIVITY (Last 14 days)
----------------------------------------------------------------------
  ##############
  ##############
  ##############  #
  ############# ##
  ############# ##
  ######  ##### ##
  ####    ##### ##  #
  ###     ##### ##  #
  ##      ##### ### #
  #       ##### ### #
  --------------
  0123456789ABCD

  Peak: 89 messages/day
```

### Export Formats

#### HTML Report Export

```python
# Generate HTML report (custom implementation)
def export_html_report(analytics, filename, days=30):
    stats = analytics.get_usage_statistics(days=days)
    model_usage = analytics.get_model_usage(days=days)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Router Analytics Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1>AI Router Analytics Report</h1>
        <h2>Usage Statistics (Last {days} days)</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Sessions</td><td>{stats['total_sessions']}</td></tr>
            <tr><td>Total Messages</td><td>{stats['total_messages']}</td></tr>
            <tr><td>Total Tokens</td><td>{stats['total_tokens']:,}</td></tr>
            <tr><td>Avg Tokens/Message</td><td>{stats['avg_tokens']:.1f}</td></tr>
        </table>

        <h2>Model Usage</h2>
        <table>
            <tr><th>Model</th><th>Sessions</th></tr>
            {''.join(f'<tr><td>{m[0]}</td><td>{m[1]}</td></tr>' for m in model_usage)}
        </table>
    </body>
    </html>
    """

    Path(filename).write_text(html, encoding='utf-8')
    print(f"HTML report exported: {filename}")

export_html_report(analytics, "analytics_report.html", days=30)
```

### Integration with Other Features

#### Session Management Integration

```python
# Analytics automatically pulls from session database
# Ensure sessions are being saved properly
from session_manager import SessionManager

sm = SessionManager(Path(".ai-router-sessions.db"))

# Create session
session_id = sm.create_session("qwen3-coder-30b", "Qwen3 Coder", "My session")

# Add messages (these appear in analytics)
sm.add_message(session_id, "user", "Hello", tokens=5)
sm.add_message(session_id, "assistant", "Hi there!", tokens=15, duration=1.2)

# Analytics now includes this data
analytics = AnalyticsDashboard(sm)
stats = analytics.get_usage_statistics(days=1)
```

### Performance Tips

1. **Index Database**: Add indexes on created_at columns for faster queries
2. **Cache Results**: Store dashboard data and refresh periodically
3. **Limit History**: Archive old sessions to keep database performant
4. **Batch Queries**: Combine multiple stat queries into single DB connection
5. **Async Rendering**: Generate charts asynchronously for large datasets

### Troubleshooting

#### Issue: Slow analytics queries

**Cause**: Large database without indexes

**Solution**: Add database indexes
```python
import sqlite3
conn = sqlite3.connect(".ai-router-sessions.db")

# Add indexes
conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")

conn.close()
```

#### Issue: Empty charts/statistics

**Cause**: No data in time range

**Solution**: Check data availability
```python
# Verify data exists
stats = analytics.get_usage_statistics(days=365)  # Check full year
if stats['total_sessions'] == 0:
    print("No sessions found. Have you created any sessions?")
```

#### Issue: Incorrect token counts

**Cause**: Missing token tracking in messages

**Solution**: Ensure add_message includes tokens
```python
# Correct:
sm.add_message(session_id, "assistant", response_text, tokens_used=247)

# Incorrect (tokens not tracked):
sm.add_message(session_id, "assistant", response_text)
```

### Best Practices

1. **Regular Monitoring**: Check dashboard weekly to spot trends
2. **Track Metrics Over Time**: Export monthly reports for historical analysis
3. **Optimize Based on Data**: Use performance metrics to choose best models
4. **Set Baseline Metrics**: Establish normal usage patterns to detect anomalies
5. **Share Reports**: Generate HTML reports for stakeholders
6. **Monitor Costs**: Track token usage to estimate costs for cloud models
7. **Archive Old Data**: Periodically archive sessions older than 6 months
8. **Validate Data Quality**: Check for missing tokens/durations and fix
9. **Use Custom Queries**: Leverage SQL for domain-specific analytics
10. **Automate Reporting**: Schedule weekly/monthly report generation

### FAQ

**Q: How do I track costs for cloud API models?**

```python
# Add cost calculation
COST_PER_1K_TOKENS = {
    "gpt-4": 0.03,
    "claude-sonnet": 0.015,
    "gpt-3.5-turbo": 0.0015
}

def calculate_costs(stats, model_usage):
    total_cost = 0.0
    for model_id, session_count in model_usage:
        if model_id in COST_PER_1K_TOKENS:
            # Get tokens for this model
            tokens = get_tokens_for_model(model_id)  # Custom query
            cost = (tokens / 1000) * COST_PER_1K_TOKENS[model_id]
            total_cost += cost
    return total_cost
```

**Q: Can I export to PDF?**

```python
# Use HTML + headless browser or library like weasyprint
from weasyprint import HTML

export_html_report(analytics, "temp_report.html")
HTML("temp_report.html").write_pdf("analytics_report.pdf")
```

**Q: How do I compare this month vs last month?**

```python
this_month = analytics.get_usage_statistics(days=30)
last_month_start = datetime.now() - timedelta(days=60)
last_month_end = datetime.now() - timedelta(days=30)

# Custom query for last month
# Then compare metrics
growth = (this_month['total_sessions'] - last_month_sessions) / last_month_sessions * 100
print(f"Session growth: {growth:+.1f}%")
```

**Q: Can I track individual user usage in a team environment?**

```python
# Add user_id to sessions table and track per-user
# Modify SessionManager to accept user_id
# Then query analytics per user

def get_user_statistics(analytics, user_id):
    conn = analytics._get_connection()
    stats = conn.execute("""
        SELECT COUNT(*), SUM(total_tokens)
        FROM sessions
        WHERE user_id = ? AND created_at >= date('now', '-30 days')
    """, (user_id,)).fetchone()
    return {"sessions": stats[0], "tokens": stats[1]}
```

---

## 8. Context Management & Injection

### Overview

The Context Management system enables seamless injection of file content, code snippets, and text context into AI prompts, with intelligent token estimation, multi-file support, and automatic formatting. By providing relevant background information to AI models through structured context injection, you can dramatically improve response quality, accuracy, and relevance while maintaining full control over context size and composition.

This feature is essential for code reviews where you need to provide the full source file, documentation generation that requires multiple file context, question-answering about specific codebases, and any scenario where the AI needs access to external information beyond the prompt itself.

### Key Capabilities

- **File Content Injection**: Load and inject any text file with automatic language detection
- **30+ Language Support**: Automatic syntax detection for Python, JavaScript, Java, C++, Rust, Go, and 25+ more
- **Token Estimation**: Approximate token count using words * 1.3 heuristic
- **Multi-File Context**: Combine multiple files into a single context
- **Context Size Management**: Automatic truncation when exceeding token limits
- **Security**: Path traversal protection prevents access outside base directory
- **Formatted Output**: Markdown code blocks with language tags and file paths
- **Context Summary**: View all loaded context items with token counts
- **Selective Removal**: Remove individual context items by index
- **Configurable Limits**: Adjust max tokens based on model capabilities

### Architecture

```
ContextManager (context_manager.py)
├── File Loading System
│   ├── add_file() with path validation
│   ├── Language detection (30+ languages)
│   └── UTF-8 encoding handling
├── Text Context System
│   ├── add_text() for arbitrary content
│   └── Label management
├── Token Estimation
│   ├── Word count * 1.3 heuristic
│   └── Adjustable ratio
├── Context Building
│   ├── build_context_prompt()
│   ├── Truncation logic
│   └── Markdown formatting
└── Management Functions
    ├── get_context_summary()
    ├── remove_context_item()
    └── clear_context()
```

### Complete API Reference

#### ContextManager Class

```python
class ContextManager:
    def __init__(self)
    def add_file(self, file_path: Path, label: Optional[str] = None) -> Dict
    def add_text(self, text: str, label: str) -> Dict
    def estimate_tokens(self, text: str) -> int
    def build_context_prompt(self, user_prompt: str, truncate: bool = True) -> str
    def get_context_summary(self) -> str
    def remove_context_item(self, index: int) -> bool
    def clear_context(self)
    def set_max_tokens(self, max_tokens: int)
    def get_total_tokens(self) -> int
```

### Configuration Options

#### Token Limit Configuration

```python
cm = ContextManager()

# Default: 4096 tokens
cm.max_tokens = 4096

# For models with larger context
cm.set_max_tokens(8192)   # Llama3.3 70B
cm.set_max_tokens(16384)  # Some cloud models
cm.set_max_tokens(32768)  # Extended context models

# Adjust token estimation ratio
cm.token_estimation_ratio = 1.3  # Default (conservative)
cm.token_estimation_ratio = 1.5  # More conservative
cm.token_estimation_ratio = 1.0  # Less conservative
```

### Detailed Usage Examples

#### Basic: Single File Context

```python
from context_manager import ContextManager
from pathlib import Path

# Initialize
cm = ContextManager()

# Add a Python file for review
file_info = cm.add_file(Path("my_module.py"))

print(f"Added: {file_info['label']}")
print(f"Language: {file_info['language']}")
print(f"Tokens: {file_info['tokens']:,}")

# Build prompt with context
user_prompt = "Review this code for performance issues"
full_prompt = cm.build_context_prompt(user_prompt)

# Send to AI model
response = ai_router.run_model(model_id, model_data, full_prompt)

# Output prompt structure:
# ## my_module.py (path/to/my_module.py)
#
# ```python
# def my_function():
#     # ... file contents ...
# ```
#
# ================================================================================
#
# USER REQUEST:
# Review this code for performance issues
```

#### Intermediate: Multi-File Context

```python
# Add multiple related files
files = [
    "src/auth.py",
    "src/database.py",
    "src/models.py",
    "tests/test_auth.py"
]

for file_path in files:
    cm.add_file(Path(file_path))

# View context summary
print(cm.get_context_summary())

# Output:
# Context Summary:
#   Items: 4
#   Total tokens: 3,847
#   Max tokens: 4,096
#   Utilization: 93.9%
#
# Context Items:
#   [1] auth.py (file, 1,245 tokens)
#   [2] database.py (file, 987 tokens)
#   [3] models.py (file, 1,203 tokens)
#   [4] test_auth.py (file, 412 tokens)

# Build prompt (will auto-truncate if needed)
user_prompt = "Explain how authentication works in this codebase"
full_prompt = cm.build_context_prompt(user_prompt, truncate=True)
```

#### Advanced: Selective Context with Token Management

```python
# Add files with token limit
cm.set_max_tokens(8192)

# Add files in priority order (most important first)
priority_files = [
    ("core/engine.py", "Main engine logic"),
    ("core/config.py", "Configuration"),
    ("utils/helpers.py", "Helper functions")
]

for file_path, description in priority_files:
    try:
        cm.add_file(Path(file_path), label=description)
        print(f"✓ Added {description} ({cm.get_total_tokens()} tokens)")
    except Exception as e:
        print(f"✗ Failed to add {file_path}: {e}")

# Check if we're approaching limit
if cm.get_total_tokens() > cm.max_tokens * 0.9:
    print("Warning: Context nearly full, consider removing lower-priority items")

# Remove least important item if needed
if cm.get_total_tokens() > cm.max_tokens:
    cm.remove_context_item(len(cm.context_items) - 1)  # Remove last item
```

#### Real-World: Codebase Documentation Generation

```python
# Generate documentation for entire module
from pathlib import Path
import glob

cm = ContextManager()
cm.set_max_tokens(16384)  # Large context for comprehensive docs

# Find all Python files in module
module_files = list(Path("src/mymodule/").glob("*.py"))

# Add all files
for file_path in sorted(module_files):
    if file_path.name != "__init__.py":  # Skip __init__
        cm.add_file(file_path)

print(cm.get_context_summary())

# Generate documentation prompt
doc_prompt = """
Analyze the provided codebase and generate comprehensive documentation including:

1. Module Overview
2. Class Descriptions
3. Function Reference
4. Usage Examples
5. Dependencies

Format the output as Markdown suitable for a README.md file.
"""

full_prompt = cm.build_context_prompt(doc_prompt)

# Send to large model for documentation
response = ai_router.run_model(
    model_id="llama33-70b",  # Large model for comprehensive analysis
    model_data=ai_router.models["llama33-70b"],
    prompt=full_prompt
)

# Save generated documentation
Path("README.md").write_text(response.text, encoding='utf-8')
print("Documentation generated: README.md")
```

### Text Context Addition

```python
# Add arbitrary text context (not from files)
cm = ContextManager()

# Add API documentation
api_docs = """
Authentication API:
- POST /auth/login - Username/password login
- POST /auth/logout - End session
- GET /auth/status - Check authentication status
"""

cm.add_text(api_docs, label="API Endpoints")

# Add requirements
requirements = """
Requirements:
- Must support OAuth 2.0
- Rate limit: 100 requests/minute
- Response time < 200ms
"""

cm.add_text(requirements, label="System Requirements")

# Build prompt
prompt = "Design an authentication system that meets these requirements"
full_prompt = cm.build_context_prompt(prompt)
```

### Supported Languages

All 30+ languages with automatic file extension detection:

| Category | Languages |
|----------|-----------|
| **Backend** | Python, JavaScript, TypeScript, Java, C++, C, Rust, Go, Ruby, PHP |
| **Frontend** | HTML, CSS, SCSS, SASS, JavaScript, TypeScript, Vue, Svelte |
| **Data/Config** | JSON, YAML, TOML, XML, INI, SQL |
| **Scripts** | Bash, Shell, Zsh, PowerShell, Makefile, Dockerfile |
| **Other** | Swift, Kotlin, Scala, R, Markdown |

### Security & Path Validation

```python
# Path traversal protection
cm = ContextManager()

# Safe: File within current directory
cm.add_file(Path("src/module.py"))  # ✓ Allowed

# Blocked: Path traversal attempt
try:
    cm.add_file(Path("../../../etc/passwd"))
except ValueError as e:
    print(f"Blocked: {e}")
    # Output: Access denied: Path '../../../etc/passwd' is outside the allowed base directory

# Blocked: Absolute path outside project
try:
    cm.add_file(Path("/etc/shadow"))
except ValueError as e:
    print(f"Blocked: {e}")
```

### Integration with Other Features

#### Workflow Engine Integration

```yaml
# workflow.yaml
steps:
  - name: load_context
    type: context
    files:
      - "src/main.py"
      - "src/utils.py"

  - name: analyze_code
    type: prompt
    model: qwen3-coder-30b
    prompt: "Analyze this codebase for security vulnerabilities"
    use_context: true
```

#### Session Management Integration

```python
# Save context with session
from session_manager import SessionManager

sm = SessionManager(Path(".ai-router-sessions.db"))
cm = ContextManager()

# Add context
cm.add_file(Path("important_code.py"))

# Create session with context metadata
session_id = sm.create_session(
    model_id="qwen3-coder-30b",
    model_name="Qwen3 Coder",
    title="Code review with context"
)

# Save context summary to session metadata
sm.add_message(
    session_id,
    "system",
    cm.get_context_summary(),
    tokens=0
)

# Use context in prompt
full_prompt = cm.build_context_prompt("Review this code")
response = ai_router.run_model(model_id, model_data, full_prompt)

sm.add_message(session_id, "user", "Review this code", tokens=50)
sm.add_message(session_id, "assistant", response.text, tokens=response.tokens_output)
```

### Performance Tips

1. **Load Files Once**: Cache file content if using same context repeatedly
2. **Prioritize Files**: Add most important files first (truncation keeps early items)
3. **Estimate Before Loading**: Check file size before adding to avoid over-limit
4. **Chunk Large Files**: Split very large files and add most relevant sections
5. **Clear Context**: Always clear context between unrelated tasks

### Troubleshooting

#### Issue: File not found

**Cause**: Incorrect path or file doesn't exist

**Solution**: Use absolute paths or verify existence
```python
file_path = Path("myfile.py").resolve()
if not file_path.exists():
    print(f"File not found: {file_path}")
else:
    cm.add_file(file_path)
```

#### Issue: Context exceeds token limit

**Cause**: Too many/large files

**Solution**: Remove low-priority items or increase limit
```python
# Check before adding
if cm.get_total_tokens() + estimated_tokens > cm.max_tokens:
    print("Would exceed limit, skipping file")
else:
    cm.add_file(file_path)

# Or use truncation
full_prompt = cm.build_context_prompt(prompt, truncate=True)
```

#### Issue: Wrong language detected

**Cause**: Unusual file extension

**Solution**: Explicitly set language (not currently supported, future enhancement)
```python
# Workaround: Use add_text with code block
code = Path("unusual.xyz").read_text()
cm.add_text(f"```python\n{code}\n```", label="unusual.xyz (Python)")
```

### Best Practices

1. **Label Files Clearly**: Use descriptive labels for easier context management
2. **Monitor Token Usage**: Check get_total_tokens() regularly
3. **Prioritize Context**: Add most relevant files first
4. **Clear Between Tasks**: Start fresh context for unrelated prompts
5. **Use Appropriate Models**: Larger context requires models with higher token limits
6. **Validate Paths**: Always check file existence before adding
7. **Handle Encoding**: Ensure files are UTF-8 encoded
8. **Security Conscious**: Never bypass path validation
9. **Document Context**: Save context summary with sessions for reproducibility
10. **Test Token Estimates**: Validate that estimates align with actual model token counts

### FAQ

**Q: How accurate is token estimation?**

A: The words * 1.3 heuristic is approximately 85-90% accurate for English text. Actual tokenization varies by model. For precise counts, use model-specific tokenizers.

**Q: Can I add binary files or images?**

A: No, ContextManager only supports text files. For images, use vision-capable models directly.

**Q: How do I add only part of a large file?**

```python
# Read and slice file
full_content = Path("large_file.py").read_text()
relevant_section = "\n".join(full_content.split("\n")[100:200])  # Lines 100-200

cm.add_text(relevant_section, label="large_file.py (lines 100-200)")
```

**Q: Can I modify context after adding?**

```python
# Remove and re-add
cm.remove_context_item(0)  # Remove first item
cm.add_file(Path("updated_file.py"))
```

**Q: How do I prevent context truncation?**

```python
# Option 1: Increase limit
cm.set_max_tokens(16384)

# Option 2: Disable truncation (may exceed model limits)
try:
    full_prompt = cm.build_context_prompt(prompt, truncate=False)
except ValueError as e:
    print(f"Prompt too large: {e}")
```

---

## 9. Workflow Automation (Prompt Chaining)

### Overview

The Workflow Automation system enables creation of sophisticated multi-step AI workflows using YAML configuration files, supporting prompt chaining, variable passing, conditional branching, loops, and error handling. By defining sequences of AI operations that build upon each other's outputs, you can automate complex tasks like research-summarize-report pipelines, iterative code generation and refinement, multi-stage content creation, and data processing workflows—all without writing Python code.

Perfect for repetitive multi-step tasks, team workflow standardization, automated content pipelines, and building reusable AI automation templates.

### Key Capabilities

- **YAML-Based Configuration**: Define workflows in human-readable YAML files
- **Variable Substitution**: Pass data between steps using {{variable}} syntax
- **Multiple Step Types**: prompt, template, conditional, loop, extract, sleep
- **Conditional Execution**: if-then-else logic based on variable values
- **Loops**: Iterate over lists and process each item
- **Data Extraction**: Use regex to extract specific data from responses
- **Error Handling**: Continue or stop on errors with per-step configuration
- **Template Integration**: Use prompt templates within workflows
- **Auto Model Selection**: Use "auto" for intelligent model selection
- **Progress Callbacks**: Monitor workflow execution in real-time
- **Result Persistence**: Save workflow outputs as JSON
- **Workflow Validation**: Pre-execution validation of YAML structure

### Architecture

```
WorkflowEngine (workflow_engine.py)
├── YAML Parser
│   ├── load_workflow()
│   ├── validate_workflow()
│   └── Metadata extraction
├── Execution Engine
│   ├── execute_workflow()
│   ├── Step type handlers
│   └── Progress tracking
├── Step Types
│   ├── Prompt: Execute model with prompt
│   ├── Template: Use prompt template
│   ├── Conditional: If-then-else branching
│   ├── Loop: Iterate over items
│   ├── Extract: Regex extraction
│   └── Sleep: Delay execution
├── Variable System
│   ├── _substitute_variables()
│   ├── _evaluate_condition()
│   └── Variable storage
└── Management Functions
    ├── list_workflows()
    └── save_workflow_results()
```

### Complete API Reference

#### WorkflowEngine Class

```python
class WorkflowEngine:
    def __init__(self, workflows_dir: Path, ai_router)
    def load_workflow(self, workflow_path: Path) -> WorkflowExecution
    def execute_workflow(self, execution: WorkflowExecution,
                        progress_callback: Optional[Callable] = None) -> Dict
    def validate_workflow(self, workflow_path: Path) -> tuple[bool, List[str]]
    def list_workflows(self) -> List[Dict]
    def save_workflow_results(self, execution: WorkflowExecution, output_file: Path)
```

#### WorkflowExecution Dataclass

```python
@dataclass
class WorkflowExecution:
    workflow_id: str
    workflow_name: str
    steps: List[WorkflowStep]
    variables: Dict[str, Any]
    results: Dict[str, Any]
    status: str  # pending|running|completed|failed
    current_step: int
    error_message: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
```

### Configuration Options

#### Step Type Reference

| Step Type | Purpose | Required Fields |
|-----------|---------|-----------------|
| **prompt** | Execute AI model | prompt, model (optional) |
| **template** | Use prompt template | template_id, variables (optional) |
| **conditional** | If-then-else logic | condition, then, else (optional) |
| **loop** | Iterate over items | items_var, body |
| **extract** | Extract data with regex | from_step, pattern (optional) |
| **sleep** | Delay execution | duration (seconds) |

### Detailed Usage Examples

#### Basic: Two-Step Research Workflow

```yaml
# research_workflow.yaml
id: research_and_summarize
name: Research Topic and Summarize
description: Research a topic then create executive summary

variables:
  topic: "Artificial Intelligence"
  depth: "intermediate"

steps:
  - name: research
    type: prompt
    model: qwen25-14b
    prompt: "Research {{topic}} at {{depth}} level. Provide comprehensive overview."
    output_var: research_results

  - name: summarize
    type: prompt
    model: phi4-14b
    prompt: |
      Create an executive summary of this research:

      {{research_results}}

      Format: 3-5 bullet points, each max 2 sentences.
    output_var: final_summary
```

```python
from workflow_engine import WorkflowEngine
from pathlib import Path

# Initialize
we = WorkflowEngine(workflows_dir=Path("workflows/"), ai_router=router)

# Load workflow
workflow = we.load_workflow(Path("workflows/research_workflow.yaml"))

# Override variables
workflow.variables['topic'] = "Quantum Computing"
workflow.variables['depth'] = "expert"

# Execute
results = we.execute_workflow(workflow)

print(results['final_summary'])

# Output:
# • Quantum computing leverages quantum superposition and entanglement...
# • Current systems achieve 50-100 qubits with error rates around 0.1%...
# • Applications include cryptography, drug discovery, optimization...
```

#### Intermediate: Conditional Workflow with Branching

```yaml
# code_analysis_workflow.yaml
id: code_analysis
name: Code Analysis with Quality Check
description: Analyze code and take action based on quality score

variables:
  code_file: "my_module.py"
  quality_threshold: "7"

steps:
  - name: analyze_code
    type: prompt
    model: qwen3-coder-30b
    prompt: |
      Analyze this code and rate its quality (1-10):

      [File content: {{code_file}}]

      Provide: Quality score (number only), then explanation.
    output_var: analysis_result

  - name: extract_score
    type: extract
    from_step: analyze_code
    pattern: 'Quality score: (\d+)'
    output_var: quality_score

  - name: check_quality
    type: conditional
    condition: "{{quality_score}} >= {{quality_threshold}}"
    then:
      type: prompt
      model: phi4-14b
      prompt: "Code quality is good ({{quality_score}}/10). Generate optimization suggestions."
      output_var: improvement_suggestions
    else:
      type: prompt
      model: qwen3-coder-30b
      prompt: "Code quality is low ({{quality_score}}/10). Refactor this code completely."
      output_var: refactored_code
```

```python
# Execute conditional workflow
workflow = we.load_workflow(Path("workflows/code_analysis_workflow.yaml"))

# Provide code file
workflow.variables['code_file'] = Path("my_module.py").read_text()

results = we.execute_workflow(workflow)

# Results contain either improvement_suggestions OR refactored_code
# depending on quality score
if 'improvement_suggestions' in results:
    print("Good code! Suggestions:", results['improvement_suggestions'])
else:
    print("Code refactored:", results['refactored_code'])
```

#### Advanced: Loop-Based Batch Processing

```yaml
# batch_translate_workflow.yaml
id: batch_translation
name: Batch Translation with Quality Check
description: Translate multiple texts and verify quality

variables:
  texts:
    - "Hello world"
    - "Good morning"
    - "How are you?"
  target_language: "Spanish"

steps:
  - name: translate_all
    type: loop
    items_var: texts
    loop_var: current_text
    body:
      type: prompt
      model: gemma3-27b
      prompt: "Translate to {{target_language}}: {{current_text}}"
      output_var: translation
    output_var: all_translations

  - name: create_summary
    type: prompt
    model: phi4-14b
    prompt: |
      Create a translation summary report:

      Source texts: {{texts}}
      Translations: {{all_translations}}
      Language: {{target_language}}

      Format as markdown table.
    output_var: translation_report
```

```python
# Execute loop workflow
workflow = we.load_workflow(Path("workflows/batch_translate_workflow.yaml"))

# Provide custom texts
workflow.variables['texts'] = [
    "Welcome to our website",
    "Please enter your password",
    "Thank you for your order"
]
workflow.variables['target_language'] = "French"

results = we.execute_workflow(workflow)

print("Translations:", results['all_translations'])
print("\nReport:\n", results['translation_report'])

# Output:
# Translations: ['Bienvenue sur notre site', 'Veuillez entrer votre mot de passe', ...]
#
# Report:
# | English | French |
# |---------|--------|
# | Welcome to our website | Bienvenue sur notre site |
# ...
```

#### Real-World: Content Generation Pipeline

```yaml
# content_pipeline.yaml
id: blog_post_pipeline
name: Complete Blog Post Generation Pipeline
description: Research → Outline → Write → Edit → SEO → Publish

variables:
  topic: "The Future of AI in Healthcare"
  target_length: "1500"
  audience: "healthcare professionals"

steps:
  - name: research
    type: prompt
    model: qwen25-14b
    prompt: "Research {{topic}}. Find 5 key points and recent statistics."
    output_var: research_data

  - name: create_outline
    type: prompt
    model: phi4-14b
    prompt: |
      Create blog post outline for {{topic}}
      Research: {{research_data}}
      Audience: {{audience}}
      Length: {{target_length}} words
    output_var: outline

  - name: write_draft
    type: prompt
    model: gemma3-27b
    prompt: |
      Write blog post following this outline:
      {{outline}}

      Requirements:
      - Engaging introduction
      - Clear sections
      - Conclusion with call-to-action
      - Target length: {{target_length}} words
    output_var: draft_content

  - name: edit_draft
    type: prompt
    model: phi4-14b
    prompt: |
      Edit this draft for clarity, grammar, and flow:
      {{draft_content}}

      Keep the same length and structure.
    output_var: edited_content

  - name: add_seo
    type: prompt
    model: qwen25-14b
    prompt: |
      Add SEO elements to this blog post:
      {{edited_content}}

      Add:
      - Meta description (150 chars)
      - 5 relevant keywords
      - Internal linking suggestions
    output_var: final_post_with_seo

  - name: sleep_before_publish
    type: sleep
    duration: 2  # Simulate review period

  - name: extract_meta
    type: extract
    from_step: add_seo
    pattern: 'Meta description: (.*)'
    output_var: meta_description
```

```python
# Execute full pipeline
workflow = we.load_workflow(Path("workflows/content_pipeline.yaml"))

# Customize
workflow.variables['topic'] = "Edge Computing in Manufacturing"
workflow.variables['target_length'] = "2000"

# Progress callback
def show_progress(execution, step):
    print(f"[{execution.current_step + 1}/{len(execution.steps)}] {step.name}")

results = we.execute_workflow(workflow, progress_callback=show_progress)

# Save final post
Path("blog_posts/edge_computing.md").write_text(
    results['final_post_with_seo'],
    encoding='utf-8'
)

print(f"\nMeta description: {results['meta_description']}")
print(f"Blog post saved!")
```

### Variable Substitution

```python
# Variables use {{name}} syntax
variables:
  author: "John Doe"
  date: "2025-12-09"

prompt: "Written by {{author}} on {{date}}"
# Result: "Written by John Doe on 2025-12-09"

# Nested access (future enhancement)
variables:
  config:
    model: "qwen3-coder-30b"

prompt: "Using model: {{config.model}}"
```

### Conditional Logic

Supported conditions:

```yaml
# Equality
condition: "{{status}} == 'complete'"

# Inequality
condition: "{{score}} != '0'"

# Contains
condition: "{{response}} contains 'error'"

# Existence
condition: "{{result}} exists"
```

### Error Handling

```yaml
steps:
  - name: risky_operation
    type: prompt
    model: qwen3-coder-30b
    prompt: "{{potentially_invalid_input}}"
    on_error: continue  # Options: continue, stop (default)

  - name: next_step
    type: prompt
    # This runs even if risky_operation fails (when on_error: continue)
```

### Template Integration

```yaml
# Use existing prompt templates in workflows
steps:
  - name: code_review
    type: template
    template_id: code-review.yaml
    variables:
      language: "{{detected_language}}"
      code: "{{source_code}}"
      focus_areas: "security, performance"
    output_var: review_results
```

### Workflow Validation

```python
# Validate before execution
from workflow_engine import WorkflowEngine

we = WorkflowEngine(workflows_dir=Path("workflows/"), ai_router=router)

# Validate YAML structure
is_valid, errors = we.validate_workflow(Path("workflows/my_workflow.yaml"))

if not is_valid:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Workflow is valid!")
    workflow = we.load_workflow(Path("workflows/my_workflow.yaml"))
    results = we.execute_workflow(workflow)
```

### Saving Workflow Results

```python
# Save complete execution results
we.save_workflow_results(
    execution=workflow_execution,
    output_file=Path("results/blog_pipeline_2025-12-09.json")
)

# Saved JSON contains:
# - All step results
# - All variables
# - Execution metadata (start/end time, duration, status)
# - Error messages (if any)
```

### Integration with Other Features

#### Batch Processor Integration

```python
# Create workflow for each item in batch
from batch_processor import BatchProcessor

bp = BatchProcessor(checkpoint_dir=Path("checkpoints/"))
we = WorkflowEngine(workflows_dir=Path("workflows/"), ai_router=router)

# Load workflow template
workflow_template = Path("workflows/analyze_code.yaml")

# Execute workflow for each code file
code_files = list(Path("src/").glob("*.py"))

for code_file in code_files:
    workflow = we.load_workflow(workflow_template)
    workflow.variables['code_file'] = code_file.read_text()
    workflow.variables['filename'] = code_file.name

    results = we.execute_workflow(workflow)

    # Save individual results
    we.save_workflow_results(
        workflow,
        Path(f"results/{code_file.stem}_analysis.json")
    )
```

#### Response Processor Integration

```python
# Extract and save code from workflow results
from response_processor import ResponseProcessor

rp = ResponseProcessor(output_dir=Path("workflow_outputs/"))

# Execute workflow
results = we.execute_workflow(workflow)

# Extract code blocks from result
if 'generated_code' in results:
    code_blocks = rp.extract_code_blocks(results['generated_code'])
    rp.save_code_blocks(results['generated_code'], "workflow_output")
```

### Performance Tips

1. **Minimize Steps**: Combine operations when possible to reduce overhead
2. **Use Auto Selection**: Let ModelSelector choose optimal models
3. **Cache Workflow Files**: Load YAML once, execute multiple times with different variables
4. **Parallel Execution**: Future enhancement for independent steps
5. **Stream Large Results**: For very large workflows, save intermediate results

### Troubleshooting

#### Issue: Variable not substituted

**Cause**: Typo in variable name or missing variable

**Solution**: Check variable names
```python
# Debug variables
workflow = we.load_workflow(workflow_path)
print("Available variables:", workflow.variables.keys())

# Validate all variables used in prompts exist
```

#### Issue: Workflow fails at specific step

**Cause**: Error in step execution

**Solution**: Add error handling
```yaml
- name: potentially_failing_step
  type: prompt
  model: qwen3-coder-30b
  prompt: "{{input}}"
  on_error: continue  # Continue even if this fails
```

#### Issue: Slow workflow execution

**Cause**: Many steps or large models

**Solution**: Monitor execution time
```python
def progress_with_timing(execution, step):
    elapsed = (datetime.now() - execution.start_time).total_seconds()
    print(f"[{elapsed:.1f}s] Step {step.name}")

we.execute_workflow(workflow, progress_callback=progress_with_timing)
```

### Best Practices

1. **Start Simple**: Begin with 2-3 steps, add complexity gradually
2. **Validate Early**: Run validate_workflow() before execution
3. **Use Descriptive Names**: Clear step names make debugging easier
4. **Save Results**: Always save workflow results for auditing
5. **Handle Errors**: Use on_error for robust workflows
6. **Document Variables**: Comment required variables in YAML
7. **Version Workflows**: Use git to track workflow changes
8. **Test Incrementally**: Test each step individually before full workflow
9. **Monitor Progress**: Use progress callbacks for long workflows
10. **Reuse Templates**: Create reusable workflow templates for common tasks

### FAQ

**Q: Can I call one workflow from another?**

Future enhancement. Currently, use separate executions:
```python
workflow1_results = we.execute_workflow(workflow1)
workflow2.variables['input_from_workflow1'] = workflow1_results['output']
workflow2_results = we.execute_workflow(workflow2)
```

**Q: How do I debug a failing workflow?**

```python
# Run with detailed progress
def debug_progress(execution, step):
    print(f"\n{'='*60}")
    print(f"Step: {step.name}")
    print(f"Type: {step.step_type}")
    print(f"Variables: {execution.variables}")
    print(f"{'='*60}")

try:
    results = we.execute_workflow(workflow, progress_callback=debug_progress)
except Exception as e:
    print(f"Failed at step {workflow.current_step}: {e}")
    print(f"Last results: {workflow.results}")
```

**Q: Can I pause and resume workflows?**

Not currently supported. Workaround: Save results and create continuation workflow:
```yaml
# continuation_workflow.yaml
variables:
  previous_results: "{{load from saved results}}"

steps:
  - name: continue_from_step_5
    # ... remaining steps
```

**Q: How do I handle user input during workflow execution?**

Workflows are fully automated. For interactive workflows, use Python with workflow as template:
```python
workflow = we.load_workflow(workflow_path)

# Inject user input as variables
user_input = input("Enter topic: ")
workflow.variables['topic'] = user_input

results = we.execute_workflow(workflow)
```

**Q: What's the maximum number of steps per workflow?**

No hard limit, but recommend <20 steps per workflow for maintainability. For larger workflows, break into sub-workflows.

---

_End of Features 6-9 Complete Documentation_
