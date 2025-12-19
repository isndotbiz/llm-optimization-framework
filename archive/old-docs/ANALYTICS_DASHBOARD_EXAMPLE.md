# Analytics Dashboard Example Output

## Overview
The Performance Analytics Dashboard provides comprehensive usage statistics and insights for the AI Router application.

## Sample Dashboard Output

```
======================================================================
  PERFORMANCE ANALYTICS DASHBOARD
  Period: Last 7 days
  Generated: 2025-12-08 21:16:36
======================================================================

USAGE STATISTICS
----------------------------------------------------------------------
  Total Sessions:                 2
  Total Messages:                 4
    |- User Messages:             2
    +- AI Responses:              2
  Total Tokens:                 310
  Avg Tokens/Message:          77.5

MODEL USAGE
----------------------------------------------------------------------
  phi4-14b             ########################################     1 ( 50.0%)
  qwen3-coder-30b      ########################################     1 ( 50.0%)

DAILY ACTIVITY (Last 1 days)
----------------------------------------------------------------------
  #
  #
  #
  #
  #
  #
  #
  #
  #
  #
  -
  9

  Peak: 4 messages/day

PERFORMANCE METRICS
----------------------------------------------------------------------
  Avg Response Time:           1.85 seconds

RECOMMENDATIONS
----------------------------------------------------------------------
  1. Try exploring different models to find your favorites
```

## Features

### 1. Usage Statistics
- Total sessions created
- Total messages (user + assistant)
- Token usage tracking
- Average tokens per message

### 2. Model Usage Chart
- Horizontal bar chart showing model popularity
- Top 10 models by usage count
- Percentage distribution

### 3. Daily Activity Chart
- ASCII sparkline chart showing daily message volume
- Shows last 14 days of activity
- Peak activity indicator

### 4. Performance Metrics
- Average response time across all models
- Token throughput analysis

### 5. Smart Recommendations
- AI-driven usage recommendations based on patterns
- Suggestions for optimization
- Feature discovery prompts

## Access Methods

### From Main Menu
1. Launch AI Router: `python ai-router.py`
2. Select option `[6] Analytics Dashboard`
3. Choose time period:
   - Last 7 days
   - Last 30 days
   - All time
   - Export to JSON

### Menu Options
```
ANALYTICS DASHBOARD
╔══════════════════════════════════════════════════════════════╗
║  ANALYTICS DASHBOARD                                         ║
╚══════════════════════════════════════════════════════════════╝

[1] View dashboard (last 7 days)
[2] View dashboard (last 30 days)
[3] View dashboard (all time)
[4] Export statistics to JSON
[0] Back to main menu
```

## Export Functionality

Analytics can be exported to JSON format for:
- Long-term tracking
- External analysis
- Sharing with team members
- Integration with other tools

### Export Example
```json
{
  "generated_at": "2025-12-08T21:16:36.123456",
  "period_days": 7,
  "usage_statistics": {
    "total_sessions": 2,
    "total_messages": 4,
    "user_messages": 2,
    "assistant_messages": 2,
    "total_tokens": 310,
    "avg_tokens": 77.5
  },
  "model_usage": [
    {"model": "phi4-14b", "count": 1},
    {"model": "qwen3-coder-30b", "count": 1}
  ],
  "daily_activity": [
    {"date": "2025-12-08", "count": 4}
  ],
  "avg_response_time": 1.85
}
```

## Database Views

The analytics system creates several SQL views for advanced querying:

### model_performance
Aggregates usage statistics by model including:
- Session count
- Message count
- Average tokens
- Total tokens
- Average duration

### daily_stats
Daily aggregation of:
- Session count
- Models used
- Total messages
- Total tokens

### hourly_activity
Shows usage patterns by hour of day

### session_quality
Analyzes session engagement metrics:
- Tokens per message
- Seconds per message
- Engagement level classification

### token_usage_trends
Tracks token consumption over time by model

### response_time_analysis
Analyzes model response performance:
- Average response time
- Min/max response times
- Tokens per second

## Recommendations System

The dashboard provides intelligent recommendations based on:

1. **Low Usage** (< 10 sessions)
   - "Try exploring different models to find your favorites"

2. **High Token Usage** (avg > 5000 tokens/message)
   - "Consider using context management to reduce token usage"

3. **Low Model Diversity** (using only 1 model)
   - "Try model comparison mode to explore alternative models"

4. **High Engagement** (> 50 sessions)
   - "Great engagement! Consider exporting analytics for tracking"

5. **Very High Usage** (> 100 sessions)
   - "For repetitive tasks, consider batch processing workflows"

## Integration Points

### AIRouter Class
- `analytics` property: AnalyticsDashboard instance
- `analytics_mode()`: Interactive analytics menu
- `export_analytics()`: JSON export functionality

### SessionManager Integration
- Direct access to session database
- Real-time statistics
- Historical data analysis

## Files Created

1. **D:\models\analytics_dashboard.py**
   - AnalyticsDashboard class implementation
   - All visualization methods
   - Test suite included

2. **D:\models\analytics_schema.sql**
   - Database views for analytics
   - Indexes for performance
   - Helper views for common queries

3. **D:\models\ai-router.py** (modified)
   - Added analytics import
   - Initialized analytics dashboard
   - Added analytics menu option (6)
   - Added analytics_mode() method
   - Added export_analytics() method
   - Updated menu to include Analytics Dashboard

## Testing

The analytics dashboard includes a built-in test suite:

```bash
python analytics_dashboard.py
```

This creates a temporary database with sample data and displays the dashboard.

## Future Enhancements

Potential additions to the analytics system:

1. **Response Time Tracking**
   - Add `response_time_ms` column to messages table
   - Track per-model performance

2. **Session Tags**
   - Categorize sessions by type
   - Filter analytics by category

3. **Model Version Tracking**
   - Track which model versions are used
   - Compare performance across versions

4. **Cost Tracking**
   - If using API models, track costs
   - Budget alerts

5. **Comparison Mode**
   - Side-by-side model comparison
   - A/B testing results

## Database Maintenance

For optimal analytics performance, run periodically:

```sql
VACUUM;
ANALYZE;
```

This optimizes the database and updates query statistics.

## Summary

The Performance Analytics Dashboard provides comprehensive insights into AI Router usage, helping users:
- Understand usage patterns
- Optimize model selection
- Track token consumption
- Improve workflow efficiency
- Make data-driven decisions

All analytics are generated from the existing session database with no additional overhead during normal operation.
