"""
Autonomous Calculator Agent powered by Google AI Studio Gemini LLM.
Pure Python, zero external agent frameworks (No LangChain, No CrewAI, No LlamaIndex).
Implements a first-principles ReAct / Tool-Calling Loop with retry resilience and full observability.
"""

import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional

# Ensure standard UTF-8 console output across Windows and Unix platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google import genai
from google.genai import types

from tools import TOOLS_LIST, execute_tool


class GeminiCalculatorAgent:
    """An autonomous agent that utilizes Gemini LLM and deterministic arithmetic tools."""

    DEFAULT_SYSTEM_INSTRUCTION = (
        "You are an expert computational assistant and mathematical problem solver. "
        "CRITICAL INSTRUCTION: You must NEVER perform arithmetic operations mentally. "
        "Whenever any calculation, arithmetic step, or mathematical evaluation is required, "
        "you MUST invoke the appropriate calculator tool (add, subtract, multiply, divide, power, modulus). "
        "For complex, multi-step math problems, break them down and execute each required tool step sequentially "
        "or in parallel until you reach the final result. "
        "Once all calculations are completed, present the solution clearly with the final answer."
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.5-flash",
        fallback_models: Optional[List[str]] = None,
        system_instruction: Optional[str] = None,
        max_iterations: int = 12,
        verbose: bool = True,
    ):
        """Initializes the Agent.

        Args:
            api_key: Gemini API key. Defaults to GEMINI_API_KEY environment variable.
            model: Primary Gemini model identifier.
            fallback_models: Alternative models to try if the primary model encounters capacity limits (503).
            system_instruction: System prompt to guide agent behavior.
            max_iterations: Safety limit on the number of reasoning/tool execution cycles.
            verbose: If True, prints formatted traces of thoughts and tool executions.
        """
        # Resolve API key from argument or environment variables
        resolved_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        if not resolved_key or not resolved_key.strip():
            raise ValueError(
                "Gemini API Key is missing. Please set GEMINI_API_KEY in your code or environment.\n"
                "You can get a free key from Google AI Studio: https://aistudio.google.com/app/apikey"
            )

        self.api_key = resolved_key.strip().strip("'\"")

        self.primary_model = model
        # Configure fallback chain for high-availability
        fallbacks = fallback_models if fallback_models is not None else ["gemini-flash-latest", "gemini-3.7-flash"]
        self.candidate_models = [m for m in [model] + fallbacks if m]
        self.active_model_idx = 0

        self.max_iterations = max_iterations
        self.verbose = verbose
        self.system_instruction = system_instruction or self.DEFAULT_SYSTEM_INSTRUCTION

        # Initialize the official Google GenAI Client
        self.client = genai.Client(api_key=self.api_key)

        # Configure tools: automatic function calling is disabled so that the agent loop
        # explicitly orchestrates and logs every perception-action-observation step.
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=TOOLS_LIST,
            temperature=0.0,  # Zero temperature for deterministic computation
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        # Agent short-term memory (conversation trajectory)
        self.conversation_history: List[types.Content] = []

    @property
    def current_model(self) -> str:
        return self.candidate_models[self.active_model_idx]

    def reset(self) -> None:
        """Clears the agent's short-term conversation memory."""
        self.conversation_history.clear()

    def _log(self, text: str, prefix: str = "", color_code: str = "\033[0m") -> None:
        """Helper for formatted console telemetry."""
        if not self.verbose:
            return
        reset = "\033[0m"
        formatted = f"{color_code}{prefix}{text}{reset}"
        try:
            print(formatted, flush=True)
        except UnicodeEncodeError:
            # Fallback for restrictive console encodings
            print(formatted.encode("ascii", errors="replace").decode("ascii"), flush=True)

    def _call_gemini_with_retry(
        self, contents: List[types.Content], max_retries: int = 3, base_delay: float = 2.0
    ) -> types.GenerateContentResponse:
        """Calls Gemini API with exponential backoff and transparent multi-model fallback."""
        start_idx = self.active_model_idx
        for model_offset in range(len(self.candidate_models)):
            idx = (start_idx + model_offset) % len(self.candidate_models)
            model_to_use = self.candidate_models[idx]

            for attempt in range(max_retries):
                try:
                    resp = self.client.models.generate_content(
                        model=model_to_use,
                        contents=contents,
                        config=self.config,
                    )
                    self.active_model_idx = idx  # Keep successful model as current
                    return resp
                except Exception as exc:
                    err_msg = str(exc)
                    is_transient = any(
                        code in err_msg for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]
                    )
                    if is_transient:
                        if attempt < max_retries - 1:
                            sleep_time = base_delay * (1.5 ** attempt)
                            self._log(
                                f"Transient API condition on {model_to_use}. Retrying in {sleep_time:.1f}s... (Attempt {attempt + 1}/{max_retries})",
                                prefix="[WARNING] ",
                                color_code="\033[93m",
                            )
                            time.sleep(sleep_time)
                        else:
                            # Try falling back to next candidate model if available
                            if model_offset < len(self.candidate_models) - 1:
                                next_model = self.candidate_models[(start_idx + model_offset + 1) % len(self.candidate_models)]
                                self._log(
                                    f"Model '{model_to_use}' capacity saturated. Failing over to '{next_model}'...",
                                    prefix="[FAILOVER] ",
                                    color_code="\033[95m",
                                )
                                break
                    else:
                        raise exc

        raise RuntimeError("All candidate models failed during API generation.")

    def run(self, user_prompt: str) -> str:
        """Executes the autonomous agent loop for the user query.

        Args:
            user_prompt: The user query or calculation request.

        Returns:
            The agent's synthesized response text.
        """
        self._log(f"\n[USER PROMPT] {user_prompt}", color_code="\033[1;36m")

        # 1. Append user input to conversation trajectory
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)],
        )
        self.conversation_history.append(user_content)

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            self._log(f"[STEP {iteration}] Querying Gemini ({self.current_model})...", color_code="\033[90m")

            # 2. Perception: Query model
            response = self._call_gemini_with_retry(self.conversation_history)

            if not response.candidates or not response.candidates[0].content:
                raise RuntimeError("Received empty response from Gemini model.")

            candidate_content = response.candidates[0].content
            # Append model's response to conversation history
            self.conversation_history.append(candidate_content)

            # 3. Decision: Check if model decided to call tools
            function_calls = response.function_calls

            # Termination condition: No tool calls requested => final answer ready
            if not function_calls:
                final_answer = response.text or ""
                self._log(f"\n[FINAL ANSWER]\n{final_answer}\n", color_code="\033[1;32m")
                return final_answer

            # 4. Action: Execute requested tool calls (handles parallel calls gracefully)
            response_parts: List[types.Part] = []

            for call in function_calls:
                fn_name = call.name
                fn_args = dict(call.args or {})
                args_str = ", ".join(f"{k}={v}" for k, v in fn_args.items())
                self._log(f"-> [TOOL CALL] {fn_name}({args_str})", color_code="\033[1;33m")

                # Local tool execution
                tool_output = execute_tool(fn_name, fn_args)

                if "error" in tool_output:
                    self._log(f"   [ERROR] {tool_output['error']}", color_code="\033[1;31m")
                else:
                    self._log(f"   [RESULT] {tool_output['result']}", color_code="\033[1;34m")

                # Construct function response part
                tool_part = types.Part.from_function_response(
                    name=fn_name,
                    response=tool_output,
                )
                response_parts.append(tool_part)

            # 5. Observation: Feed tool results back into the trajectory
            tool_response_content = types.Content(
                role="user",
                parts=response_parts,
            )
            self.conversation_history.append(tool_response_content)

        raise TimeoutError(
            f"Agent exceeded maximum allowed iterations ({self.max_iterations}) without reaching a final answer."
        )
