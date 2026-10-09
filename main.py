"""
Interactive Terminal REPL for the Gemini Calculator Agent.
"""

import getpass
import os
import sys

# Ensure standard UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent import GeminiCalculatorAgent
from tools import TOOL_REGISTRY


# ==============================================================================
# 🔑 SET YOUR GOOGLE AI STUDIO API KEY DIRECTLY HERE:
# 1. Get your free API key at: https://aistudio.google.com/app/apikey
# 2. Paste it between the quotes below (it typically starts with "AIzaSy..."):
# ==============================================================================
API_KEY_IN_CODE = "AQ.Ab8RN6LIAxdEGSQprvzZ6xzr-X7mMTuwUD2T_NG-RhjZ2Y5z5w"  # <-- PASTE YOUR KEY HERE, e.g. "AIzaSy..."
# ==============================================================================


BANNER = """
================================================================================
           GEMINI AUTONOMOUS ARITHMETIC AGENT (ZERO-FRAMEWORK)
   Built from First-Principles with Google GenAI SDK & Python Standard Library
================================================================================
"""

HELP_TEXT = """
Available Commands:
  /help        - Show this guidance message
  /clear       - Reset agent memory for a fresh conversation
  /tools       - List available arithmetic tools
  /exit, /quit - Exit the interactive session

Sample Prompts to Try:
  - "What is (450 * 12) + (1800 / 15) - 3^4?"
  - "If an investment grows by 7.5% per year, what is $15,000 worth after 5 years? (Use compound interest: P * (1 + r)^t)"
  - "Find the remainder when 45982 is divided by 37."
  - "Divide 150 by 0 and tell me what happens."
"""


def load_local_dotenv(filepath: str = ".env") -> None:
    """Lightweight zero-dependency .env loader."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))
        except Exception:
            pass


def get_api_key() -> str:
    """Retrieves and validates API key from code, .env, environment, or user prompt."""
    load_local_dotenv()

    # 1. Check code-level variable
    if API_KEY_IN_CODE and API_KEY_IN_CODE.strip() and API_KEY_IN_CODE != "PASTE_YOUR_KEY_HERE":
        candidate = API_KEY_IN_CODE.strip().strip("'\"")
    else:
        # 2. Check environment variables
        candidate = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or ""
        ).strip().strip("'\"")

    # 3. If still empty, prompt the user in terminal
    if not candidate:
        print("\n[!] No API key found in 'main.py' or system environment.")
        print("[i] You can get a free Gemini API key at: https://aistudio.google.com/app/apikey")
        while not candidate:
            candidate = input("Enter your Google AI Studio API key (starts with 'AIza...'): ").strip().strip("'\"")
            if not candidate:
                print("Key cannot be empty.")

    # Validate key format and warn if an OAuth access token was mistakenly supplied
    if candidate.startswith("AQ.") or candidate.startswith("ya29."):
        print("\n" + "=" * 70)
        print("[WARNING] The key you provided appears to be an OAuth/gcloud token ('AQ...' or 'ya29...'),")
        print("          rather than a Google AI Studio API Key.")
        print("          Google AI Studio requires an API key that starts with 'AIzaSy...'.")
        print("          Create one for free at: https://aistudio.google.com/app/apikey")
        print("=" * 70 + "\n")

    return candidate


def print_tools() -> None:
    """Displays registered tools and docstrings."""
    print("\nRegistered Arithmetic Tools:")
    for name, fn in TOOL_REGISTRY.items():
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        print(f"  * {name}: {doc}")
    print()


def main():
    print(BANNER)
    api_key = get_api_key()

    model_name = "gemini-3.5-flash"
    print(f"[*] Initializing Agent with primary model: {model_name}")
    print(f"[*] Loaded {len(TOOL_REGISTRY)} arithmetic tools directly into agent runtime.")
    print("Type /help for commands or /exit to quit.\n")

    try:
        agent = GeminiCalculatorAgent(
            api_key=api_key,
            model=model_name,
            verbose=True,
        )
    except Exception as init_err:
        print(f"\n[Error during agent initialization]: {init_err}")
        return

    # One-shot input via command-line arguments (e.g. python main.py "What is 125 * 4?")
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
        if query:
            agent.run(query)
            return

    while True:
        try:
            prompt = input("User > ").strip()
            if not prompt:
                continue

            # Command handling
            cmd = prompt.lower()
            if cmd in ["/exit", "/quit", "exit", "quit"]:
                print("\nExiting session. Happy computing!")
                break
            elif cmd == "/help":
                print(HELP_TEXT)
                continue
            elif cmd == "/clear":
                agent.reset()
                print("\n[OK] Agent conversation memory cleared. Starting fresh.\n")
                continue
            elif cmd == "/tools":
                print_tools()
                continue

            # Autonomous execution
            agent.run(prompt)

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession terminated by user.")
            break
        except Exception as exc:
            print(f"\n[Error during execution]: {exc}\n")


if __name__ == "__main__":
    main()
