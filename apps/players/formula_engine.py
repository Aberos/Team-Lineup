"""Sandboxed Lua engine that evaluates overall formulas."""

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from lupa import LuaError, LuaMemoryError, LuaRuntime

from apps.players.exceptions import FormulaError
from apps.players.models import OVERALL_MAX, OVERALL_MIN

MAX_INSTRUCTIONS = 200_000
MAX_MEMORY_BYTES = 16 * 1024 * 1024
ROUNDING_OFFSET = 0.5
TRACEBACK_MARKER = "stack traceback"
MEMORY_MESSAGE = "limite de memória excedido"
GENERIC_MESSAGE = "erro ao executar a fórmula"

_SANDBOX = """
local load, sethook, raise = load, debug.sethook, error
local function guard(limit)
  sethook(function() raise("limite de instruções excedido", 2) end, "", limit)
end
local function copy(source, skipped)
  local target = {}
  for key, value in pairs(source) do
    if not skipped[key] then target[key] = value end
  end
  return target
end
local function sandbox()
  return {
    math = copy(math, { random = true, randomseed = true }),
    string = copy(string, { dump = true }),
    table = copy(table, {}),
    pairs = pairs, ipairs = ipairs, next = next, select = select,
    tonumber = tonumber, tostring = tostring, type = type,
    error = error, assert = assert,
  }
end
return function(code, limit)
  local env = sandbox()
  local chunk, compile_error = load(code, "=formula", "t", env)
  if not chunk then return nil, compile_error end
  guard(limit)
  local ok, run_error = pcall(chunk)
  sethook()
  if not ok then return nil, tostring(run_error) end
  local entry = env.overall
  if type(entry) ~= "function" then
    return nil, "o script deve definir a função "
      .. "overall(notas, funcoes, principal)"
  end
  return function(notas, funcoes, principal)
    guard(limit)
    local call_ok, result = pcall(entry, notas, funcoes, principal)
    sethook()
    if not call_ok then raise(tostring(result), 0) end
    return result
  end
end
"""


@dataclass(frozen=True)
class FormulaInput:
    """Data of one player given to the formula.

    Attributes:
        ratings: Card ratings keyed by attribute abbreviation.
        roles: Names of the roles of the player.
        primary: Name of the primary role, or None.
    """

    ratings: Mapping[str, int]
    roles: Sequence[str]
    primary: str | None


def _readable(error: LuaError) -> str:
    """Return the first line of a Lua error, without the traceback.

    Args:
        error: Error raised by the Lua runtime.

    Returns:
        A short message for the administrator.
    """
    if isinstance(error, LuaMemoryError):
        return MEMORY_MESSAGE
    message = str(error).split(TRACEBACK_MARKER, 1)[0].strip()
    first_line = message.splitlines()[0].strip() if message else ""
    if not first_line:
        return GENERIC_MESSAGE
    if "not enough memory" in first_line:
        return MEMORY_MESSAGE
    return first_line


def _to_overall(result: object) -> int | None:
    """Validate the value returned by the formula and round it.

    Args:
        result: Value returned by the Lua function.

    Returns:
        The rounded overall, or None when the formula returned nil.

    Raises:
        FormulaError: If the value is not a finite number from 0 to 100.
    """
    if result is None:
        return None
    if isinstance(result, bool) or not isinstance(result, int | float):
        raise FormulaError("a função overall deve retornar um número ou nil")
    if not math.isfinite(result):
        raise FormulaError("a função overall retornou um número inválido")
    if not OVERALL_MIN <= result <= OVERALL_MAX:
        raise FormulaError(
            f"a função overall deve retornar de {OVERALL_MIN} a "
            f"{OVERALL_MAX}, mas retornou {result}"
        )
    return int(result + ROUNDING_OFFSET)


class CompiledFormula:
    """A formula ready to be evaluated for many players."""

    def __init__(
        self, runtime: LuaRuntime, entry: Callable[..., object]
    ) -> None:
        """Keep the Lua runtime and the guarded entry point.

        Args:
            runtime: Runtime that owns the compiled script.
            entry: Guarded Lua function that calls ``overall``.
        """
        self._runtime = runtime
        self._entry = entry

    def evaluate(self, data: FormulaInput) -> int | None:
        """Run the formula for one player.

        Args:
            data: Ratings and roles of the player.

        Returns:
            The rounded overall, or None when the formula returned nil.

        Raises:
            FormulaError: If the script fails, exceeds its limits or
                returns an invalid value.
        """
        ratings = self._runtime.table_from(dict(data.ratings))
        roles = self._runtime.table_from(list(data.roles))
        try:
            result = self._entry(ratings, roles, data.primary)
        except LuaError as error:
            raise FormulaError(_readable(error)) from error
        return _to_overall(result)


def compile_formula(script: str) -> CompiledFormula:
    """Compile a script inside an isolated Lua sandbox.

    Args:
        script: Lua source that defines ``overall``.

    Returns:
        The compiled formula.

    Raises:
        FormulaError: If the script has syntax errors, fails while loading,
            exceeds its limits or does not define ``overall``.
    """
    runtime = LuaRuntime(
        register_eval=False,
        register_builtins=False,
        unpack_returned_tuples=True,
        max_memory=MAX_MEMORY_BYTES,
    )
    factory = runtime.execute(_SANDBOX)
    try:
        compiled = factory(script, MAX_INSTRUCTIONS)
    except LuaError as error:
        raise FormulaError(_readable(error)) from error
    if isinstance(compiled, tuple):
        message = str(compiled[1])
        if "not enough memory" in message:
            raise FormulaError(MEMORY_MESSAGE)
        raise FormulaError(message.split(TRACEBACK_MARKER, 1)[0].strip())
    if not callable(compiled):
        raise FormulaError("não foi possível compilar a fórmula")
    return CompiledFormula(runtime, compiled)
