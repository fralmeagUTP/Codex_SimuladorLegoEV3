from pathlib import Path


def test_simulator_robot_differences_are_documented_for_students() -> None:
    document = (Path(__file__).parents[2] / "Documentos" / "DIFERENCIAS_SIMULADOR_ROBOT.md").read_text(
        encoding="utf-8"
    )

    for topic in ("Motores", "Sensores", "Ultrasonido", "Seguridad", "Criterio de entrega"):
        assert topic in document
