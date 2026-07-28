from simulador_ev3.shared.mission_catalog import MissionCatalog


def test_catalog_exposes_only_missions_with_local_resources(tmp_path) -> None:
    examples = tmp_path / "examples"
    worlds = tmp_path / "worlds"
    examples.mkdir()
    worlds.mkdir()
    examples.joinpath("11_siguelineas_basico.py").write_text("pass", encoding="utf-8")
    worlds.joinpath("01_linea_negra_basica.json").write_text("{}", encoding="utf-8")

    missions = MissionCatalog(examples, worlds).list_missions()

    assert [mission.identifier for mission in missions] == ["sigue-linea-basico"]
    assert MissionCatalog(examples, worlds).get("evita-obstaculos") is None
