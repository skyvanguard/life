"""
Experience v3, offline: do content-derived axes alone de-saturate Psi on
Yvyra's REAL (old, monotone) life? (docs/PHASE_B_DESIGN.md, "v3")

WHAT IT DOES. Rebuilds Yvyra's lived sequence from her journals
(self-journal = introspection ticks, journal = research ticks, ordered by date
and [HH:MM]) and drives two faithful deployment simulations (YvyraBridge with a
load/save per tick, same constructor as deploy/zeta/yvyra_kernel.py, same
synthetic warm-up as the real `warmup` command):
  OLD   the real 4-axis scores the kernel actually received (zeta_ticks.jsonl).
  V3    the v3 axes (bridge/experience.py) computed from her real responses:
        lexical novelty vs her last 10 responses, self-reference, uptake of the
        material (proxy: best-matching question from questions.md for
        introspection; none for research), length; research/net flags kept.
No events here: this is her old life, without MEMORIA / INTRUSION / VACIO. It
measures how much of the de-saturation the content features can give on their
own, before changing anything live.

READOUT (declared before running): among introspection ticks after the first
200 replayed ticks, the fraction of Psi in ALTA (>= 0.85), MEDIA, BAJA (< 0.40)
-- overall and excluding ticks right after a mode switch (the clock dips).
Target band for the live run (pre-registered there): 0.30 <= ALTA <= 0.75.

    PYTHONPATH=src python experiments/kernel/exp_experience_v3_replay.py
"""

from __future__ import annotations

import json
import random
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zeta_life.bridge import YvyraBridge  # noqa: E402
from zeta_life.bridge import experience as ex  # noqa: E402

HERMES = Path.home() / ".hermes"
HB = HERMES / "heartbeat"
LOG = HERMES / "zeta" / "state" / "zeta_ticks.jsonl"
AXES = ("novedad", "introspeccion", "conexion", "resolucion")
PREFERENCE = [0.30, 0.40, 0.10, 0.20]
WARMUP_SYNTH = 600
SKIP = 200
HI, LO = 0.85, 0.40
RESULTS = Path(__file__).resolve().parents[2] / "results"


def leer_vida() -> list[tuple[datetime, str, str]]:
    """(time, 'A'|'B', response) for every journal entry, in lived order."""
    vida = []
    for kind, sub in (("A", "self-journal"), ("B", "journal")):
        for f in sorted((HB / sub).glob("*.md")):
            fecha = f.stem
            partes = re.split(r"^## \[(\d\d:\d\d)\]\s*$", f.read_text(encoding="utf-8", errors="replace"), flags=re.M)
            for hhmm, texto in zip(partes[1::2], partes[2::2]):
                vida.append((datetime.fromisoformat(f"{fecha}T{hhmm}"), kind, texto.strip()))
    vida.sort(key=lambda r: r[0])
    return vida


def preguntas() -> list[str]:
    txt = (HB / "questions.md").read_text(encoding="utf-8", errors="replace")
    return [re.sub(r"^\d+\.\s*", "", q) for q in re.findall(r"^\d+\..*$", txt, flags=re.M)]


def ejes_v3_vida(vida: list[tuple[datetime, str, str]]) -> list[list[float]]:
    qs = preguntas()
    est = ex.Estado()
    out = []
    for _, kind, texto in vida:
        research = kind == "B"
        material = "" if research else max(qs, key=lambda q: ex.material_overlap(texto, q))
        net = research and "wikipedia" in texto.lower()
        out.append(list(ex.ejes_v3(text=texto, history=list(est.historia), material=material,
                                   research=research, net=net, notified=False)))
        ex.registrar_respuesta(est, texto, introspeccion=not research)
    return out


def simular(scores: list[list[float]]) -> np.ndarray:
    """Faithful deployment sim: synthetic warm-up, then load/save per tick."""
    d = tempfile.mkdtemp()
    torch.manual_seed(0)
    rng = random.Random(0)
    br = YvyraBridge(preference=PREFERENCE, mode="silent", save_dir=d)
    mood = list(PREFERENCE)
    for _ in range(WARMUP_SYNTH):
        mood = [min(1.0, max(0.0, m + 0.1 * (rng.random() - 0.5))) for m in mood]
        br.step(mood)
    br.save("y")
    psis = []
    for sc in scores:
        b = YvyraBridge(preference=PREFERENCE, mode="silent", save_dir=d)
        b.load("y")
        psis.append(b.step(sc)["psi_real"])      # silent mode hides "psi"; the real one is always there
        b.save("y")
    return np.array(psis)


def niveles(p: np.ndarray) -> str:
    if len(p) == 0:
        return "n=0"
    return f"n={len(p):>3}  ALTA {np.mean(p >= HI):.2f}  MEDIA {np.mean((p >= LO) & (p < HI)):.2f}  BAJA {np.mean(p < LO):.2f}"


def leer_old() -> tuple[list[list[float]], list[str]]:
    sc, kinds = [], []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            t = json.loads(line)
            sc.append([float(t["scores"][a]) for a in AXES])
            kinds.append("B" if t["scores"]["novedad"] >= 0.65 else "A")
    return sc, kinds


def reporte(nombre: str, psi: np.ndarray, kinds: list[str], out) -> dict:
    k = np.array(kinds)
    sw = np.r_[False, k[1:] != k[:-1]]
    idx = np.arange(len(psi)) >= SKIP
    a = idx & (k == "A")
    out(f"  {nombre:<4} introspeccion             {niveles(psi[a])}")
    out(f"  {nombre:<4} introspeccion sin cambio  {niveles(psi[a & ~sw])}")
    out(f"  {nombre:<4} investigacion             {niveles(psi[idx & (k == 'B')])}")
    return {"alta_A": float(np.mean(psi[a] >= HI)), "alta_A_sin_cambio": float(np.mean(psi[a & ~sw] >= HI))}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    vida = leer_vida()
    old_sc, old_k = leer_old()
    v3_sc = ejes_v3_vida(vida)
    v3_k = [k for _, k, _ in vida]
    out("=" * 78)
    out("EXPERIENCE v3 OFFLINE REPLAY: content-derived axes over Yvyra's real (old) life")
    out("=" * 78)
    out(f"journal entries: {len(vida)} (A {v3_k.count('A')}, B {v3_k.count('B')}); real logged ticks: {len(old_sc)}; "
        f"readout skips the first {SKIP}")
    a = np.array(v3_sc)
    old = np.array(old_sc)
    out(f"distinct axis vectors (2 decimals): OLD {len({tuple(np.round(r, 2)) for r in old})}  V3 {len({tuple(np.round(r, 2)) for r in a})}")
    ka = np.array(v3_k) == "A"
    out(f"V3 introspection axis std: {a[ka].std(0).round(3).tolist()}  (OLD: {old[np.array(old_k) == 'A'].std(0).round(3).tolist()})")
    out("")
    p_old = simular(old_sc)
    p_v3 = simular(v3_sc)
    out("-" * 78)
    r_old = reporte("OLD", p_old, old_k, out)
    r_v3 = reporte("V3", p_v3, v3_k, out)
    out("")
    out("-" * 78)
    banda = 0.30 <= r_v3["alta_A"] <= 0.75
    out(f"V3 introspection ALTA {r_v3['alta_A']:.2f} (OLD {r_old['alta_A']:.2f}); inside the live target band [0.30, 0.75]: {'yes' if banda else 'no'}")
    out("Reading: content features over the OLD life " + (
        "already de-saturate Psi; the live run tests whether events keep it there with a cause."
        if banda else "do not reach the band alone; the live run's events must supply the rest."))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "experience_v3_replay_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
