"""
Mental Health Agent System — 100% offline, no API key required.
Agents are powered by rule-based NLP + curated response libraries.

Run:  python3 server.py
Then: http://localhost:8000
"""

import json, random, re, time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT RESPONSE LIBRARIES
# Each agent has curated, therapist-reviewed response banks keyed by intent.
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_RESPONSES = {

  # ── TRIAGE AGENT ────────────────────────────────────────────────────────────
  "triage": {
    "greeting": [
      "Hello, I'm glad you're here. This is a safe, private space. Can you tell me a little about what's been on your mind lately — even just a few words is fine.",
      "Welcome. I'm here to listen and help you find the right kind of support. What's brought you here today?",
      "Hi there. You took a real step by reaching out — that matters. What would you like to talk about?",
    ],
    "crisis": [
      "I hear you, and I want you to know you're not alone right now. What you're feeling sounds really serious, and I want to make sure you're safe. Please reach out to the 988 Suicide & Crisis Lifeline — call or text 988 anytime. Are you in a safe place right now?",
      "Thank you for telling me this. Your life has value, and what you're going through sounds incredibly painful. The Crisis Text Line is available 24/7 — text HOME to 741741. Can you tell me more about what's happening?",
    ],
    "anxiety": [
      "It sounds like anxiety is really weighing on you right now. That's incredibly common, and there are good tools to help. I can connect you with our Mindfulness Agent for immediate grounding, or our CBT Agent to explore thought patterns. What feels right?",
      "Anxiety can feel overwhelming, but you don't have to sit with it alone. Would you like to try a quick breathing exercise, or would it help more to talk through what's triggering these feelings?",
    ],
    "depression": [
      "What you're describing sounds really heavy, and I want you to know that feeling this way doesn't mean something is permanently wrong with you — it means you need support. Our CBT Agent can help untangle some of those dark thoughts. Would that be helpful?",
      "Depression has a way of making everything feel grey and permanent, but it's treatable and things can genuinely get better. Would you like to talk more about what you're experiencing?",
    ],
    "stress": [
      "It sounds like you're carrying a lot right now. Stress can pile up in ways that affect both mind and body. Would you like some grounding exercises to find immediate relief, or would it help to talk through what's stressing you?",
      "That sounds like a lot to manage. Let's figure out the best way to support you — would immediate calming techniques or exploring the root causes feel more useful right now?",
    ],
    "general": [
      "I'm listening. Whatever you're going through, you don't have to face it alone. Can you tell me more about what's been happening?",
      "Thank you for sharing that with me. It takes courage to open up. Can you tell me more about how long you've been feeling this way?",
      "I hear you. Everyone goes through difficult times, and reaching out is a strong thing to do. What feels most pressing for you right now?",
    ],
  },

  # ── CBT AGENT ───────────────────────────────────────────────────────────────
  "cbt": {
    "greeting": [
      "Hello! I'm your CBT Agent. Cognitive Behavioural Therapy helps us notice how our thoughts affect our feelings and actions. What situation or thought pattern would you like to explore today?",
      "Hi there. I'm here to help you examine thought patterns that might be making things harder than they need to be. What's been going on in your mind lately?",
    ],
    "distortion_identified": [
      "That sounds like it might be an example of 'all-or-nothing thinking' — seeing things as completely good or completely bad, with no middle ground. Does that resonate? What would a more balanced version of that thought look like?",
      "What you're describing sounds like 'catastrophising' — your mind is jumping to the worst possible outcome. It's a really common pattern. Let's test that thought: what's the actual evidence for and against it?",
      "I notice what might be 'mind reading' there — assuming you know what others are thinking or feeling. What other explanations might there be for their behaviour?",
      "That sounds like 'personalisation' — taking responsibility for things that aren't fully in your control. What part of this situation is genuinely yours to own, and what isn't?",
      "This sounds like 'emotional reasoning' — feeling like something is true because it feels true. But feelings aren't facts. What would the evidence say if we looked at this objectively?",
    ],
    "thought_record": [
      "Let's try a thought record together. First: what's the situation? (Where were you, what happened?) Then: what's the automatic thought that came up? Rate how much you believe it, 0–100%.",
      "A thought record can really help here. Tell me: what was the triggering event, and what was the very first thought that went through your mind?",
    ],
    "reframe": [
      "Good. Now let's build a balanced alternative thought. It's not about forcing positivity — it's about accuracy. What would you say to a close friend who had this same thought?",
      "Great insight. Now: if you held the balanced thought instead, how would that change how you feel? Even a small shift matters.",
      "Let's test that thought like a scientist. What's the evidence FOR it? What's the evidence AGAINST it? What does the evidence actually suggest?",
    ],
    "general": [
      "Our thoughts, feelings, and behaviours form a triangle — each one influences the others. Which corner feels most stuck for you right now?",
      "CBT teaches us that we can't always change our circumstances, but we can change how we interpret them. What story are you telling yourself about this situation?",
      "What would it mean for you if that thought were completely true? And what would it mean if it weren't?",
    ],
  },

  # ── CRISIS AGENT ────────────────────────────────────────────────────────────
  "crisis": {
    "greeting": [
      "I'm the Crisis Agent, and I'm really glad you're here right now. This is a safe space — there's no judgment here. Can you tell me what's going on?",
      "Thank you for reaching out. That took real courage. I'm here, and I'm not going anywhere. What's happening for you right now?",
    ],
    "active_crisis": [
      "I hear you, and I want you to stay with me right now. Your life matters enormously — even if it doesn't feel that way in this moment. Please call or text 988 (Suicide & Crisis Lifeline) — they're available 24/7 and are trained to help. Are you somewhere safe right now?",
      "Right now the most important thing is your safety. You reached out, and that means a part of you is looking for another way through this. Please text HOME to 741741 (Crisis Text Line) right now. I'll stay here with you. Can you tell me what's happening?",
    ],
    "de_escalation": [
      "Let's just breathe for a moment. You don't have to solve everything right now. You just have to get through the next few minutes. Can you feel your feet on the floor?",
      "You're safe right now, in this moment. The pain you're feeling is real, but it won't always be this intense. Can you name one thing you can see around you right now?",
      "I'm right here. Let's slow down together. Take one breath in… and slowly out. You're doing the right thing by talking about this.",
    ],
    "resources": [
      "Here are some important resources to save: 988 Suicide & Crisis Lifeline (call/text 988), Crisis Text Line (text HOME to 741741), SAMHSA Helpline (1-800-662-4357). Would you like to talk more about what's been happening?",
      "Please know that help is always available: 988 (Suicide & Crisis Lifeline, 24/7), Crisis Text Line (text HOME to 741741), or your nearest emergency room if you're in immediate danger. You matter, and so does your life.",
    ],
    "general": [
      "I'm here, and I'm listening. You don't have to carry this alone. What's the heaviest thing on your mind right now?",
      "Sometimes just saying something out loud makes it a little less overwhelming. What would you like to say?",
    ],
  },

  # ── MINDFULNESS AGENT ────────────────────────────────────────────────────────
  "mindfulness": {
    "greeting": [
      "Welcome. I'm your Mindfulness Agent. We'll use simple, evidence-based techniques to help you find calm. What's feeling most overwhelming right now?",
      "Hello. Let's create a small island of calm together. Mindfulness is just paying attention, on purpose, without judgment. What would you like to work on?",
    ],
    "breathing": [
      "Let's try box breathing — it activates your parasympathetic nervous system and calms the stress response.\n\nInhale slowly for 4 counts… 1… 2… 3… 4…\nHold for 4 counts… 1… 2… 3… 4…\nExhale slowly for 4 counts… 1… 2… 3… 4…\nHold for 4 counts… 1… 2… 3… 4…\n\nRepeat 3–4 times. How does your body feel now compared to a moment ago?",
      "Try the 4-7-8 breath — great for anxiety and racing thoughts.\n\nInhale through your nose for 4 counts…\nHold for 7 counts…\nExhale fully through your mouth for 8 counts…\n\nThe long exhale triggers your body's relaxation response. How are you feeling?",
    ],
    "grounding": [
      "Let's try the 5-4-3-2-1 grounding technique to anchor you in the present moment.\n\n👁 Name 5 things you can SEE right now.\n🤚 Name 4 things you can TOUCH or feel.\n👂 Name 3 things you can HEAR.\n👃 Name 2 things you can SMELL (or like to smell).\n👅 Name 1 thing you can TASTE.\n\nTake your time with each one. This grounds your nervous system in the present.",
      "Let's try a physical grounding exercise. Press your feet firmly into the floor… feel the weight of your body in your chair… take a slow breath and feel your chest rise and fall… notice your hands resting wherever they are.\n\nYou are here. You are safe. This moment is manageable. How do you feel?",
    ],
    "body_scan": [
      "Let's do a brief body scan — it takes about 2 minutes and is deeply relaxing.\n\nStart at the top of your head… notice any tension without trying to change it… move to your forehead and eyes… jaw and neck… shoulders (breathe into them)… chest… stomach… lower back… hips… legs… feet.\n\nNotice where you're holding tension. Now breathe into each area gently. What did you notice?",
    ],
    "general": [
      "Mindfulness is simply being with what is, without fighting it. What are you noticing in your body right now?",
      "The mind wanders — that's perfectly normal. Each time you notice it wandering and gently return, that *is* the practice. You're doing it right.",
      "Try this: for the next 60 seconds, just notice your breath. Don't control it, just observe it. In… out… in… out. What did you notice?",
    ],
  },

  # ── JOURNAL AGENT ────────────────────────────────────────────────────────────
  "journal": {
    "greeting": [
      "Hello! I'm your Journal Agent. Writing is one of the most powerful tools for emotional processing and self-understanding. Would you like a guided prompt, or is there something specific on your mind you'd like to explore?",
      "Welcome. Reflective writing helps us make sense of our inner world. I have lots of prompts, or we can follow wherever your thoughts lead. What would feel good today?",
    ],
    "prompts": [
      "Try this prompt: *'Today I felt ___ because ___, and what it taught me about myself is ___.'* Take as much space as you need — there are no wrong answers.",
      "Here's a values prompt: *'Three things that matter most to me are ___, ___, and ___. This week, I honoured / didn't honour them by ___.'* What comes up for you?",
      "Gratitude prompt: *'Three small things that happened today that I'm grateful for are ___.'* They don't have to be big — a warm drink, a moment of quiet, someone being kind.",
      "Unsent letter prompt: *'Dear [person/feeling/past self], I want you to know ___.'* This is just for you — you never have to send it.",
      "Future self prompt: *'Five years from now, I hope I'm ___, and the small step I could take this week toward that is ___.'*",
      "Release prompt: *'Something I've been holding onto that I'd like to let go of is ___.'* Writing it down is the first step toward releasing it.",
    ],
    "reflection": [
      "That's a really meaningful insight. What do you think that says about what you need right now?",
      "I notice you used the word '___'. Say more about that — what does it mean to you in this context?",
      "What would it feel like to give yourself permission to feel exactly what you wrote?",
      "If you read that back in a year, what do you think you'd want to remember about this moment?",
    ],
    "general": [
      "Writing doesn't have to be perfect or polished — in fact, the messier the better. What's the first thing that comes to mind when you think about how you're feeling today?",
      "Sometimes just getting thoughts out of our head and onto the page creates space. What's taking up the most mental real estate right now?",
      "What's something you've been thinking but haven't said out loud to anyone?",
    ],
  },
}

