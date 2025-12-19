# Workflow Builder UI Specification

## Overview

This document describes a user interface for building YAML-based LLM workflows visually, allowing non-technical users to create complex multi-step AI workflows without writing code.

## Core Components

### 1. Canvas-Based Workflow Designer

**Visual Flow Editor**
- Drag-and-drop interface for adding workflow steps
- Visual connections between steps showing data flow
- Real-time validation of workflow structure
- Zoom and pan for large workflows
- Grid snapping for alignment
- Mini-map for navigation

**Step Types Available**
- LLM Call (purple icon)
- User Confirmation (blue icon)
- User Input (blue icon)
- Validation (yellow icon)
- Action/API Call (green icon)
- Expression/Calculation (orange icon)
- Conditional Branch (diamond shape)
- Loop (circular arrow)

### 2. Step Configuration Panel

**LLM Call Configuration**
```
┌─ LLM Call Step ────────────────────────────┐
│ Step Name: [Generate Summary            ] │
│ Step ID:   [auto-generated or custom    ] │
│                                            │
│ Model Selection:                           │
│ ○ GPT-4                                    │
│ ○ GPT-3.5 Turbo                            │
│ ○ Claude Sonnet                            │
│ ○ Custom: [____________]                   │
│                                            │
│ Temperature: [0.7] ████████░░ (0-1)        │
│ Max Tokens:  [2000]                        │
│                                            │
│ Prompt Template:                           │
│ ┌────────────────────────────────────────┐ │
│ │ Summarize this text:                   │ │
│ │ {{input_text}}                         │ │
│ │                                        │ │
│ │ Focus on: {{focus_area}}               │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ [Insert Variable ▼]  [Test Prompt]         │
│                                            │
│ Outputs:                                   │
│ ├─ summary (string)                        │
│ └─ [+ Add Output]                          │
│                                            │
│ Dependencies:                              │
│ ├─ extract_text                            │
│ └─ [+ Add Dependency]                      │
│                                            │
│ Condition (optional):                      │
│ [{{steps.check.outputs.proceed == true}}] │
│                                            │
│ [Error Handling ▼]  [Advanced ▼]           │
│                                            │
│ [Cancel]  [Save]  [Save & Test]            │
└────────────────────────────────────────────┘
```

**User Confirmation Configuration**
```
┌─ User Confirmation Step ───────────────────┐
│ Step Name: [Approve Draft              ] │
│                                            │
│ Message to User:                           │
│ ┌────────────────────────────────────────┐ │
│ │ Please review this draft:              │ │
│ │                                        │ │
│ │ {{steps.write_draft.outputs.content}}  │ │
│ │                                        │ │
│ │ Approve to continue?                   │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ Confirmation Options:                      │
│ ☑ Allow Approve                            │
│ ☑ Allow Reject                             │
│ ☑ Allow Request Changes                    │
│                                            │
│ Timeout:                                   │
│ ☑ Enable timeout                           │
│   Duration: [24] [hours ▼]                 │
│   On timeout: [Escalate ▼]                 │
│                                            │
│ Outputs:                                   │
│ └─ approved (boolean)                      │
│                                            │
│ [Cancel]  [Save]                           │
└────────────────────────────────────────────┘
```

**Conditional Branch Configuration**
```
┌─ Conditional Branch ───────────────────────┐
│ Branch Name: [Quality Check            ] │
│                                            │
│ Condition Type:                            │
│ ○ Simple comparison                        │
│ ● Complex expression                       │
│                                            │
│ Expression Builder:                        │
│ ┌────────────────────────────────────────┐ │
│ │ [steps.quality_check.outputs.score ▼]  │ │
│ │ [       >=        ▼]                   │ │
│ │ [       8         ]                    │ │
│ │                                        │ │
│ │ [AND ▼] ─────────────────────────────  │ │
│ │                                        │ │
│ │ [steps.validation.outputs.passed   ▼]  │ │
│ │ [       ==        ▼]                   │ │
│ │ [      true       ]                    │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ True Path: → [publish_content]             │
│ False Path: → [revise_content]             │
│                                            │
│ [Test Condition]  [Cancel]  [Save]         │
└────────────────────────────────────────────┘
```

