# Research-Optimized Model Runner
# Automatically loads best system prompts and parameters for each model

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        'Llama70B', 'Qwen3Coder', 'DolphinVenice', 'Phi4', 'Gemma3',
        'Ministral3', 'DeepSeekR1', 'WizardVicuna', 'Dolphin8B',
        'Qwen14BInstruct', 'Qwen14BUncensored', 'Llama8B', 'QwenCoder7B'
    )]
    [string]$Model,

    [Parameter(Mandatory=$true)]
    [string]$UserPrompt,

    [int]$MaxTokens = 512,

    [switch]$UseOptimalContext  # Use recommended context size instead of default
)

# Model configuration database (synced with research findings)
$ModelConfigs = @{
    'Llama70B' = @{
        Path = 'D:\models\organized\Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf'
        SystemPrompt = 'D:\models\organized\Llama-3.3-70B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 6000
        TopP = 0.95
        TopK = 40
        RepeatPenalty = 1.05
        Format = 'llama'
    }
    'Qwen3Coder' = @{
        Path = 'D:\models\organized\Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
        SystemPrompt = 'D:\models\organized\Qwen3-Coder-30B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 131072
        TopP = 0.8
        TopK = 20
        RepeatPenalty = 1.05
        ExtraFlags = '--jinja --enable-chunked-prefill --max-num-batched-tokens 131072'
        Format = 'chatml'
    }
    'DolphinVenice' = @{
        Path = 'D:\models\organized\cognitivecomputations_Dolphin-Mistral-24B-Venice-Edition-Q4_K_M.gguf'
        SystemPrompt = 'D:\models\organized\Dolphin-Mistral-24B-SYSTEM-PROMPT.txt'
        Temp = 0.15
        Context = 16384
        TopP = 0.95
        TopK = 40
        RepeatPenalty = 1.1
        Format = 'chatml'
    }
    'Phi4' = @{
        Path = 'D:\models\organized\microsoft_Phi-4-reasoning-plus-Q6_K.gguf'
        SystemPrompt = 'D:\models\organized\Phi-4-Reasoning-Plus-SYSTEM-PROMPT.txt'
        Temp = 0.8
        Context = 16384
        TopP = 0.9
        TopK = 25
        RepeatPenalty = 1.05
        ExtraFlags = '--jinja'
        Format = 'chatml'
    }
    'Gemma3' = @{
        Path = 'D:\models\organized\mlabonne_gemma-3-27b-it-abliterated-Q2_K.gguf'
        SystemPrompt = 'D:\models\organized\Gemma-3-27B-SYSTEM-PROMPT.txt'
        Temp = 1.0
        Context = 100000
        MinP = 0.08
        TopK = 50
        RepeatPenalty = 1.2
        FrequencyPenalty = 0.5
        Format = 'gemma_special'
        Note = 'NO SYSTEM PROMPT SUPPORT - prompt file contains user framing instructions'
    }
    'Ministral3' = @{
        Path = 'D:\models\organized\Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf'
        SystemPrompt = 'D:\models\organized\Ministral-3-14B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 200000
        TopP = 0.95
        TopK = 30
        RepeatPenalty = 1.05
        Format = 'mistral'
    }
    'DeepSeekR1' = @{
        Path = 'D:\models\organized\DeepSeek-R1-Distill-Qwen-14B-Q5_K_M.gguf'
        SystemPrompt = 'D:\models\organized\DeepSeek-R1-SYSTEM-PROMPT.txt'
        Temp = 0.6
        Context = 32768
        TopP = 0.95
        TopK = 30
        Format = 'deepseek_special'
        Note = 'NO SYSTEM PROMPT - prompt file contains user template only'
    }
    'WizardVicuna' = @{
        Path = 'D:\models\organized\Wizard-Vicuna-13B-Uncensored-Q4_0.gguf'
        SystemPrompt = 'D:\models\organized\Wizard-Vicuna-13B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 16384
        TopP = 0.95
        TopK = 40
        RepeatPenalty = 1.1
        Format = 'vicuna'
    }
    'Dolphin8B' = @{
        Path = 'D:\models\organized\Dolphin3.0-Llama3.1-8B-Q6_K.gguf'
        SystemPrompt = 'D:\models\organized\Dolphin-3.0-8B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 24576
        TopP = 0.95
        TopK = 40
        RepeatPenalty = 1.1
        Format = 'chatml'
    }
    'Qwen14BInstruct' = @{
        Path = 'D:\models\rtx4060ti-16gb\qwen25-14b-instruct\Qwen2.5-14B-Instruct-Q4_K_M.gguf'
        SystemPrompt = 'D:\models\rtx4060ti-16gb\Qwen-14B-Instruct-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 32768
        TopP = 0.8
        TopK = 40
        RepeatPenalty = 1.05
        ExtraFlags = '--jinja'
        Format = 'chatml'
    }
    'Qwen14BUncensored' = @{
        Path = 'D:\models\rtx4060ti-16gb\qwen25-14b-uncensored\Qwen2.5-14B_Uncensored_Instruct-Q4_K_M.gguf'
        SystemPrompt = 'D:\models\rtx4060ti-16gb\Qwen-14B-Uncensored-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 32768
        TopP = 0.8
        TopK = 40
        RepeatPenalty = 1.05
        ExtraFlags = '--jinja'
        Format = 'chatml'
    }
    'Llama8B' = @{
        Path = 'D:\models\rtx4060ti-16gb\llama31-8b-instruct\Meta-Llama-3.1-8B-Instruct-Q6_K.gguf'
        SystemPrompt = 'D:\models\rtx4060ti-16gb\Llama-3.1-8B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 32768
        TopP = 0.9
        TopK = 50
        RepeatPenalty = 1.05
        Format = 'llama'
    }
    'QwenCoder7B' = @{
        Path = 'D:\models\rtx4060ti-16gb\qwen25-coder-7b\qwen2.5-coder-7b-instruct-q5_k_m.gguf'
        SystemPrompt = 'D:\models\rtx4060ti-16gb\Qwen-Coder-7B-SYSTEM-PROMPT.txt'
        Temp = 0.7
        Context = 32768
        TopP = 0.9
        TopK = 20
        RepeatPenalty = 1.2
        ExtraFlags = '--jinja'
        Format = 'chatml'
    }
}

