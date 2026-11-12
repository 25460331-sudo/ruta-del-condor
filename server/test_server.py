import json
import server


def test_snapshot_incluye_a_los_jugadores():
    server.estado.clear()
    server.estado["ana"] = {"id": "ana", "x": 1.0, "y": 2.0}
    assert json.loads(server.snapshot())["e"]["ana"]["x"] == 1.0


def test_carrera_es_de_8():
    assert server.MAX_JUGADORES == 8


def test_limpiar_acepta_mensaje_valido_y_descarta_campos_extra():
    r = server.limpiar({"id": "abc123", "name": "Diego", "x": 10, "y": 50, "z": -3, "score": 7, "hack": "rm -rf /"})
    assert r["id"] == "abc123" and r["x"] == 10 and r["score"] == 7
    assert "hack" not in r


def test_limpiar_rechaza_ids_peligrosos_y_tipos_raros():
    assert server.limpiar({"id": "<script>"}) is None
    assert server.limpiar({"id": "a" * 40}) is None
    assert server.limpiar({"x": 1}) is None
    assert server.limpiar([1, 2, 3]) is None
    assert server.limpiar("texto") is None


def test_limpiar_pone_cero_en_numeros_invalidos_y_recorta_textos():
    r = server.limpiar({"id": "p1", "x": float("nan"), "y": "99", "z": True, "name": "N" * 100})
    assert r["x"] == 0 and r["y"] == 0 and r["z"] == 0
    assert len(r["name"]) == 14


def test_limpiar_limita_proyectiles_y_aros():
    pr = [[i, 0, 1, 2, 3] for i in range(20)]
    r = server.limpiar({"id": "p1", "pr": pr, "ac": list(range(100))})
    assert len(r["pr"]) == 4 and len(r["ac"]) == 16


def test_limpiar_acepta_mejoras_skin_y_ametralladora():
    r = server.limpiar({"id": "p1", "sk": 4, "hp": 80, "up": [1, 2, 3, 9, -5, 0], "ov": 1, "tb": 1,
                        "mg": [1, 2, 3, 0, 0, 1], "cd": list(range(20)), "gc": 3})
    assert r["sk"] == 4 and r["hp"] == 80 and r["ov"] == 1 and r["tb"] == 1 and r["gc"] == 3
    assert r["up"] == [1, 2, 3, 3, 0, 0]               # los niveles se acotan a 0..3
    assert r["mg"] == [1.0, 2.0, 3.0, 0.0, 0.0, 1.0] and len(r["cd"]) == 8


def test_limpiar_descarta_mg_y_mejoras_invalidas():
    r = server.limpiar({"id": "p1", "mg": [1, 2, "x", 0, 0, 1], "up": "hola"})
    assert r["mg"] == 0 and r["up"] == [0] * 6
