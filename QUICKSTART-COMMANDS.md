# TrueNAS AI Router - Quick Start Commands

## 🚀 **Access Your System**

### SSH to Server (No Password Needed!)
```bash
ssh root@10.0.0.89
```

---

## 📊 **Monitor GPU While Running**

```bash
ssh root@10.0.0.89 "watch -n 1 nvidia-smi"
```

Shows real-time:
- GPU Memory usage
- Temperature
- Utilization %

---

## 🤖 **View/Control the Router**

### Watch the Router Log (Live)
```bash
ssh root@10.0.0.89 "tail -f /mnt/models/router.log"
```

### See Running Processes
```bash
ssh root@10.0.0.89 "ps aux | grep ai-router"
```

### Restart Router
```bash
ssh root@10.0.0.89 "pkill -f 'ai-router-truenas-production.py'; sleep 1; cd /mnt/models && nohup python3 ai-router-truenas-production.py > router.log 2>&1 &"
```

---

## 💬 **Use the Router Interactively**

### Connect and Use Menu (SSH)
```bash
ssh root@10.0.0.89
cd /mnt/models
python3 ai-router-truenas-production.py
```

Then in the menu:
```
[1] Create New Project
[2] Load Existing Project
[3] Run Chat Session     ← USE THIS TO CHAT
[4] View Conversation History
[5] Check GPU VRAM Status
[6] View Available Models
[8] Exit
```

---

## 🧪 **Test Models Directly**

### Test Dolphin (Fast Chat)
```bash
ssh root@10.0.0.89 "/root/llama.cpp/build/bin/llama-cli \
  -m /mnt/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf \
  -p 'What is 2+2?' \
  -n 20 \
  -ngl 999"
```

### Test Qwen Coder (Programming)
```bash
ssh root@10.0.0.89 "/root/llama.cpp/build/bin/llama-cli \
  -m /mnt/models/organized/qwen25-coder-7b/qwen2.5-coder-7b-instruct-q5_k_m.gguf \
  -p 'Write a Python function to reverse a string' \
  -n 50 \
  -ngl 999"
```

---

## 📁 **Your Pre-Created Projects**

All ready to use! Just load them in the menu:

- **general-chat** → Dolphin 8B (fast, uncensored)
- **coding** → Qwen Coder 7B (programming)
- **reasoning** → Llama 3.1 Instruct 8B (production-grade)
- **creative** → Qwen 14B Uncensored (creative writing)

---

## 🔧 **Manage Projects (SSH)**

### List all projects
```bash
ssh root@10.0.0.89 "ls -la /mnt/models/projects/"
```

### View a project config
```bash
ssh root@10.0.0.89 "cat /mnt/models/projects/general-chat/config.json"
```

### View conversation history
```bash
ssh root@10.0.0.89 "cat /mnt/models/projects/general-chat/memory.json | python3 -m json.tool | head -50"
```

---

## 📊 **GPU Status**

### Quick GPU Check
```bash
ssh root@10.0.0.89 "nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits"
```

**Output:** `VRAM_Used, VRAM_Total, GPU_Util, Temp_C`

Example: `1, 16380, 0, 37` = 1GB used, 0% load, 37°C

---

## 🛑 **Stop/Start/Check Services**

### Check if running
```bash
ssh root@10.0.0.89 "ps aux | grep 'ai-router-truenas' | grep -v grep"
```

### Kill router
```bash
ssh root@10.0.0.89 "pkill -f 'ai-router-truenas-production.py'"
```

### Start router
```bash
ssh root@10.0.0.89 "cd /mnt/models && nohup python3 ai-router-truenas-production.py > router.log 2>&1 &"
```

### Check log errors
```bash
ssh root@10.0.0.89 "tail -30 /mnt/models/router.log | grep -i error"
```

---

## 📈 **Performance Tips**

### Monitor while inferencing
Open 2 terminals:

**Terminal 1** - Watch GPU:
```bash
watch -n 1 'ssh root@10.0.0.89 "nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits"'
```

**Terminal 2** - Use router:
```bash
ssh root@10.0.0.89
cd /mnt/models
python3 ai-router-truenas-production.py
# Then [2] Load Project → [3] Chat
```

---

## 💡 **Model Selection Guide**

| Model | Size | Speed | Best For | Command |
|-------|------|-------|----------|---------|
| **Dolphin 8B** | 6.2GB | ⚡⚡⚡ | Fast chat, uncensored | `general-chat` project |
| **Qwen Coder 7B** | 5.1GB | ⚡⚡⚡ | Code generation | `coding` project |
| **Llama 3.1 8B** | 6.2GB | ⚡⚡ | Production-grade, reliable | `reasoning` project |
| **Qwen 14B Instruct** | 8.4GB | ⚡⚡ | Balanced, multilingual | Manual load |
| **Qwen 14B Uncensored** | 8.4GB | ⚡⚡ | Creative, roleplay | `creative` project |

---

## 🎯 **Quick Start (Right Now!)**

```bash
# SSH to server
ssh root@10.0.0.89

# Load general chat project
cd /mnt/models
python3 ai-router-truenas-production.py

# Menu appears - press 2
# [2] Load Existing Project

# Select general-chat
# [3] Run Chat Session

# Type your prompt and press Enter!
```

---

## 🔐 **Keep It Running Always**

The router is set up with systemd to auto-restart on failure.

Check status:
```bash
ssh root@10.0.0.89 "systemctl status ai-router"
```

---

**That's it!** You're all set. Enjoy your AI models! 🚀
