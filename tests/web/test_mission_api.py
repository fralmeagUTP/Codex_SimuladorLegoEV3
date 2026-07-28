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


def test_web_session_can_select_a_mission_and_exposes_its_contract(tmp_path) -> None:
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
    client = app.test_client()
    created = client.post("/api/sessions").get_json()

    response = client.post(
        f"/api/sessions/{created['session_id']}/mission",
        json={"id": "sigue-linea-basico"},
        headers={"X-Session-Token": created["owner_token"]},
    )

    assert response.status_code == 200
    assert response.get_json()["active_mission"] == {"id": "sigue-linea-basico", "title": "Sigue líneas básico"}
