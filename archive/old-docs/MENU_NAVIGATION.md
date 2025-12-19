# AI Router Enhanced - Menu Navigation Flowchart

## Document Overview

**Purpose:** Visual representation of menu hierarchy and navigation paths
**Date:** December 8, 2025
**Format:** ASCII art flowcharts and diagrams
**File:** D:\models\ai-router.py

---

## Main Menu Structure (ASCII Flowchart)

```
                    ┌─────────────────────────────────────┐
                    │   AI ROUTER ENHANCED MAIN MENU      │
                    │         (interactive_mode)          │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │      User Input: [0-10, A]          │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
  ┌─────────┐              ┌──────────────┐           ┌─────────────┐
  │ CORE    │              │ PROMPT/      │           │ ADVANCED    │
  │ (1-2)   │              │ CONTEXT      │           │ (5-6)       │
  └────┬────┘              │ (3-4)        │           └──────┬──────┘
       │                   └──────┬───────┘                  │
       │                          │                          │
       ├──[1] Auto-Select         ├──[3] Context Mgmt ❌     ├──[5] Batch
       │      └─> auto_select_    │      └─> context_mode()  │      └─> batch_mode()
       │          mode()           │          MISSING!        │          ├─> From File
       │                           │                          │          ├─> Manual
       └──[2] Browse Models        └──[4] Session Mgmt       │          ├─> Resume
              └─> list_models()           └─> session_mode() │          └─> List
                                           ├─> List           │
                                           ├─> Search         └──[6] Workflow
                                           ├─> Resume             └─> workflow_mode()
                                           ├─> View                   ├─> Run
                                           ├─> Export                 ├─> List
                                           └─> Cleanup                ├─> Create
                                                                      └─> Validate

        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌─────────┐              ┌──────────────┐           ┌─────────────┐
  │ ANALYTICS│              │ INFO/DOCS    │           │ SETTINGS    │
  │ (7)      │              │ (8-10)       │           │ (A, 0)      │
  └────┬─────┘              └──────┬───────┘           └──────┬──────┘
       │                           │                          │
       └──[7] Analytics            ├──[8] System Prompts      ├──[A] Toggle Auto-Yes
              └─> analytics_mode() │      └─> view_system_    │      └─> toggle_bypass_
                  ├─> Dashboard    │          prompts()        │          mode()
                  └─> Export       │                           │
                                   ├──[9] Parameters Guide     └──[0] Exit
                                   │      └─> view_parameters_        └─> sys.exit(0)
                                   │          guide()
                                   │
                                   └──[10] Documentation
                                          └─> view_documentation()
                                              ├─> List Docs
                                              └─> View File

```

---

## Proposed Menu Structure (With Missing Features)

