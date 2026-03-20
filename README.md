# Mental Health Agent System 

Multi-agent mental health support platform. 

## Run it 
```bash
cd mental-health-agent-system-offline
bash run.sh
```

Opens automatically at **http://localhost:8000**

## Manual run (even simpler)

```bash
python3 server.py
```

Then open http://localhost:8000 in your browser.

## How it works



| File | What it does |
|------|-------------|
| `server.py` | Python web server + rule-based agent logic |
| `index.html` | Full UI (no framework, no build step) |
| `run.sh` | One-command launcher |

## The 5 agents

| Agent | Speciality |
|-------|-----------|
| 🎯 Triage | First contact, severity assessment, routing |
| 🧠 CBT | Cognitive distortions, thought records, reframing |
| 🛟 Crisis | Safety protocols, de-escalation, crisis resources |
| 🌿 Mindfulness | Box breathing, 5-4-3-2-1 grounding, body scans |
| 📓 Journal | Reflective prompts, gratitude, values clarification |

## Requirements

- Python 3 
- That's it

## ⚠️ Disclaimer

Demo system only. Not a substitute for professional mental health care.

**Crisis resources:**
- 988 Suicide & Crisis Lifeline — call or text **988**
- Crisis Text Line — text **HOME** to **741741**
