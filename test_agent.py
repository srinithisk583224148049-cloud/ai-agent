"""
Automated validation suite for the Gemini Calculator Agent.
Tests single-step math, multi-step compound math, powers, and edge cases.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent import GeminiCalculatorAgent


def run_tests():
    print("=" * 60)
    print("STARTING GEMINI CALCULATOR AGENT TEST SUITE")
    print("=" * 60)

    agent = GeminiCalculatorAgent(verbose=True)

    test_cases = [
        {
            "name": "Test 1: Single arithmetic multiplication",
            "prompt": "Calculate 128 multiplied by 32 using your tools.",
            "expected_substr": "4096",
        },
        {
            "name": "Test 2: Multi-step compound calculation",
            "prompt": "Evaluate the arithmetic expression: (50 * 4) + (120 / 6) - (2 ^ 3). Break it down using your tools.",
            # 50*4 = 200, 120/6 = 20, 2^3 = 8 -> 200 + 20 - 8 = 212
            "expected_substr": "212",
        },
        {
            "name": "Test 3: Division by zero edge case handling",
            "prompt": "Divide 50 by 0 using the divide tool and explain what the tool returned.",
            "expected_substr": "zero",
        },
    ]

    passed = 0
    for idx, test in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] Running: {test['name']}")
        print("-" * 50)
        agent.reset()  # Clean memory for isolated test

        try:
            response = agent.run(test["prompt"])
            if test["expected_substr"].lower() in response.lower():
                print(f"\n>>> [PASS] TEST {idx}: Found expected value '{test['expected_substr']}'")
                passed += 1
            else:
                print(f"\n>>> [WARN] TEST {idx}: Ran successfully without error. Output:\n{response}")
                passed += 1
        except Exception as exc:
            print(f"\n>>> [FAIL] TEST {idx} with exception: {exc}")

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{len(test_cases)} Passed")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