```
                    ┌─────────────────────────────────────┐
                    │   AI ROUTER ENHANCED MAIN MENU      │
                    │   (REORGANIZED WITH ALL 9 FEATURES) │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │    User Input: [1-9, A-D, S, Q]     │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────────────┐
        │                          │                                  │
        ▼                          ▼                                  ▼
  ┌──────────┐            ┌───────────────┐                  ┌──────────────┐
  │ CORE     │            │ PROMPT/       │                  │ ADVANCED     │
  │ (1-2)    │            │ CONTEXT       │                  │ (6-9)        │
  └─────┬────┘            │ (3-5)         │                  └──────┬───────┘
        │                 └───────┬───────┘                         │
        │                         │                                 │
  [1] Auto-Select           [3] Templates ⭐NEW                [6] Comparison ⭐NEW
      auto_select_mode()        template_mode()                   comparison_mode()
        │                         ├─> Browse                         ├─> Quick Compare
        │                         ├─> Create                         ├─> Multi Compare
        │                         ├─> Edit                           └─> History
        │                         ├─> Delete
  [2] Browse Models               └─> Use Template             [7] Post-Process ⭐NEW
      list_models()                                                post_process_mode()
                              [4] Context Mgmt 🔧FIX               ├─> Format
                                  context_mode()                    ├─> Export
                                  ├─> Load File                     └─> Custom
                                  ├─> Load Multiple
                                  ├─> Clipboard                 [8] Batch Processing
                                  └─> Clear                         batch_mode()
                                                                    ├─> From File
                              [5] Session Mgmt                      ├─> Manual
                                  session_mode()                    ├─> Resume
                                  ├─> List                          └─> List
                                  ├─> Search
                                  ├─> Resume                    [9] Workflow
                                  ├─> View                          workflow_mode()
                                  ├─> Export                        ├─> Run
                                  └─> Cleanup                       ├─> List
                                                                    ├─> Create
                                                                    └─> Validate

        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌─────────┐              ┌──────────────┐           ┌─────────────┐
  │ ANALYTICS│              │ INFO & DOCS  │           │ SETTINGS    │
  │ (A)      │              │ (B-D)        │           │ (S, Q)      │
  └────┬─────┘              └──────┬───────┘           └──────┬──────┘
       │                           │                          │
  [A] Analytics              [B] System Prompts         [S] Settings
      analytics_mode()           view_system_prompts()       toggle_bypass_mode()
      ├─> Dashboard                                           Toggle Auto-Yes
      └─> Export             [C] Parameters
                                 view_parameters_guide()  [Q] Exit
                                                              sys.exit(0)
                             [D] Documentation
                                 view_documentation()
                                 ├─> List
                                 └─> View

LEGEND:
⭐NEW = Feature needs to be added to menu
🔧FIX = Method implementation needed
```

---

## Session Management Sub-Navigation

```
┌────────────────────────────────────────┐
│  SESSION MANAGEMENT MENU               │
│  (session_mode - line 902)             │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-6, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┬─────────────┐
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  [1]         [2]         [3]           [4]           [5]
  List        Search      Resume        View          Export
  Sessions    Sessions    Session       Details       Session
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  list_      search_     resume_      view_         export_
  sessions_  sessions_   session()    session_      session_
  interactive() interactive()         details()     interactive()
    │           │           │             │             │
    │           │           │             │             │
    │           │           ├─> continue_session()     │
    │           │           │                          │
    │           │           └─> display_session_       │
    │           │               details()              │
    │           │                                      │
    ▼           ▼                                      ▼
  Display     Enter                                  Choose format
  all         search                                 Export to file
  sessions    term
              │
              ▼
            Show
            matching
            sessions

    │
    ▼
  [6] Cleanup
      cleanup_sessions()
      │
      └─> Delete old sessions

    │
    ▼
  [0] Back to Main Menu
```

---

## Batch Processing Sub-Navigation

```
┌────────────────────────────────────────┐
│  BATCH PROCESSING MENU                 │
│  (batch_mode - line 1463)              │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-4, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┐
    │           │           │             │
    ▼           ▼           ▼             ▼
  [1]         [2]         [3]           [4]
  From        Manual      Resume        List
  File        Prompts     Checkpoint    Checkpoints
    │           │           │             │
    ▼           ▼           ▼             ▼
  batch_      batch_      batch_        batch_list_
  from_file() manual_     resume_       checkpoints()
              prompts()   checkpoint()
    │           │           │             │
    ▼           ▼           │             ▼
  Enter       Enter       │             Display all
  filename    prompts     │             saved checkpoints
    │           │         │
    │           │         └─> Select checkpoint
    └───────────┴────────────┐
                             │
                             ▼
                    batch_run_job()
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
           For each prompt        Save checkpoint
                │                   every N items
                │                         │
                ▼                         │
           run_model()                    │
                │                         │
                ▼                         │
        display_batch_progress()          │
                │                         │
                └─────────────────────────┘
                             │
                             ▼
                       Show results
                             │
                             ▼
                    [0] Back to Main Menu
```

---

## Workflow Automation Sub-Navigation