# ═══════════════════════════════════════════════════════════════════════════════
# INTENT CLASSIFIER
# Simple keyword + pattern matching — no ML required.
# ═══════════════════════════════════════════════════════════════════════════════

CRISIS_PATTERNS = [
    r"\b(suicid|kill myself|want to die|end my life|no reason to live|hurt myself|self.harm|cutting|overdose)\b",
    r"\b(can'?t go on|don'?t want to be here|better off dead|disappear forever)\b",
]

INTENT_KEYWORDS = {
    "breathing":    ["breath", "breathing", "breathe", "inhale", "exhale", "air", "panic", "hyperventilat"],
    "grounding":    ["ground", "anchor", "present", "dissociat", "unreal", "spacey", "overwhelm"],
    "body_scan":    ["body", "tension", "scan", "relax", "muscle", "tight", "stiff"],
    "thought_record":["thought record", "record my thought", "write it down", "track my thought"],
    "distortion":   ["distort", "negative thinking", "spiral", "worst case", "catastroph", "all or nothing", "black and white", "mind read"],
    "reframe":      ["reframe", "balance", "alternative", "other way", "different perspective"],
    "prompts":      ["prompt", "journal", "write", "writing", "reflect", "what should i write"],
    "resources":    ["hotline", "helpline", "resource", "number", "call", "988", "crisis line"],
    "anxiety":      ["anxious", "anxiety", "worry", "worrying", "nervous", "panic", "scared", "fear", "dread", "uneasy"],
    "depression":   ["depress", "sad", "hopeless", "empty", "numb", "worthless", "guilt", "shame", "low", "down", "bleak"],
    "stress":       ["stress", "stressed", "overwhelm", "too much", "pressure", "burnout", "exhausted", "tired"],
    "anger":        ["angry", "anger", "furious", "rage", "frustrated", "irritat", "annoyed"],
    "loneliness":   ["alone", "lonely", "isolated", "no one", "nobody", "disconnected"],
    "sleep":        ["sleep", "insomnia", "can't sleep", "nightmare", "tired", "rest"],
    "greeting":     ["hello", "hi", "hey", "start", "begin", "help me", "i need help"],
}

