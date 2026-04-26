"""
Module: atlas.modules.productivity
Purpose: Local productivity tools for Atlas.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library
Last Updated: 2026-04-26
"""

from __future__ import annotations

import ast
import calendar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
import operator
import time
from typing import Callable


OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNITS_TO_METERS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
    "inch": 0.0254,
    "in": 0.0254,
    "ft": 0.3048,
    "feet": 0.3048,
    "mile": 1609.344,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_safe_eval(node.operand)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError("operator is not allowed")
        return OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        funcs = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan}
        if node.func.id not in funcs:
            raise ValueError("function is not allowed")
        return float(funcs[node.func.id](*[_safe_eval(arg) for arg in node.args]))
    raise ValueError("expression is not allowed")


@dataclass
class ProductivityTools:
    """Provide local productivity capabilities."""

    todos: list[str] = field(default_factory=list)

    def calculate(self, expression: str) -> str:
        """Safely evaluate a math expression."""
        result = _safe_eval(ast.parse(expression, mode="eval"))
        if result.is_integer():
            return f"{expression} = {int(result)}"
        return f"{expression} = {result:.4f}"

    def unit_convert(self, amount: float, from_unit: str, to_unit: str) -> str:
        """Convert simple length units."""
        source = from_unit.lower()
        target = to_unit.lower()
        if source not in UNITS_TO_METERS or target not in UNITS_TO_METERS:
            raise ValueError("supported units: " + ", ".join(sorted(UNITS_TO_METERS)))
        meters = amount * UNITS_TO_METERS[source]
        converted = meters / UNITS_TO_METERS[target]
        return f"{amount:g} {from_unit} = {converted:.4g} {to_unit}"

    def translate(self, text: str, target_language: str = "hi") -> str:
        """Return a local bilingual translation for common assistant phrases."""
        phrase = text.strip().lower()
        hindi = {
            "hello": "namaste",
            "thank you": "shukriya",
            "open firefox": "firefox kholo",
            "system info": "system ki jankari",
        }
        urdu = {
            "hello": "assalam alaikum",
            "thank you": "shukriya",
            "open firefox": "firefox kholo",
            "system info": "system ki maloomat",
        }
        table = urdu if target_language.lower() in {"ur", "urdu"} else hindi
        return table.get(phrase, f"Offline translation placeholder for '{text}' to {target_language}")

    def dictionary(self, word: str) -> str:
        """Return built-in definitions for common assistant terms."""
        entries = {
            "atlas": "a local-first desktop assistant that routes commands safely",
            "assistant": "software that helps complete tasks through natural commands",
            "bilingual": "able to use two languages",
        }
        return entries.get(word.lower(), f"No offline definition found for '{word}'.")

    def add_todo(self, text: str) -> str:
        """Add a task to the in-memory todo list."""
        self.todos.append(text)
        return f"Added todo: {text}"

    def list_todos(self) -> str:
        """Return current in-memory todos."""
        if not self.todos:
            return "No todos yet."
        return "; ".join(f"{index + 1}. {item}" for index, item in enumerate(self.todos))

    def todo(self, text: str) -> str:
        """Add or list todos based on command text."""
        cleaned = text.strip()
        if not cleaned or "list" in cleaned.lower():
            return self.list_todos()
        return self.add_todo(cleaned)

    def timer(self, minutes: float) -> str:
        """Create a timer description without blocking the process."""
        due = datetime.now() + timedelta(minutes=minutes)
        return f"Timer set for {minutes:g} minutes, due at {due:%H:%M:%S}."

    def stopwatch(self) -> str:
        """Start a simple stopwatch timestamp."""
        return f"Stopwatch started at {time.strftime('%H:%M:%S')}."

    def calendar_view(self, year: int | None = None, month: int | None = None) -> str:
        """Return a text calendar for the selected month."""
        now = datetime.now()
        return calendar.month(year or now.year, month or now.month)

    def pomodoro(self, minutes: int = 25) -> str:
        """Return a Pomodoro focus session plan."""
        return f"Pomodoro started: focus for {minutes} minutes, then take a 5 minute break."
