"""
Minimal example showing how to pass input to the agent programmatically.
"""

from agent import GeminiCalculatorAgent

# 1. Initialize the agent (reads GEMINI_API_KEY from environment or paste it here)
agent = GeminiCalculatorAgent(
    # api_key="AIzaSy...",  # Optional if GEMINI_API_KEY environment variable is set
    model="gemini-3.5-flash",
    verbose=True,  # Set to True to see step-by-step tool invocation traces
)

# 2. Provide your input string directly to agent.run()
user_input = "If a car travels 65 miles per hour for 3.5 hours, how many miles did it cover?"
answer = agent.run(user_input)

print("\n--- FINAL RETURN VALUE ---")
print(answer)