```
┌────────────────────────────────────────┐
│  WORKFLOW AUTOMATION MENU              │
│  (workflow_mode - line 1797)           │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-4, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┐
    │           │           │             │
    ▼           ▼           ▼             ▼
  [1]         [2]         [3]           [4]
  Run         List        Create        Validate
  Workflow    Workflows   from          Workflow
              │           Template      │
    │         │           │             │
    ▼         ▼           ▼             ▼
workflow_   workflow_   workflow_     workflow_
run()       list()      create_from_  validate()
                        template()
    │         │           │             │
    │         │           │             │
    ▼         ▼           ▼             ▼
Select      Display     Choose        Load workflow
workflow    all         template      file
    │       workflows   type          │
    │         │           │           │
    ▼         │           ▼           ▼
Execute       │         Create        Check steps
chain of      │         workflow      Check variables
prompts       │         definition    Check logic
    │         │           │           │
    │         │           ▼           ▼
    │         │         Save          Show results
    │         │         workflow      (valid/invalid)
    │         │           │           │
    └─────────┴───────────┴───────────┘
                    │
                    ▼
              [0] Back to Main Menu
```

---

## Analytics Dashboard Sub-Navigation

```
┌────────────────────────────────────────┐
│  ANALYTICS DASHBOARD                   │
│  (analytics_mode - line 1197)          │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-2, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
  [1]                     [2]
  View                    Export
  Dashboard               Analytics
    │                       │
    ▼                       ▼
  Display:              export_
  - Total queries       analytics()
  - Model usage stats     │
  - Avg response time     │
  - Success rate          ▼
  - Usage by category   Choose format
  - Charts/graphs       (JSON, CSV, etc)
    │                     │
    │                     ▼
    │                   Save to file
    │                     │
    └─────────────────────┘
                │
                ▼
          [0] Back to Main Menu
```

---

## Documentation Viewer Sub-Navigation

```
┌────────────────────────────────────────┐
│  DOCUMENTATION MENU                    │
│  (view_documentation - line 1350)      │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Scan docs/ folder   │
    └───────────┬───────────┘
                │
                ▼
        List all .md files
                │
    ┌───────────┴───────────┬──────────────┐
    │                       │              │
    ▼                       ▼              ▼
  [1] File 1              [2] File 2     [N] File N
    │                       │              │
    └───────────┬───────────┴──────────────┘
                │
                ▼
        Select file number
                │
                ▼
          Read file
                │
                ▼
        Display content
          (with paging)
                │
                ▼
          [0] Back
```

---

## Proposed: Template Mode Sub-Navigation (NEW - To Be Implemented)

```
┌────────────────────────────────────────┐
│  PROMPT TEMPLATES MENU                 │
│  (template_mode - TO BE IMPLEMENTED)   │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-5, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┬─────────────┐
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  [1]         [2]         [3]           [4]           [5]
  Browse      Create      Edit          Delete        Use
  Templates   New         Template      Template      Template
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  List all    Enter       Select        Select        Select
  available   template    template      template      template
  templates   details     to edit       to delete     to use
    │           │           │             │             │
    │           │           ▼             ▼             ▼
    │           │         Modify        Confirm       Load template
    │           │         fields        deletion      │
    │           │           │             │           │
    │           │           ▼             ▼           ▼
    │           │         Save          Delete       Fill variables
    │           │         changes       template      │
    │           │           │             │           │
    │           ▼           │             │           ▼
    │         Save          │             │         Execute prompt
    │         template      │             │         with template
    │           │           │             │           │
    └───────────┴───────────┴─────────────┴───────────┘
                            │
                            ▼
                    [0] Back to Main Menu
```

---

## Proposed: Model Comparison Sub-Navigation (NEW - To Be Implemented)

```
┌────────────────────────────────────────┐
│  MODEL COMPARISON MENU                 │
│  (comparison_mode - TO BE IMPLEMENTED) │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-3, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┐
    │           │           │             │
    ▼           ▼           ▼             ▼
  [1]         [2]         [3]           [0]
  Quick       Multi-      View          Back
  Compare     Model       History
  (2 models)  Compare
    │           │           │
    ▼           ▼           ▼
  Select      Select      List all
  Model 1     2+ models   past
    │           │         comparisons
    ▼           │           │
  Select        │           │
  Model 2       │           │
    │           │           │
    └─────┬─────┘           │
          │                 │
          ▼                 │
    Enter prompt            │
          │                 │
          ▼                 │
    Run on both/all         │
    models in parallel      │
          │                 │
          ▼                 │
    Display results         │
    side-by-side            │
          │                 │
          ▼                 │
    Show metrics:           │
    - Response time         │
    - Token count           │
    - Quality score         │
          │                 │
          ▼                 │
    Save comparison         │
          │                 │
          └─────────────────┘
                │
                ▼
          [0] Back to Main Menu
```

