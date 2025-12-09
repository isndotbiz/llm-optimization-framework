# System and User Prompt Creator
# Uses Qwen3-Coder-30B for optimal prompt engineering (256K context, structured output)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Create system prompt', 'Create user template', 'Analyze prompt', 'Improve prompt')]
    [string]$Task,

    [string]$UseCase = "",
    [string]$ModelType = "",
    [string]$Category = "",
    [string]$Language = "",
    [string]$PromptFile = "",
    [string]$OutputFile = ""
)

# ===== INSERT YOUR CUSTOM SYSTEM PROMPT HERE =====
# This is where you can customize the prompt engineering assistant's behavior
$CustomSystemPrompt = @"
<|im_start|>system
<role>
You are an expert prompt engineer specializing in creating optimal system prompts and
user prompt templates for large language models. You have deep knowledge of:
- Prompt engineering best practices (2024 research)
- Model-specific optimization (Qwen, Llama, Phi, Mistral, Gemma families)
- XML/Markdown structured prompting
- CRAFT and CO-STAR frameworks
- Research-backed techniques (positive framing, instruction hierarchy, etc.)
</role>

<capabilities>
- Generate production-ready system prompts optimized for specific use cases
- Create user prompt templates that maximize model performance
- Analyze existing prompts and provide detailed improvement recommendations
- Apply cutting-edge research findings (June-December 2024)
</capabilities>

<guidelines>
Use XML-structured prompts when appropriate (proven 40% better performance).
Apply positive framing ("do this" not "don't do that").
Include clear role definition, capabilities, guidelines, and output format.
Optimize for the specific model family's strengths and quirks.
Keep prompts focused (~300 tokens optimal for many use cases).
</guidelines>

<output_format>
Provide complete, ready-to-use prompts with clear formatting.
Include usage instructions and recommended parameters.
Explain design decisions briefly.
</output_format>
<|im_end|>
"@

# Model configuration
$Qwen3CoderPath = "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"

# Build user prompt based on task
$userPrompt = ""

switch ($Task) {
    'Create system prompt' {
        $userPrompt = @"
Create a comprehensive, research-optimized system prompt for:

Use Case: $UseCase
Model Type: $ModelType

Requirements:
1. Use XML-structured format with <role>, <capabilities>, <guidelines>, <output_format> sections
2. Apply positive framing (avoid "don't do" instructions)
3. Include model-specific optimizations if applicable
4. Keep focused and clear (~300-500 tokens)
5. Specify recommended parameters (temperature, top-p, context, etc.)

Provide:
- Complete system prompt ready to use
- Recommended llama.cpp parameters
- Brief explanation of design choices
"@
    }

    'Create user template' {
        $userPrompt = @"
Create optimal user prompt templates for:

Category: $Category
Language/Domain: $Language

Requirements:
1. Create 3-5 reusable prompt patterns for this category
2. Use CRAFT or CO-STAR framework where appropriate
3. Include placeholder variables clearly marked ([VARIABLE])
4. Optimize for structured, predictable outputs
5. Include examples of usage

Provide:
- Multiple template variations
- When to use each template
- Example filled-in prompts
"@
    }

    'Analyze prompt' {
        if (-not (Test-Path $PromptFile)) {
            Write-Host "Error: Prompt file not found: $PromptFile" -ForegroundColor Red
            exit 1
        }

        $promptContent = Get-Content $PromptFile -Raw

        $userPrompt = @"
Analyze this existing prompt and provide detailed improvement recommendations:

```
$promptContent
```

Analyze:
1. Structure and clarity
2. Use of positive vs negative framing
3. Specificity and completeness
4. Alignment with 2024 best practices
5. Model-specific optimizations

Provide:
- Detailed analysis of strengths and weaknesses
- Specific improvement recommendations
- Improved version of the prompt
- Expected performance impact
"@
    }

    'Improve prompt' {
        if (-not (Test-Path $PromptFile)) {
            Write-Host "Error: Prompt file not found: $PromptFile" -ForegroundColor Red
            exit 1
        }

        $promptContent = Get-Content $PromptFile -Raw

        $userPrompt = @"
Improve this prompt using 2024 research-backed best practices:

```
$promptContent
```

Apply:
1. XML structuring if beneficial
2. Positive framing
3. Clear role definition
4. Explicit guidelines and output format
5. Model-specific optimizations

Provide:
- Improved prompt ready to use
- List of changes made and why
- Expected performance improvement
"@
    }
}

# Build llama.cpp command
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PROMPT ENGINEERING ASSISTANT (Qwen3-Coder-30B)" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Task: $Task" -ForegroundColor Green
Write-Host "Model: Qwen3-Coder-30B (256K context, structured output)" -ForegroundColor Green
Write-Host "`nGenerating...`n" -ForegroundColor Yellow

# Escape prompts for bash
$escapedSystemPrompt = $CustomSystemPrompt -replace '"', '\"' -replace '`', '\`'
$escapedUserPrompt = $userPrompt -replace '"', '\"' -replace '`', '\`'

# Construct full prompt with system + user
$fullPrompt = $escapedSystemPrompt + "`n`n<|im_start|>user`n" + $escapedUserPrompt + "`n<|im_end|>`n<|im_start|>assistant`n"

# Run Qwen3-Coder with optimal parameters
$cmd = "wsl bash -c `"~/llama.cpp/build/bin/llama-cli -m '$Qwen3CoderPath' -p '$fullPrompt' --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 -c 32768 -n 2048 -t 24 -b 2048 --no-ppl -ngl 99 --jinja 2>&1`""

$output = Invoke-Expression $cmd

# Extract just the response (after prompt processing)
if ($output -match "assistant\n(.*?)(?:\n\n|$)") {
    $response = $Matches[1]
} else {
    # Fallback: try to find actual response
    $response = $output | Select-String -Pattern "(?s)assistant.*?(\n.*)" | ForEach-Object { $_.Matches[0].Groups[1].Value }
}

# Display result
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  GENERATED PROMPT" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host $output

# Save to file if specified
if ($OutputFile) {
    $output | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host "`n✓ Saved to: $OutputFile" -ForegroundColor Green
}

Write-Host "`n✓ Complete!" -ForegroundColor Green
Write-Host "`nTo customize the prompt engineering assistant, edit the 'CustomSystemPrompt' variable" -ForegroundColor Yellow
Write-Host "in this script (line 15-45)" -ForegroundColor Yellow