### 3. Variable Management Panel

```
┌─ Workflow Variables ───────────────────────┐
│                                            │
│ Global Variables                           │
│ ├─ 📝 user_query (string)                  │
│ ├─ 🔢 max_iterations (number) = 3          │
│ ├─ ☑  enable_fallback (boolean) = true    │
│ └─ [+ Add Variable]                        │
│                                            │
│ Step Outputs (Read-only)                   │
│ ├─ 📋 steps.research.outputs               │
│ │  └─ key_points (string)                  │
│ ├─ 📋 steps.expand.outputs                 │
│ │  └─ expanded_content (string)            │
│ └─ 📋 steps.quality_check.outputs          │
│    ├─ score (number)                       │
│    └─ issues (array)                       │
│                                            │
│ [Variable Reference Guide]                 │
└────────────────────────────────────────────┘
```

### 4. Error Handling Configuration

```
┌─ Error Handling ───────────────────────────┐
│                                            │
│ Retry Configuration                        │
│ ☑ Enable retry on failure                 │
│   Max attempts: [3]                        │
│   Backoff strategy: [Exponential ▼]        │
│   Initial delay: [1000] ms                 │
│   Max delay: [10000] ms                    │
│                                            │
│ Retry Conditions:                          │
│ ☑ Network timeout                          │
│ ☑ Rate limit (429)                         │
│ ☑ Service unavailable (503)                │
│ ☐ Custom condition: [_______________]      │
│                                            │
│ Fallback Behavior                          │
│ ○ Continue workflow                        │
│ ○ Skip this step                           │
│ ● Execute fallback step: [backup_llm ▼]   │
│ ○ Pause for human intervention             │
│ ○ Fail workflow                            │
│                                            │
│ On Max Retries Exceeded:                   │
│ [Send notification ▼] to [admin@...   ]    │
│                                            │
│ [Cancel]  [Save]                           │
└────────────────────────────────────────────┘
```

### 5. Workflow Templates Library

```
┌─ Template Gallery ─────────────────────────┐
│                                            │
│ [Search templates...]          [Filter ▼]  │
│                                            │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 📄 Content   │  │ 📊 Data      │        │
│ │ Generation   │  │ Processing   │        │
│ │              │  │              │        │
│ │ 5 steps      │  │ 8 steps      │        │
│ │ ⭐⭐⭐⭐⭐     │  │ ⭐⭐⭐⭐☆     │        │
│ └──[Use]───────┘  └──[Use]───────┘        │
│                                            │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 🎯 Customer  │  │ 📧 Email     │        │
│ │ Support      │  │ Campaign     │        │
│ │              │  │              │        │
│ │ 12 steps     │  │ 10 steps     │        │
│ │ ⭐⭐⭐⭐☆     │  │ ⭐⭐⭐⭐⭐     │        │
│ └──[Use]───────┘  └──[Use]───────┘        │
│                                            │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 🔍 Research  │  │ ✅ Code      │        │
│ │ & Analysis   │  │ Review       │        │
│ │              │  │              │        │
│ │ 7 steps      │  │ 15 steps     │        │
│ │ ⭐⭐⭐⭐☆     │  │ ⭐⭐⭐⭐⭐     │        │
│ └──[Use]───────┘  └──[Use]───────┘        │
│                                            │
│ [Create Custom Template]                   │
└────────────────────────────────────────────┘
```

### 6. Testing & Debugging Panel