---

## Proposed: Post-Processing Sub-Navigation (NEW - To Be Implemented)

```
┌────────────────────────────────────────┐
│  RESPONSE POST-PROCESSING MENU         │
│  (post_process_mode - TO BE IMPL.)     │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-4, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┬─────────────┐
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  [1]         [2]         [3]           [4]           [0]
  Format      Export      Custom        Process       Back
  Response    to File     Processor     Last
                                        Response
    │           │           │             │
    ▼           ▼           ▼             ▼
  Choose      Choose      Select        Load last
  format:     format:     processor     model output
  - Markdown  - TXT       type            │
  - HTML      - JSON        │             │
  - Plain     - PDF         │             ▼
  - Code      - MD          │         Apply processing
    │           │           │             │
    ▼           ▼           ▼             │
  Apply       Save to     Apply           │
  formatting  file        custom          │
    │           │         transform       │
    │           │           │             │
    └───────────┴───────────┴─────────────┘
                │
                ▼
          Display result
                │
                ▼
          [0] Back to Main Menu
```

---

## Proposed: Context Management Sub-Navigation (FIX - To Be Implemented)

```
┌────────────────────────────────────────┐
│  CONTEXT MANAGEMENT MENU               │
│  (context_mode - TO BE IMPLEMENTED)    │
└───────────────┬────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Choose: [1-5, 0]    │
    └───────────┬───────────┘
                │
    ┌───────────┼───────────┬─────────────┬─────────────┐
    │           │           │             │             │
    ▼           ▼           ▼             ▼             ▼
  [1]         [2]         [3]           [4]           [5]
  Load        Load        Load from     View          Clear
  Single      Multiple    Clipboard     Context       Context
  File        Files                     │             │
    │           │           │           │             │
    ▼           ▼           ▼           ▼             ▼
  Enter       Enter       Paste       Display       Confirm
  file        glob        text        current       clear
  path        pattern       │         loaded          │
    │           │           │         files/text      │
    │           │           │           │             ▼
    │           ▼           │           │         Clear all
    │         Select        │           │         context
    │         files         │           │             │
    │           │           │           │             │
    └─────┬─────┴───────────┴───────────┘             │
          │                                           │
          ▼                                           │
    Add to context manager                            │
          │                                           │
          ▼                                           │
    Confirm loaded                                    │
          │                                           │
          └───────────────────────────────────────────┘
                            │
                            ▼
                    [0] Back to Main Menu
```

---

## Complete Navigation Map (All Paths)

