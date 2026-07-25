from simulador_ev3.web.app import create_app


def test_mission_api_exposes_only_available_local_missions(tmp_path) -> None:
    examples = tmp_path / "examples"
    worlds = tmp_path / "worlds"
    examples.mkdir()
    worlds.mkdir()
    examples.joinpath("11_siguelineas_basico.py").write_text("pass", encoding="utf-8")
    worlds.joinpath("01_linea_negra_basica.json").write_text("{}", encoding="utf-8")
    app = create_app(
        {
            "TESTING": True,
            "ENABLE_SESSION_CLEANUP_THREAD": False,
            "EXAMPLES_DIR": examples,
            "WORLDS_DIR": worlds,
        }
    )

    response = app.test_client().get("/api/missions")

    assert response.status_code == 200
    assert [mission["id"] for mission in response.get_json()["missions"]] == ["sigue-linea-basico"]
