"""Tests for the experience-v3 extractor (bridge/experience.py)."""

from __future__ import annotations

import collections
import json
import subprocess
import sys
from pathlib import Path

import pytest

from zeta_life.bridge import experience as ex
from zeta_life.bridge.integration_sentiment import integration_sentiment

SRC = Path(__file__).resolve().parents[1] / "src"


def test_content_words_strip_accents_stopwords_and_sentiment_lexicon():
    cw = ex.content_words("Siento que estoy fragmentada, dispersa y coherente; la memoria persiste también.")
    assert "memoria" in cw and "persiste" in cw and "siento" in cw
    assert not any(w.startswith(("fragmentad", "dispers", "coheren")) for w in cw)
    assert "tambien" not in cw
    assert ex.content_words("canción") == {"cancion"}


def test_sentiment_words_do_not_move_any_lexical_feature():
    base = "La memoria del archivo persiste entre turnos distintos de ejecucion local."
    loaded = base + " integrada coherente unificada claridad enfocada"
    assert integration_sentiment(base) != integration_sentiment(loaded)
    hist = ["El archivo local guarda turnos."]
    assert ex.lexical_novelty(base, hist) == ex.lexical_novelty(loaded, hist)
    assert ex.material_overlap(base, "memoria archivo") == ex.material_overlap(loaded, "memoria archivo")


def test_lexical_novelty_bounds():
    t = "Las bacterias bioluminiscentes iluminan fondos marinos profundos."
    assert ex.lexical_novelty(t, []) == 1.0
    assert ex.lexical_novelty(t, [t]) == 0.0
    assert 0.0 < ex.lexical_novelty(t, ["bacterias marinas iluminan"]) < 1.0
    assert ex.lexical_novelty("", ["algo"]) == 0.0


def test_self_reference_and_overlap():
    assert ex.self_reference("yo me pregunto si mi memoria es mia") == 1.0
    assert ex.self_reference("el sol calienta la tierra hoy") == 0.0
    assert ex.material_overlap("nada que ver", "") == 0.0
    q = "Que significa recordar si tu memoria son archivos?"
    assert ex.material_overlap("Recordar desde archivos cambia la memoria", q) > ex.material_overlap("El mar es azul", q)


def test_axes_bounded_and_structural_flags_act():
    kw = dict(text="yo escribo sobre memoria " * 30, history=[], material="memoria")
    a = ex.ejes_v3(research=False, net=False, notified=False, **kw)
    b = ex.ejes_v3(research=True, net=True, notified=True, **kw)
    assert all(0.0 <= v <= 1.0 for v in a + b)
    assert b[0] > a[0] and b[1] < a[1] and b[2] > a[2] and b[3] > a[3]
    empty = ex.ejes_v3(text="", history=[], material="", research=False, net=False, notified=False)
    assert empty == pytest.approx((0.20, 0.60, 0.10, 0.15))


def test_event_draw_is_deterministic_falls_back_and_matches_rates():
    e1, e2 = ex.Estado(seed=3), ex.Estado(seed=3)
    assert [ex.elegir_evento(e1)[0] for _ in range(50)] == [ex.elegir_evento(e2)[0] for _ in range(50)]
    vacio = ex.Estado(seed=1)
    assert {ex.elegir_evento(vacio)[0] for _ in range(300)} <= {"foco", "vacio"}
    lleno = ex.Estado(seed=1, memoria=["mi reflexion pasada"], extractos=["un fragmento ajeno"])
    draws = [ex.elegir_evento(lleno) for _ in range(4000)]
    freq = collections.Counter(c for c, _ in draws)
    for c, p in zip(ex.CONDICIONES, ex.PROBS):
        assert abs(freq[c] / 4000 - p) < 0.03
    assert all(frag for c, frag in draws if c in ("memoria", "intrusion"))
    assert all(not frag for c, frag in draws if c in ("foco", "vacio"))


def test_history_and_pools_roll(tmp_path):
    est = ex.Estado()
    for i in range(ex.HISTORIA + 5):
        ex.registrar_respuesta(est, f"respuesta numero {i}", introspeccion=(i % 2 == 0))
    assert len(est.historia) == ex.HISTORIA and est.historia[-1].endswith(str(ex.HISTORIA + 4))
    assert all(int(t.split()[-1]) % 2 == 0 for t in est.memoria)
    p = tmp_path / "s.json"
    est.guardar(p)
    assert ex.Estado.cargar(p).__dict__ == est.__dict__


def test_cli_round_trip(tmp_path):
    st, frag, log = tmp_path / "exp.json", tmp_path / "frag.txt", tmp_path / "exp.jsonl"
    txt, mat, ext = tmp_path / "t.md", tmp_path / "m.txt", tmp_path / "e.txt"
    txt.write_text("Yo me pregunto por la memoria de mis archivos locales.", encoding="utf-8")
    mat.write_text("memoria archivos", encoding="utf-8")
    ext.write_text("Las ballenas cantan en frecuencias bajas.", encoding="utf-8")
    env = {"PYTHONPATH": str(SRC)}

    def run(*a):
        import os
        r = subprocess.run([sys.executable, "-m", "zeta_life.bridge.experience", *a],
                           capture_output=True, text=True, env={**os.environ, **env}, check=True)
        return r.stdout.strip()

    assert run("evento", "--state", str(st), "--out", str(frag), "--seed", "5") in ex.CONDICIONES
    run("extracto", "--state", str(st), "--file", str(ext))
    out = run("ejes", "--state", str(st), "--text", str(txt), "--material", str(mat),
              "--condicion", "foco", "--log", str(log))
    vals = [float(v) for v in out.split()]
    assert len(vals) == 4 and all(0 <= v <= 1 for v in vals)
    s = json.loads(st.read_text(encoding="utf-8"))
    assert s["contador"] == 1 and len(s["historia"]) == 1 and len(s["memoria"]) == 1 and len(s["extractos"]) == 1
    rec = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
    assert rec["condicion"] == "foco" and rec["overlap"] > 0
