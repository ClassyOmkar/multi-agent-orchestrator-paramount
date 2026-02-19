# Design Document - Multi-Agent Task Orchestration System

## 1. Architectural Decisions

### Backend: FastAPI & Async Agents
I chose **FastAPI** for the backend due to its high performance, ease of use, and native support for asynchronous programming (`asyncio`). The orchestration of agents inherently involves waiting for I/O (simulated or real LLM calls), making an async architecture ideal to handle concurrency without blocking the main thread.

- **Agent Abstraction:** I defined a base `Agent` class with an `async process()` method. This ensures a consistent interface and allows ensuring non-blocking execution even if agents perform heavy I/O in the future.
- **Orchestrator:** The `Orchestrator` class manages the lifecycle of a task. It maintains the state of the task (Planning -> Researching -> Writing -> Reviewing) and coordinates the data flow between agents.
- **State Management:** Currently, the system uses in-memory dictionaries to store task states. This was chosen for simplicity and speed given the scope of the assignment, but the design allows for easy migration to a persistent database (e.g., PostgreSQL or Redis) by abstracting the storage layer.

### Frontend: Next.js & React
I utilized **Next.js** for the frontend to leverage its robust routing and server-side rendering capabilities, though the current implementation is primarily client-side for dynamic updates.
- **Component-Based Architecture:** The UI is broken down into reusable components (`TaskForm`, `StatusTracker`, `ResultDisplay`) to maintain clean code and separation of concerns.
- **CSS Modules:** Styling is handled via CSS Modules to ensure scoped styles and avoid class name collisions, providing a maintainable and conflict-free styling approach without heavy external dependencies.

## 2. Trade-offs Considered

### Polling vs. WebSockets
For real-time progress updates, I considered using WebSockets. However, I opted for **short polling** (every 1 second) for this implementation.
- **Reasoning:** Polling is significantly simpler to implement and robust enough for the expected load in a demo scenario. WebSockets introduce complexity with connection management, reconnection logic, and state synchronization. Given the 2-4 hour timeframe, polling ensured a reliable and functional solution without the overhead of maintaining persistent connections.

### In-Memory vs. Persistent Database
I chose **in-memory storage** for task history.
- **Reasoning:** Setting up a database (SQL or NoSQL) would add configuration overhead (Docker, migrations, etc.) that might exceed the time limit and complicate the setup for reviewers. In-memory storage is sufficient to demonstrate the orchestration logic and state transitions. The trade-off is that data is lost on server restart, which is acceptable for a take-home assignment context.

## 3. Future Improvements

With more time, I would address the following:
1.  **Persistence:** Integrate a database (e.g., PostgreSQL with SQLAlchemy) to persist task history and results.
2.  **WebSockets:** Replace polling with WebSockets or Server-Sent Events (SSE) for true push-based real-time updates.
3.  **Error Recovery:** Implement a robust retry mechanism in the Orchestrator. If an agent fails, the system could automatically retry or route to a fallback agent.
4.  **Real LLM Integration:** Replace the mock agents with actual calls to OpenAI/Anthropic APIs, handling API keys and rate limits securely.
5.  **Agent Configuration:** Allow users to dynamically configure the pipeline (e.g., skip review, add custom steps) via the UI.

## 4. Assumptions

-   The environment is single-process for the backend (due to in-memory state).
-   Task processing time is simulated with `asyncio.sleep` to mimic real LLM latency.
-   The user is running the application locally.
