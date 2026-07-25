from pathlib import Path


def test_pybricks_conformance_matrix_declares_all_public_modules() -> None:
    root = Path(__file__).parents[2]
    matrix = (
        root / "openspec" / "changes" / "elevar-calidad-y-paridad-de-interfaz" / "pybricks-conformance-v1.md"
    ).read_text(encoding="utf-8")

    for module in ("parameters", "ev3devices", "robotics", "hubs", "tools"):
        assert f"pybricks.{module}" in matrix
    for test_class in (
        "TestParameters",
        "TestMotorAPI",
        "TestSensorAPI",
        "TestDriveBaseAPI",
        "TestEV3BrickAPI",
        "TestWait",
        "TestStopWatch",
    ):
        assert test_class in matrix