$Config = $ModelConfigs[$Model]

# Load system prompt
$SystemPromptContent = Get-Content $Config.SystemPrompt -Raw

# Special handling for models with non-standard prompt formats
if ($Config.Format -eq 'gemma_special') {
    Write-Host "`n⚠️  NOTE: Gemma models don't support system prompts!" -ForegroundColor Yellow
    Write-Host "Using prompt framing template from file instead.`n" -ForegroundColor Yellow
    $FullPrompt = $SystemPromptContent + "`n`n" + $UserPrompt
    $SystemPromptContent = ""  # No system prompt for Gemma
}
elseif ($Config.Format -eq 'deepseek_special') {
    Write-Host "`n⚠️  NOTE: DeepSeek-R1 performs worse with system prompts!" -ForegroundColor Yellow
    Write-Host "Using user prompt template only.`n" -ForegroundColor Yellow
    $FullPrompt = $SystemPromptContent.Replace('[Problem statement here]', $UserPrompt)
    $SystemPromptContent = ""  # No system prompt for DeepSeek
}
else {
    $FullPrompt = $UserPrompt
}

# Build llama.cpp command with optimal parameters
$ContextSize = if ($UseOptimalContext) { $Config.Context } else { 8192 }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RUNNING: $Model" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📊 Parameters:" -ForegroundColor Green
Write-Host "   Temperature: $($Config.Temp)"
Write-Host "   Context: $ContextSize tokens"
Write-Host "   Top-P: $($Config.TopP)"
Write-Host "   Top-K: $($Config.TopK)"
Write-Host "   Repeat Penalty: $($Config.RepeatPenalty)"
if ($Config.MinP) { Write-Host "   Min-P: $($Config.MinP)" }
if ($Config.FrequencyPenalty) { Write-Host "   Frequency Penalty: $($Config.FrequencyPenalty)" }
Write-Host ""

# Convert to WSL path
$WslModelPath = $Config.Path -replace 'D:\\', '/mnt/d/' -replace '\\', '/'

# Build command
$Cmd = "wsl bash -c `"~/llama.cpp/build/bin/llama-cli -m '$WslModelPath'"

# Add system prompt if not special case
if ($SystemPromptContent -and $Config.Format -ne 'gemma_special' -and $Config.Format -ne 'deepseek_special') {
    $EscapedSystemPrompt = $SystemPromptContent -replace '"', '\"' -replace '`', '\`'
    $Cmd += " -p '$EscapedSystemPrompt`n`nUser: $FullPrompt`n`nAssistant:'"
}
else {
    $EscapedPrompt = $FullPrompt -replace '"', '\"' -replace '`', '\`'
    $Cmd += " -p '$EscapedPrompt'"
}

# Add parameters
$Cmd += " --temp $($Config.Temp)"
$Cmd += " -c $ContextSize"
$Cmd += " --top-p $($Config.TopP)"
$Cmd += " --top-k $($Config.TopK)"
$Cmd += " --repeat-penalty $($Config.RepeatPenalty)"
if ($Config.MinP) { $Cmd += " --min-p $($Config.MinP)" }
if ($Config.FrequencyPenalty) { $Cmd += " --frequency-penalty $($Config.FrequencyPenalty)" }
$Cmd += " -n $MaxTokens"
$Cmd += " -t 24 -b 2048 --no-ppl -ngl 99"

# Add extra flags if specified
if ($Config.ExtraFlags) {
    $Cmd += " $($Config.ExtraFlags)"
}

$Cmd += "`""

# Execute
Write-Host "🚀 Executing...`n" -ForegroundColor Green
Invoke-Expression $Cmd

Write-Host "`n`n✅ Complete!" -ForegroundColor Green