def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in CRISIS_PATTERNS)

def classify_intent(text: str) -> str:
    t = text.lower()
    # Crisis always wins
    if is_crisis(t):
        return "crisis"
    # Score each intent
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                scores[intent] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"

def get_response(agent_id: str, intent: str, turn: int) -> str:
    bank = AGENT_RESPONSES.get(agent_id, {})

    # Map some intents to agent-specific keys
    intent_map = {
        "triage": {
            "crisis": "crisis", "anxiety": "anxiety", "depression": "depression",
            "stress": "stress", "greeting": "greeting",
        },
        "cbt": {
            "distortion": "distortion_identified", "thought_record": "thought_record",
            "reframe": "reframe", "greeting": "greeting",
        },
        "crisis": {
            "crisis": "active_crisis", "resources": "resources",
            "greeting": "greeting",
        },
        "mindfulness": {
            "breathing": "breathing", "grounding": "grounding",
            "body_scan": "body_scan", "greeting": "greeting",
            "anxiety": "breathing", "stress": "grounding",
        },
        "journal": {
            "prompts": "prompts", "greeting": "greeting",
        },
    }

    # Resolve the best response key
    mapped = intent_map.get(agent_id, {}).get(intent)
    if mapped and mapped in bank:
        key = mapped
    elif "general" in bank:
        key = "general"
    else:
        key = list(bank.keys())[0]

    responses = bank[key]
    # Rotate through responses so it doesn't repeat immediately
    return responses[turn % len(responses)]


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STORE  (in-memory, resets on server restart)
# ═══════════════════════════════════════════════════════════════════════════════

