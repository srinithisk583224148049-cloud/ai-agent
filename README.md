# Autonomous Gemini Arithmetic Agent (Zero Framework)

An agent built from first principles using **Python 3** and the **Google GenAI SDK (`google-genai`)** without bloated or opaque third-party frameworks like LangChain, CrewAI, or AutoGen.

---

## 🏛️ Architecture & Design Principles

As a 20-year software engineering veteran, building AI agents from first principles provides:
1. **Full Observability & Auditability**: Every reasoning step, tool call, argument, and tool response is visible and logged.
2. **Deterministic Computation**: Language models should never approximate arithmetic internally; they must delegate computation to verified, deterministic Python functions.
3. **Resilience & Fault Tolerance**: Transient server spikes (e.g. HTTP 503 / 429) are mitigated using exponential backoff retry and model failover (`gemini-3.5-flash` ➔ `gemini-flash-latest` ➔ `gemini-3.7-flash`).
4. **Zero Overhead**: Minimal dependencies, pure Python type hints, and standard library data structures.

```
                           +----------------------------+
                           |         User Query         |
                           +--------------+-------------+
                                          |
                                          v
+-------------------> [ Perception: Conversation Trajectory ] <-------------------+
|                                         |                                       |
|                                         v                                       |
|                       [ Deliberation: Gemini LLM ]                              |
|                         (gemini-3.5-flash / failover)                           |
|                                         |                                       |
|                     +-------------------+-------------------+                   |
|                     |                                       |                   |
|          [ Tool Calls Requested? ]                                              |
|            /                  \                                                 |
|          YES                   NO                                               |
|           |                     \                                               |
|           v                      +-------------> [ Final Synthesized Answer ] --+
|  +--------------------+                                                         |
|  |   Action Engine    |                                                         |
|  | - add              |                                                         |
|  | - subtract         |                                                         |
|  | - multiply         |                                                         |
|  | - divide           |                                                         |
|  | - power            |                                                         |
|  | - modulus          |                                                         |
|  +--------+-----------+                                                         |
|           |                                                                     |
|           v                                                                     |
|  [ Observation: Tool Result / Error ] ------------------------------------------+
```

---

## 📁 Project Structure

```
gemini_calculator_agent/
├── tools.py          # Pure Python arithmetic tools with type annotations & registry
├── agent.py          # Autonomous GeminiCalculatorAgent implementing ReAct loop
├── main.py           # Interactive terminal REPL with command handling
├── test_agent.py     # Automated test suite (single-step, compound, edge-cases)
└── README.md         # Architecture and usage documentation
```

---

## 🛠️ Registered Arithmetic Tools

| Tool | Signature | Description |
| :--- | :--- | :--- |
| `add` | `(a: float, b: float) -> float` | Computes $a + b$ |
| `subtract` | `(a: float, b: float) -> float` | Computes $a - b$ |
| `multiply` | `(a: float, b: float) -> float` | Computes $a \times b$ |
| `divide` | `(a: float, b: float) -> float` | Computes $a / b$ (catches division by zero) |
| `power` | `(base: float, exponent: float) -> float` | Computes $\text{base}^{\text{exponent}}$ |
| `modulus` | `(a: float, b: float) -> float` | Computes $a \pmod b$ |

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ and the official `google-genai` SDK:
```bash
pip install google-genai
```

### 2. Configure Your API Key
Set your Google AI Studio API key in your terminal environment:

**PowerShell (Windows):**
```powershell
$env:GEMINI_API_KEY = "your_actual_api_key_here"
```

**Bash / Zsh (Linux/macOS):**
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

*(Note: If not set in the environment, `main.py` will securely prompt you for it upon startup).*

---

## 💻 Running the Interactive Agent (REPL)

Start the agent in your terminal:
```bash
python main.py
```

### Supported In-Session Commands:
- `/help` : Displays guide and suggested prompts.
- `/tools` : Inspects all registered arithmetic tools.
- `/clear` : Resets the agent's short-term conversation memory.
- `/exit` or `/quit` : Gracefully exits the session.

---

## 🧪 Running the Test Suite

Run the automated test suite to verify end-to-end multi-step tool calling and edge case recovery:
```bash
python test_agent.py
```
