import re
from pathlib import Path


def test_user_interface_modules_do_not_reach_private_runtime_or_engine_details() -> None:
    root = Path(__file__).resolve().parents[2]
    sources = [
        *(root / "simulador_ev3" / "ui").glob("*.py"),
        *(root / "simulador_ev3" / "web" / "routes").glob("*.py"),
    ]
    forbidden = re.compile(r"\._(?:service|engine|worker|controller)_")

    violations = [f"{path.relative_to(root)}" for path in sources if forbidden.search(path.read_text(encoding="utf-8"))]

    assert not violations, f"Acceso UI a detalle privado: {', '.join(violations)}"
