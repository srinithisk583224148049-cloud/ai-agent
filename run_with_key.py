import inspect
import functools
from google import genai
from google.genai import types

# ==============================================================================
# 🔑 SET YOUR GEMINI API KEY HERE
# ==============================================================================
API_KEY = "AQ.Ab8RN6LIAxdEGSQprvzZ6xzr-X7mMTuwUD2T_NG-RhjZ2Y5z5w"
# ==============================================================================


# ------------------------------------------------------------------------------
# 1. Arithmetic Tools (Pure Python)
# ------------------------------------------------------------------------------
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b. Raises error on division by zero."""
    if b == 0:
        raise ZeroDivisionError("Division by zero is undefined.")
    return a / b

def power(base: float, exponent: float) -> float:
    """Raise base to exponent."""
    return base ** exponent

def modulus(a: float, b: float) -> float:
    """Calculate the modulo remainder of a divided by b."""
    if b == 0:
        raise ZeroDivisionError("Modulo by zero is undefined.")
    return a % b

RAW_TOOLS = [add, subtract, multiply, divide, power, modulus]


# ------------------------------------------------------------------------------
# 2. Tool Observability Wrapper (Logs every step)
# ------------------------------------------------------------------------------
def build_logged_tools(tools_list):
    wrapped = []
    for fn in tools_list:
        @functools.wraps(fn)
        def wrapper(*args, __func=fn, **kwargs):
            call_kwargs = kwargs.copy()
            if args:
                sig = inspect.signature(__func)
                names = list(sig.parameters.keys())
                for i, v in enumerate(args):
                    if i < len(names):
                        call_kwargs[names[i]] = v
           
            args_repr = ", ".join(f"{k}={v}" for k, v in call_kwargs.items())
            print(f"  [Tool Action] -> {__func.__name__}({args_repr})")
            try:
                res = __func(*args, **kwargs)
                print(f"  [Tool Observation] <- {res}")
                return res
            except Exception as err:
                print(f"  [Tool Error] <- {err}")
                raise
        wrapped.append(wrapper)
    return wrapped


# ------------------------------------------------------------------------------
# 3. Agent Execution Function
# ------------------------------------------------------------------------------
def run_agent():
    if API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE" or not API_KEY.strip():
        print("\n⚠️ Please replace 'PASTE_YOUR_GEMINI_API_KEY_HERE' with your real API key at the top of the file!\n")
        return

    # Initialize Google GenAI client directly with the hardcoded API key
    client = genai.Client(api_key=API_KEY)

    system_instruction = (
        "You are an analytical mathematical reasoning agent.\n"
        "You have access to discrete arithmetic tools: add, subtract, multiply, divide, power, modulus.\n"
        "RULES:\n"
        "1. Never do math in your head. Always call the arithmetic tools for every step.\n"
        "2. Break down expressions into sequential operations.\n"
        "3. State your reasoning clearly and provide a concise final answer."
    )

    # Wrap tools so we can see real-time tool execution logs in terminal
    tools = build_logged_tools(RAW_TOOLS)

    # Create autonomous chat session (maintains context across follow-ups)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=tools,
        temperature=0.0
    )
    chat = client.chats.create(model="gemini-3.5-flash-lite", config=config)

    print("=" * 60)
    print(" GEMINI CALCULATOR AGENT READY")
    print(" Type a calculation, or type 'exit' to quit.")
    print("=" * 60)

    # Interactive chat loop
    while True:
        try:
            query = input("\nUser >> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        print("[Agent Loop Started]...")
        try:
            response = chat.send_message(query)
            print(f"\n[Final Answer]\n{response.text}\n")
        except Exception as e:
            print(f"[Error]: {e}\n")


if __name__ == "__main__":
    run_agent()

