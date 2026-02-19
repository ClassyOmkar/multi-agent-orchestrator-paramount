# The Thinking Behind This Architecture
**Project:** Multi-Agent Orchestrator (Next.js + Python/FastAPI)
**Author:** [Your Name]
**Date:** Feb 2026

## The "Why" Before The "How"
Most multi-agent demos fail because they overengineer the communication layer. I didn't want to build a fragile house of cards. I wanted a system that feels *solid* when you use it. The core philosophy here is **"Stability First, Complexity Second."**

We needed an orchestrator that could take a vague user thought ("Research React vs Svelte") and turn it into a concrete, polished report. Here is how I broke that down.

## Architecture: The "Brain" and The "Body"
I split the system into two distinct parts that don't trust each other too much.

### 1. The Body (Frontend - Next.js)
The UI is dumb on purpose. It doesn't know *how* `Task 123` is being solved; it just asks "Are we there yet?"
*   **Unique Tech Choice:** using `CSS Grid` for the status icons. Flexbox was driving me crazy with sub-pixel alignment issues on the checkmarks. Grid just works.
*   **Persistence:** I used `localStorage` because losing your 5-minute research task significantly hurts the user experience if you accidentally hit refresh.

### 2. The Brain (Backend - FastAPI)
This is where the actual thinking happens.
*   **The Orchestrator:** It's a simple State Machine. It pushes the task object (`Dict`) from one agent to the next.
    *   *Input* -> **Planner** (Breaks it down)
    *   *Plan* -> **Researcher** (Gets real data)
    *   *Data* -> **Writer** (Drafts it)
    *   *Draft* -> **Reviewer** (Polishes it)
    *   *Result* -> **User**
*   **The "Fake News" Fix:** Initially, the Researcher was hallucinating sources. I plugged in the **Tavily API** to force it to look at the real internet. If it can't verify a fact, it doesn't write it.

## The Tough Decisions (Trade-offs)

### Polling vs. WebSockets
Everyone loves to say "Use WebSockets" for real-time apps. But for a task that updates maybe once every 2-3 seconds? WebSockets are overkill. They introduce connection state issues, firewall headaches, and reconnection logic.
**My Decision:** HTTP Polling every 1 second. It’s bulletproof, stateless, and impossible to break.

### The Reviewer "Death Logic"
A Reviewer Agent that can reject work sounds great until it gets stuck in an infinite loop of "Reject -> Fix -> Reject."
**My Decision:** For this version, the Reviewer goes into "Edit Mode" instead of "Reject Mode." It *always* approves, but it silently fixes the prose. This guarantees the user always gets a result, even if it's not perfect.

## If I Had More Time (Future Work)
1.  **Parallel Research:** Right now, the Researcher looks up topics sequentially. I'd make it async so it can Google 5 things at once.
2.  **Human-in-the-loop:** I'd add a "Pause" button before the Writer starts, so I can tweak the Plan manually.

---
*This codebase is built to be read, not just run. Check `orchestrator.py` for the core logic.*