```
START: python ai-router.py
    │
    ▼
print_banner()
    │
    ▼
interactive_mode()
    │
    ├─[1]─> auto_select_mode() ───────────────────────────────> run_model() ──> OUTPUT
    │
    ├─[2]─> list_models() ─> manual_select_mode() ──> run_model() ──> OUTPUT
    │
    ├─[3]─> context_mode() ❌ MISSING
    │         │
    │         └─> [Should implement]
    │             ├─ Load file(s)
    │             ├─ Load clipboard
    │             ├─ View context
    │             └─ Clear context
    │
    ├─[4]─> session_mode()
    │         ├─[1]─> list_sessions_interactive()
    │         ├─[2]─> search_sessions_interactive()
    │         ├─[3]─> resume_session() ──> continue_session()
    │         ├─[4]─> view_session_details() ──> display_session_details()
    │         ├─[5]─> export_session_interactive()
    │         └─[6]─> cleanup_sessions()
    │
    ├─[5]─> batch_mode()
    │         ├─[1]─> batch_from_file() ──────┐
    │         ├─[2]─> batch_manual_prompts() ─┤
    │         ├─[3]─> batch_resume_checkpoint()┤
    │         └─[4]─> batch_list_checkpoints() │
    │                                          │
    │                  ┌───────────────────────┘
    │                  ▼
    │             batch_run_job() ──> run_model() (loop) ──> OUTPUT
    │
    ├─[6]─> workflow_mode()
    │         ├─[1]─> workflow_run()
    │         ├─[2]─> workflow_list()
    │         ├─[3]─> workflow_create_from_template()
    │         └─[4]─> workflow_validate()
    │
    ├─[7]─> analytics_mode()
    │         ├─[1]─> Display dashboard
    │         └─[2]─> export_analytics()
    │
    ├─[8]─> view_system_prompts()
    │
    ├─[9]─> view_parameters_guide()
    │
    ├─[10]─> view_documentation()
    │          └─> Select file ──> Display content
    │
    ├─[A]─> toggle_bypass_mode()
    │         └─> Toggle self.bypass_mode
    │
    └─[0]─> sys.exit(0) ──> END


MISSING FEATURES (Not in current menu):

    ⚠️ template_mode() ──> [Should add as option 3]
         ├─ Browse templates
         ├─ Create new
         ├─ Edit existing
         ├─ Delete template
         └─ Use template

    ⚠️ comparison_mode() ──> [Should add as option 6]
         ├─ Quick compare (2 models)
         ├─ Multi-model compare
         └─ View history

    ⚠️ post_process_mode() ──> [Should add as option 7]
         ├─ Format response
         ├─ Export to file
         └─ Custom processors
```

---

## User Journey Examples

### Journey 1: First-Time User - Auto-Select

```
1. Start: python ai-router.py
   │
   ▼
2. See banner and main menu
   │
   ▼
3. Choose [1] Auto-select
   │
   ▼
4. Enter prompt: "explain quantum computing"
   │
   ▼
5. System analyzes prompt
   │
   ▼
6. Shows: Category=Educational, Model=Qwen2.5:14b, Confidence=85%
   │
   ▼
7. Confirm or change model
   │
   ▼
8. Model runs, displays response
   │
   ▼
9. Back to main menu
```

**Path:** START → interactive_mode() → [1] → auto_select_mode() → run_model() → OUTPUT → MENU

---

### Journey 2: Power User - Batch Processing with Templates

```
1. Start with context loaded
   │
   ▼
2. Choose [3] Templates ⚠️ (when implemented)
   │
   ▼
3. Select "Code Review" template
   │
   ▼
4. Back to menu, choose [8] Batch Processing
   │
   ▼
5. Choose [1] From File
   │
   ▼
6. Select file with multiple code snippets
   │
   ▼
7. Select model (e.g., DeepSeek Coder)
   │
   ▼
8. Batch processes all with progress bar
   │
   ▼
9. Checkpoint saved after each 5 items
   │
   ▼
10. View results, export to file
    │
    ▼
11. Back to main menu
```

**Path:** START → [3] template_mode() → [8] batch_mode() → [1] batch_from_file() → batch_run_job() → OUTPUT

---

### Journey 3: Analyst - Model Comparison

```
1. Start application
   │
   ▼
2. Choose [6] Model Comparison ⚠️ (when implemented)
   │
   ▼
3. Choose [1] Quick Compare
   │
   ▼
4. Select Model 1: Qwen2.5:14b
   │
   ▼
5. Select Model 2: DeepSeek R1:14b
   │
   ▼
6. Enter test prompt
   │
   ▼
7. Both models run in parallel
   │
   ▼
8. Side-by-side comparison displayed
   │
   ▼
9. Metrics shown (time, tokens, quality)
   │
   ▼
10. Save comparison for history
    │
    ▼
11. Back to menu
```

**Path:** START → [6] comparison_mode() → Quick Compare → parallel run_model() → Comparison Display

---

### Journey 4: Researcher - Session Resume

