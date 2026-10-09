"""
Arithmetic Tools for the Gemini Agent.
Zero-framework, pure Python implementation with explicit type hints and docstrings.
"""

from typing import Any, Callable, Dict


def add(a: float, b: float) -> float:
    """Adds two numbers (a + b).

    Args:
        a: First number (float or int).
        b: Second number (float or int).

    Returns:
        The sum of a and b.
    """
    return float(a + b)


def subtract(a: float, b: float) -> float:
    """Subtracts the second number from the first number (a - b).

    Args:
        a: First number (minuend).
        b: Second number (subtrahend).

    Returns:
        The difference of a and b.
    """
    return float(a - b)


def multiply(a: float, b: float) -> float:
    """Multiplies two numbers (a * b).

    Args:
        a: First number.
        b: Second number.

    Returns:
        The product of a and b.
    """
    return float(a * b)


def divide(a: float, b: float) -> float:
    """Divides the first number by the second number (a / b).

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        The quotient of a and b.

    Raises:
        ValueError: If denominator b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero. Denominator must be non-zero.")
    return float(a / b)


def power(base: float, exponent: float) -> float:
    """Raises the base to the specified exponent (base ** exponent).

    Args:
        base: The base number.
        exponent: The exponent power to raise the base to.

    Returns:
        The result of base raised to power exponent.
    """
    return float(base ** exponent)


def modulus(a: float, b: float) -> float:
    """Computes the remainder of dividing a by b (a % b).

    Args:
        a: Numerator.
        b: Divisor.

    Returns:
        The remainder after division.

    Raises:
        ValueError: If divisor b is zero.
    """
    if b == 0:
        raise ValueError("Cannot compute modulus with divisor of zero.")
    return float(a % b)


# Tool registry for dynamic execution dispatch
TOOLS_LIST = [add, subtract, multiply, divide, power, modulus]

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {
    func.__name__: func for func in TOOLS_LIST
}


def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Safely executes a registered tool function by name with provided arguments.

    Args:
        name: The name of the registered function.
        args: Dictionary of keyword arguments to pass.

    Returns:
        A dictionary with 'result' on success or 'error' on failure.
    """
    if name not in TOOL_REGISTRY:
        return {"error": f"Tool '{name}' is not recognized. Available tools: {list(TOOL_REGISTRY.keys())}"}

    try:
        fn = TOOL_REGISTRY[name]
        result = fn(**args)
        return {"result": result}
    except Exception as exc:
        return {"error": f"Error executing '{name}': {str(exc)}"}
