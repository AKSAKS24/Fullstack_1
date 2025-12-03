"""
Agent loader and base classes.  Agents should subclass BaseAgent and implement the
`run` coroutine to perform their work.  This module exposes a `load_agent` function
that dynamically imports and returns the agent class by name.  New agents can be
added by placing a folder under `src/agents/{agent_name}` with an `agent.py` file
defining a subclass of BaseAgent.
"""
import importlib
from typing import Type

from .base import BaseAgent  # noqa: F401  # re-export for convenience


def load_agent(agent_name: str) -> Type[BaseAgent]:
    """
    Dynamically load and return an agent class based on its name.  The function
    expects a module `src.agents.{agent_name}.agent` with a class inheriting
    BaseAgent.  The class must be named `Agent`.
    """
    module_path = f"src.agents.{agent_name}.agent"
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ValueError(f"Agent '{agent_name}' not found") from exc
    try:
        agent_cls = getattr(module, "Agent")
    except AttributeError as exc:
        raise ValueError(f"Agent '{agent_name}' does not define an Agent class") from exc
    return agent_cls