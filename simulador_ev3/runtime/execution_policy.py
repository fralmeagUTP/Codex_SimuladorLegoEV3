"""
execution_policy.py — Política de ejecución del script de usuario.

Define qué builtins están permitidos, qué módulos están bloqueados
y cuánto tiempo puede ejecutarse un script antes de ser abortado.

Diseño basado en SAD §9: el sandbox ejecuta el script en un namespace
restringido. La capa Pybricks (Phase 5) se inyecta como módulo virtual
en ese namespace, reemplazando las importaciones reales de pybricks.*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Builtins permitidos en el namespace del script
# ---------------------------------------------------------------------------

# Subconjunto seguro de builtins de Python para scripts educativos EV3.
# Se excluyen: open, exec, eval, compile, __import__, input (bloquea hilo UI),
#              globals, locals, vars (introspección peligrosa).
SAFE_BUILTINS: dict[str, object] = {
    name: __builtins__[name]  # type: ignore[index]
    for name in (
        # Tipos básicos
        "int",
        "float",
        "str",
        "bool",
        "bytes",
        "bytearray",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        # Funciones de utilidad
        "len",
        "range",
        "enumerate",
        "zip",
        "map",
        "filter",
        "sorted",
        "reversed",
        "min",
        "max",
        "sum",
        "abs",
        "round",
        "all",
        "any",
        "isinstance",
        "issubclass",
        "type",
        "repr",
        "hash",
        "id",
        # E/S de texto (solo stdout dentro del sandbox)
        "print",
        # Constructores / iteradores
        "iter",
        "next",
        "callable",
        # Matemáticas básicas
        "pow",
        "divmod",
        # Excepciones comunes
        "Exception",
        "ValueError",
        "TypeError",
        "RuntimeError",
        "StopIteration",
        "IndexError",
        "KeyError",
        "AttributeError",
        "NotImplementedError",
        "ZeroDivisionError",
        "OverflowError",
        "AssertionError",
        # Otros inocuos
        "None",
        "True",
        "False",
        "object",
    )
    if name in (__builtins__ if isinstance(__builtins__, dict) else dir(__builtins__))
}

# Lista de módulos cuya importación directa debe bloquearse.
# El script siempre accede a la API Pybricks a través del namespace inyectado.
BLOCKED_MODULES: frozenset[str] = frozenset(
    {
        "os",
        "os.path",
        "sys",
        "subprocess",
        "socket",
        "threading",
        "multiprocessing",
        "concurrent",
        "ctypes",
        "mmap",
        "signal",
        "importlib",
        "imp",
        "pkgutil",
        "builtins",
        "__builtin__",
        "gc",
        "tracemalloc",
        "resource",
        "pybricks",  # se inyecta el módulo virtual, no el real
        "ev3dev2",  # alternativa bloqueada
        "rpyc",
    }
)


# ---------------------------------------------------------------------------
# Política de ejecución
# ---------------------------------------------------------------------------


@dataclass
class ExecutionPolicy:
    """
    Encapsula las restricciones de ejecución de un script de usuario.

    Atributos:
        max_runtime_s:  Tiempo máximo de ejecución en segundos.
                        0 = sin límite (no recomendado en producción).
        safe_builtins:  Diccionario de builtins disponibles en el namespace.
        blocked_modules:Módulos que no pueden importarse.
        allow_math:     Si True, el módulo `math` se añade al namespace.
        allow_time:     Si True, `time.sleep()` se expone (deshabilitado por
                        defecto: el script debe usar pybricks.tools.wait).
    """

    max_runtime_s: float = 120.0
    safe_builtins: dict[str, object] = field(default_factory=lambda: dict(SAFE_BUILTINS))
    blocked_modules: frozenset[str] = field(default_factory=lambda: frozenset(BLOCKED_MODULES))
    allow_math: bool = True
    allow_time: bool = False

    def __post_init__(self) -> None:
        if self.max_runtime_s < 0:
            raise ValueError("max_runtime_s debe ser ≥ 0")

    def build_namespace(
        self,
        pybricks_modules: Optional[dict[str, object]] = None,
    ) -> dict[str, object]:
        """
        Construye el namespace inicial para exec() del script de usuario.

        Args:
            pybricks_modules: Diccionario {nombre: módulo_virtual} que se
                              inyecta en el namespace.  Ejemplo:
                              {"pybricks": <PybricksVirtualPackage>}

        Returns:
            Namespace dict con __builtins__ restringidos.
        """
        import builtins as _builtins
        import math as _math
        import time as _time

        allowed_roots: set[str] = set()
        if pybricks_modules and "pybricks" in pybricks_modules:
            allowed_roots.add("pybricks")
        if self.allow_math:
            allowed_roots.add("math")
        if self.allow_time:
            allowed_roots.add("time")

        def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            """
            Importador restringido para scripts de usuario.

            Permite solo:
              - `pybricks` y submódulos registrados por la fábrica virtual
              - `math` si allow_math=True
              - `time` si allow_time=True
            Bloquea cualquier módulo de `blocked_modules` y cualquier otro no
            permitido explícitamente.
            """
            root = name.split(".", 1)[0]

            # pybricks se permite exclusivamente si fue inyectado por la
            # fábrica virtual para esta sesión.
            if root == "pybricks" and "pybricks" in allowed_roots:
                if pybricks_modules and name in pybricks_modules:
                    if fromlist:
                        return pybricks_modules[name]
                    return pybricks_modules["pybricks"]
                raise ImportError(f"Modulo Pybricks no inyectado: {name}")

            if self.is_module_blocked(name):
                raise ImportError(f"Módulo bloqueado por la política: {name}")

            if root not in allowed_roots:
                raise ImportError(f"Módulo no permitido en el sandbox: {name}")

            return _builtins.__import__(name, globals, locals, fromlist, level)

        safe_builtins = dict(self.safe_builtins)
        safe_builtins["__import__"] = _safe_import

        ns: dict[str, object] = {
            "__builtins__": safe_builtins,
            "__name__": "__main__",
        }

        if self.allow_math:
            ns["math"] = _math

        if self.allow_time:
            # Solo expone sleep; el resto es innecesario
            class _TimeMod:
                sleep = staticmethod(_time.sleep)

            ns["time"] = _TimeMod()

        if pybricks_modules:
            ns.update(pybricks_modules)

        return ns

    def is_module_blocked(self, module_name: str) -> bool:
        """True si `module_name` (o su raíz) está bloqueado."""
        root = module_name.split(".")[0]
        return root in self.blocked_modules or module_name in self.blocked_modules
