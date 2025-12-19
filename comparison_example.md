# Model Comparison Report

**Comparison ID:** a1b2c3d4-e5f6-7890-abcd-ef1234567890

**Timestamp:** 2025-12-08 14:30:45

**Models Compared:** 3

## Prompt

```
Write a Python function to calculate the factorial of a number
```

## Performance Metrics

| Model | Input Tokens | Output Tokens | Duration | Tokens/Sec |
| ----- | ------------ | ------------- | -------- | ---------- |
| Qwen3 Coder 30B Q4_K_M | 45 | 120 | 4.50s | 26.7 |
| Phi-4 Reasoning Plus 14B Q6_K | 45 | 85 | 2.10s | 40.5 |
| Dolphin 3.0 Llama 3.1 8B Q6_K | 45 | 40 | 0.90s | 44.4 |

## Responses

### 1. Qwen3 Coder 30B Q4_K_M

**Model ID:** `qwen3-coder-30b`

**Response:**

```
def factorial(n):
    """
    Calculate the factorial of a number.

    Args:
        n (int): Non-negative integer

    Returns:
        int: Factorial of n
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

### 2. Phi-4 Reasoning Plus 14B Q6_K

**Model ID:** `phi4-14b`

**Response:**

```
def factorial(n):
    """Calculate factorial using iteration for better performance."""
    if n < 0:
        raise ValueError("Factorial undefined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

### 3. Dolphin 3.0 Llama 3.1 8B Q6_K

**Model ID:** `dolphin-llama31-8b`

**Response:**

```
import math

def factorial(n):
    """Calculate factorial using Python's built-in math module."""
    return math.factorial(n)
```

## Notes

Dolphin provided the most concise solution using stdlib. Phi-4 had the best balance of performance and clarity. Qwen3 provided the most detailed documentation but used recursion which is less efficient.

## Winner

**Selected Model:** dolphin-llama31-8b