```
┌─ Workflow Testing ─────────────────────────┐
│                                            │
│ Test Input Variables                       │
│ ┌────────────────────────────────────────┐ │
│ │ user_query:                            │ │
│ │ "What are the benefits of AI?"         │ │
│ │                                        │ │
│ │ target_audience:                       │ │
│ │ "business executives"                  │ │
│ │                                        │ │
│ │ word_count: 1000                       │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ [Run Full Workflow]  [Step Through]        │
│                                            │
│ Execution Results                          │
│ ┌────────────────────────────────────────┐ │
│ │ ✓ research (2.3s)                      │ │
│ │   Output: key_points = "1. AI auto..." │ │
│ │                                        │ │
│ │ ✓ expand (3.8s)                        │ │
│ │   Output: expanded_content = "AI au..."│ │
│ │                                        │ │
│ │ ⏸ quality_check (paused)               │ │
│ │   Waiting for: LLM response            │ │
│ │                                        │ │
│ │ ⏺ format (not started)                 │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ [Export Test Results]  [Save Test Case]    │
└────────────────────────────────────────────┘
```

## Wizard Mode for Beginners

### Step 1: Choose Workflow Type
```
┌─ Create New Workflow ──────────────────────┐
│                                            │
│ What do you want to accomplish?            │
│                                            │
│ ○ Generate content (articles, posts)       │
│ ○ Process and analyze data                 │
│ ○ Automate customer support                │
│ ○ Review and approve documents             │
│ ○ Research and summarize information       │
│ ○ Custom workflow (advanced)               │
│                                            │
│              [Cancel]  [Next >]            │
└────────────────────────────────────────────┘
```

### Step 2: Define Inputs
```
┌─ Define Workflow Inputs ───────────────────┐
│                                            │
│ What information does your workflow need?  │
│                                            │
│ Input 1:                                   │
│ Name: [topic                           ]   │
│ Type: [Text ▼]                             │
│ ☑ Required                                 │
│                                            │
│ Input 2:                                   │
│ Name: [target_audience                 ]   │
│ Type: [Text ▼]                             │
│ ☑ Required                                 │
│                                            │
│ [+ Add Input]                              │
│                                            │
│         [< Back]  [Cancel]  [Next >]       │
└────────────────────────────────────────────┘
```

### Step 3: Configure Main Steps
```
┌─ Configure Workflow Steps ─────────────────┐
│                                            │
│ Based on your selection, we recommend:     │
│                                            │
│ Step 1: Research topic                     │
│ ☑ Enabled                                  │
│ [Configure...]                             │
│                                            │
│ Step 2: Create outline                     │
│ ☑ Enabled                                  │
│ [Configure...]                             │
│                                            │
│ Step 3: Write draft                        │
│ ☑ Enabled                                  │
│ [Configure...]                             │
│                                            │
│ Step 4: Quality check                      │
│ ☐ Enabled (optional)                       │
│ [Configure...]                             │
│                                            │
│ [+ Add Custom Step]                        │
│                                            │
│         [< Back]  [Cancel]  [Next >]       │
└────────────────────────────────────────────┘
```

### Step 4: Add Human Review Points
```
┌─ Human Review Configuration ───────────────┐
│                                            │
│ When should a human review be required?    │
│                                            │
│ ☑ Before final output                      │
│   Position: [After quality_check ▼]        │
│                                            │
│ ☐ If quality score is low                  │
│   Threshold: [___ ] / 10                   │
│                                            │
│ ☐ After specific steps                     │
│   Steps: [Select... ▼]                     │
│                                            │
│ ☐ At regular intervals                     │
│   Every: [___] steps                       │
│                                            │
│         [< Back]  [Cancel]  [Next >]       │
└────────────────────────────────────────────┘
```

### Step 5: Review & Deploy
```
┌─ Review & Deploy Workflow ─────────────────┐
│                                            │
│ Workflow Summary                           │
│                                            │
│ Name: Content Generation Pipeline          │
│ Type: Content Generation                   │
│ Steps: 5                                   │
│ Approvals: 1                               │
│                                            │
│ Workflow Preview:                          │
│ ┌────────────────────────────────────────┐ │
│ │ [Start] → [Research] → [Outline] →    │ │
│ │ [Draft] → [Quality] → [Review] → [End]│ │
│ └────────────────────────────────────────┘ │
│                                            │
│ ☑ Test workflow before saving              │
│ ☑ Save as template for reuse               │
│                                            │
│    [< Back]  [Test]  [Save & Deploy]       │
└────────────────────────────────────────────┘
```

