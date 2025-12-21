---
library_name: transformers
base_model: deepseek-ai/DeepSeek-R1-Distill-Llama-8B
tags:
- mlx
---

# mlx-community/DeepSeek-R1-Distill-Llama-8B

The Model [mlx-community/DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/mlx-community/DeepSeek-R1-Distill-Llama-8B) was
converted to MLX format from [deepseek-ai/DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B)
using mlx-lm version **0.21.1** by [Focused](https://focused.io).

[![Focused Logo](https://focused.io/images/header-logo.svg "Focused Logo")](https://focused.io)

## Use with mlx

```bash
pip install mlx-lm
```

```python
from mlx_lm import load, generate

model, tokenizer = load("mlx-community/DeepSeek-R1-Distill-Llama-8B")

prompt = "hello"

if tokenizer.chat_template is not None:
    messages = [{"role": "user", "content": prompt}]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True
    )

response = generate(model, tokenizer, prompt=prompt, verbose=True)
```

---

Focused is a technology company at the forefront of AI-driven development, empowering organizations to unlock the full potential of artificial intelligence. From integrating innovative models into existing systems to building scalable, modern AI infrastructures, we specialize in delivering tailored, incremental solutions that meet you where you are.
Curious how we can help with your AI next project?
[Get in Touch](https://focused.io/capabilities/ai-readiness-implementation)

[![Focused Logo](https://focused.io/images/header-logo.svg "Focused Logo")](https://focused.io)