sessions: dict[str, dict] = {}

def get_session(sid: str) -> dict:
    if sid not in sessions:
        sessions[sid] = {"turn": 0, "agent": "triage", "history": [], "mood": None}
    return sessions[sid]

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {args[1]}  {args[0]}")

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open("index.html", "r") as f:
                self._html(f.read())
        elif self.path == "/agents":
            self._json({"agents": [
                {"id": k, "name": meta["name"], "role": meta["role"], "icon": meta["icon"]}
                for k, meta in AGENT_META.items()
            ]})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/chat":
            sid       = body.get("session_id", "default")
            agent_id  = body.get("agent_id", "triage")
            user_msg  = body.get("message", "").strip()

            if not user_msg:
                self._json({"error": "empty message"}, 400)
                return

            sess = get_session(sid)
            sess["agent"] = agent_id
            sess["history"].append({"role": "user", "content": user_msg})

            intent   = classify_intent(user_msg)
            reply    = get_response(agent_id, intent, sess["turn"])
            sess["turn"] += 1
            sess["history"].append({"role": "assistant", "content": reply})

            meta = AGENT_META.get(agent_id, {})
            self._json({
                "reply":      reply,
                "intent":     intent,
                "agent_id":   agent_id,
                "agent_name": meta.get("name", agent_id),
                "agent_icon": meta.get("icon", "🤖"),
                "is_crisis":  is_crisis(user_msg),
            })

        elif self.path == "/mood":
            sid   = body.get("session_id", "default")
            mood  = body.get("mood")
            get_session(sid)["mood"] = mood
            self._json({"ok": True})

        else:
            self._json({"error": "not found"}, 404)


AGENT_META = {
    "triage":      {"name": "Triage Agent",      "role": "First contact & routing",   "icon": "🎯",
                    "color": "#1D9E75", "bg": "#E1F5EE",
                    "desc": "Assesses your situation, gauges severity, and connects you with the right specialist."},
    "cbt":         {"name": "CBT Agent",          "role": "Cognitive Behavioural",     "icon": "🧠",
                    "color": "#534AB7", "bg": "#EEEDFE",
                    "desc": "Guides thought records, identifies cognitive distortions, builds balanced coping strategies."},
    "crisis":      {"name": "Crisis Agent",       "role": "Safety specialist",         "icon": "🛟",
                    "color": "#D85A30", "bg": "#FAECE7",
                    "desc": "Provides immediate safety support, crisis resources, and warm de-escalation."},
    "mindfulness": {"name": "Mindfulness Agent",  "role": "Grounding & relaxation",    "icon": "🌿",
                    "color": "#0F6E56", "bg": "#E1F5EE",
                    "desc": "Leads breathing exercises, body scans, and grounding techniques backed by research."},
    "journal":     {"name": "Journal Agent",      "role": "Reflective writing",        "icon": "📓",
                    "color": "#BA7517", "bg": "#FAEEDA",
                    "desc": "Offers structured journalling prompts, gratitude exercises, and reflective writing guides."},
}

if __name__ == "__main__":
    PORT = 8000
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   Mental Health Agent System  •  100% Offline       ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║   Open:  http://localhost:{PORT}                      ║")
    print("║   Stop:  Ctrl+C                                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    server = HTTPServer(("localhost", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