## Advanced Features

### 1. Version Control
- Track workflow changes over time
- Compare versions side-by-side
- Rollback to previous versions
- Branch and merge workflows

### 2. Collaborative Editing
- Multiple users can edit workflows
- Real-time collaboration indicators
- Comments and annotations on steps
- Change history and audit trail

### 3. Workflow Analytics
- Execution time per step
- Success/failure rates
- Cost tracking (LLM API calls)
- Bottleneck identification
- Usage statistics

### 4. Import/Export
- Export to YAML file
- Import from YAML
- Export to JSON
- Share workflow as link
- Generate documentation

### 5. Variable Intelligence
- Auto-complete for variable references
- Type checking and validation
- Highlight unused variables
- Suggest variable names
- Show variable usage across workflow

## Mobile Considerations

### Responsive Design
- Collapsible panels on smaller screens
- Touch-friendly drag-and-drop
- Swipe gestures for navigation
- Simplified view mode for mobile

### Mobile-First Features
- Quick actions menu
- Voice input for prompts
- Camera integration for document upload
- Push notifications for approvals

## Accessibility

### WCAG 2.1 AA Compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Adjustable text size
- Focus indicators
- Alternative text for icons

## Technical Implementation Notes

### Frontend Stack
- React or Vue.js for UI components
- D3.js or React Flow for canvas visualization
- Monaco Editor for code/YAML editing
- TailwindCSS for styling
- Redux or Zustand for state management

### Backend Integration
- RESTful API for workflow CRUD operations
- WebSocket for real-time collaboration
- GraphQL for complex queries
- File upload handling for imports
- Webhook support for integrations

### Data Persistence
- Draft auto-save every 30 seconds
- Local storage for offline editing
- Cloud sync when online
- Conflict resolution for concurrent edits

## Sample User Flows

### Flow 1: Create Simple Workflow (5 minutes)
1. Click "New Workflow" → Select "Content Generation"
2. Enter workflow name and description
3. Add input variables (topic, audience)
4. Wizard auto-generates 4 basic steps
5. Customize prompts in each step
6. Add approval step before final output
7. Test with sample inputs
8. Deploy workflow

### Flow 2: Modify Existing Workflow (2 minutes)
1. Open workflow from library
2. Click step to edit
3. Update prompt template
4. Add new conditional branch
5. Test changes
6. Save new version

### Flow 3: Debug Failed Workflow (3 minutes)
1. View execution history
2. Identify failed step
3. Review error message
4. Check variable values at failure point
5. Update error handling configuration
6. Re-run from checkpoint

## Export Formats

### YAML Export Example
```yaml
# Exported from Workflow Builder
# Generated: 2025-12-08T10:30:00Z
# Version: 1.0

workflow:
  name: "Content Generation Pipeline"
  version: "1.0"
  description: "Generate blog content with quality checks"

  variables:
    topic: ""
    target_audience: "general"

  steps:
    # ... (as defined in visual editor)
```

### Documentation Export Example
```markdown
# Content Generation Pipeline

**Version:** 1.0
**Created:** 2025-12-08
**Last Modified:** 2025-12-08

## Overview
Generate blog content with quality checks

## Inputs
- `topic` (required): The main topic for content
- `target_audience` (optional): Target reader demographic

## Workflow Steps

### 1. Research (LLM Call)
- Model: GPT-4
- Temperature: 0.3
- Purpose: Research the topic and identify key points
...
```

This specification provides a comprehensive blueprint for building a user-friendly workflow builder that makes YAML-based LLM workflows accessible to both technical and non-technical users.