```
1. Start application
   │
   ▼
2. Choose [5] Session Management
   │
   ▼
3. Choose [2] Search Sessions
   │
   ▼
4. Search for "research project"
   │
   ▼
5. Found 3 matching sessions
   │
   ▼
6. Select session from 2 days ago
   │
   ▼
7. View session details (10 previous prompts)
   │
   ▼
8. Choose to resume
   │
   ▼
9. Continue conversation with context
   │
   ▼
10. New prompts saved to same session
    │
    ▼
11. Export session when done
```

**Path:** START → [5] session_mode() → [2] search → resume_session() → continue_session() → [5] export

---

## Back Navigation Summary

All sub-menus should provide clear "back" options:

```
Main Menu
    │
    ├── Sub-Menu Level 1 (e.g., Session Management)
    │     │
    │     ├── Action 1
    │     ├── Action 2
    │     ├── Action 3
    │     └── [0] Back to Main Menu ←─────┐
    │                                     │
    └─────────────────────────────────────┘

CURRENT IMPLEMENTATION:
- All sub-menus use [0] to go back
- Consistent pattern across all features
- No deep nesting (max 2 levels)

RECOMMENDATION:
- Keep [0] as universal back
- Consider [Q] as quick exit from anywhere
- Implement breadcrumbs for context
```

---

## Error Paths & Edge Cases

```
Main Menu
    │
    ├── Invalid Input (not 0-10, A)
    │     │
    │     └──> Display error message
    │           │
    │           └──> Return to menu (no crash)
    │
    ├── Feature Not Implemented (e.g., context_mode)
    │     │
    │     └──> Error: Method not found
    │           │
    │           └──> Returns to menu (currently crashes!)
    │
    ├── File Not Found (templates, docs, etc.)
    │     │
    │     └──> Error message displayed
    │           │
    │           └──> Graceful return to menu
    │
    └── Empty Input (user presses Enter)
          │
          └──> Request input again OR treat as cancel
```

**Current Issues:**
- Missing `context_mode()` will cause AttributeError
- Need try/except wrappers for robustness
- Invalid file paths need better handling

---

## Navigation Performance

**Menu Loading Times (estimated):**

```
interactive_mode()        <10ms    (instant)
list_models()            <50ms    (11 models)
session_mode()           <100ms   (database query)
batch_mode()             <50ms    (instant)
workflow_mode()          <100ms   (file system scan)
analytics_mode()         <200ms   (data aggregation)
view_documentation()     <300ms   (file scanning + WSL path detection)
```

**Optimization Opportunities:**
- Cache model list (currently regenerated each time)
- Lazy load documentation file list
- Pre-fetch session count for display

---

## Accessibility Navigation

```
Keyboard-Only Navigation:
    │
    ├── Number keys (1-9)
    ├── Letter keys (A-D, S, Q)
    ├── Enter to confirm
    ├── 0 to go back
    └── Future: Arrow keys for menu cursor

Screen Reader Support:
    │
    ├── All options have clear text labels
    ├── Numbers announced before feature names
    ├── Status indicators (ON/OFF) clearly stated
    └── Emojis optional (can be disabled)

Future Enhancements:
    │
    ├── Tab key navigation
    ├── Vim-style keys (h/j/k/l)
    ├── Custom key bindings
    └── Mouse support (if terminal supports it)
```

---

## Summary Statistics

**Current Menu:**
- Total menu options: 12
- Core features: 2
- Tools/Advanced: 4
- Info/Docs: 3
- Settings: 1
- Exit: 1
- Missing implementations: 1 (context_mode)

**Proposed Menu:**
- Total menu options: 15
- Core features: 2
- Tools: 3 (Templates, Context, Sessions)
- Advanced: 4 (Comparison, Post-Process, Batch, Workflow)
- Analytics: 1
- Info/Docs: 3
- Settings: 1
- Exit: 1
- Missing implementations: 4 (context_mode, template_mode, comparison_mode, post_process_mode)

**Navigation Depth:**
- Maximum depth: 2 levels (Main → Sub-menu)
- Average options per menu: 4-6
- Total navigation paths: ~45+

---

**Document Version:** 1.0
**Last Updated:** December 8, 2025
**Status:** Complete - Ready for Implementation
