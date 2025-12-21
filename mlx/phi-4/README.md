---
license: mit
license_link: https://huggingface.co/microsoft/phi-4/resolve/main/LICENSE
language:
- en
pipeline_tag: text-generation
tags:
- phi
- nlp
- math
- code
- chat
- conversational
- mlx
inference:
  parameters:
    temperature: 0
widget:
- messages:
  - role: user
    content: How should I explain the Internet?
library_name: transformers
base_model: microsoft/phi-4
---

# mlx-community/phi-4-4bit

The Model [mlx-community/phi-4-4bit](https://huggingface.co/mlx-community/phi-4-4bit) was
converted to MLX format from [microsoft/phi-4](https://huggingface.co/microsoft/phi-4)
using mlx-lm version **0.21.0**.

## Use with mlx

```bash
pip install mlx-lm
```

```python
from mlx_lm import load, generate

model, tokenizer = load("mlx-community/phi-4-4bit")

prompt = "hello"

if tokenizer.chat_template is not None:
    messages = [{"role": "user", "content": prompt}]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True
    )

response = generate(model, tokenizer, prompt=prompt, verbose=True)
```
