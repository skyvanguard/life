"""
El Útero — robustez de escala: ¿el 2–3/40 es un artefacto del tamaño del mundo
o del número de semillas?

Todo el arco corrió con max_n=256 (la pared de la placa de Petri) y 40
semillas. Un revisor va a preguntar por las dos cosas. Este experimento repite
la vara honesta (linaje 500 + sombra para candidatas) en:
  A. mundo 4× más grande (max_n=1024), semillas 0–39, v5 y v6 (asentada-100);
  B. mundo 256, semillas 40–119 (80 nuevas), v5 y v6 — ¿la tasa 2/40 y 3/40
     se sostiene con n mayor?

VARAS (mismas que v6 y su control): sostenida = ≥ 5 genomas persistentes/tramo
en [8000,12000) y ≥ 2× su sombra. Se reportan tasas con intervalo binomial
(Wilson 95%) para comparar 40 vs 120 semillas, y la tipicidad a 1024 vs 256.
PREDICCIONES — antes de mirar:
  P1 La tasa a 256 con 120 semillas queda dentro del Wilson de la tasa a 40
     (el 2–3/40 no era suerte de muestreo).
  P2 A 1024 la tipicidad NO baja (la pared no era lo que sostenía la novedad);
     si SUBE ≥2×, el tamaño era una jaula y hay que mover la placa.

    PYTHONPATH=src python experiments/utero/exp_utero_escala.py
"""

from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zeta_life.utero.medidas import correr_medido, media_ventana  # noqa: E402

TICKS = 14000
TRANCHE = 500
T_FILTRO = 500
MATURE = (8000, 12000)
FILT_MIN, SHADOW_X = 5.0, 2.0
ARMS = {"v5": {}, "v6": dict(invasion="asentada", eq_window=100)}
BLOQUES = {"1024x40": dict(max_n=1024, seeds=list(range(40))),
           "256x80nuevas": dict(max_n=256, seeds=list(range(40, 120)))}
PREVIO_256 = {"v5": (2, 40), "v6": (3, 40)}       # resultados publicados
WORKERS = max(1, min(20, (os.cpu_count() or 4) - 4))
RESULTS = Path(__file__).resolve().parents[2] / "results"
NAME = "utero_escala"


def job(args: tuple) -> tuple:
    bloque, arm, seed, shadow = args
    r = correr_medido(seed, dict(memoria=True, **ARMS[arm]), ticks=TICKS, tranche=TRANCHE,
                      t_filtro=T_FILTRO, shadow=shadow, max_n=BLOQUES[bloque]["max_n"])
    return bloque, arm, seed, media_ventana(r["filt"], MATURE, TRANCHE), list(r["deaths"]), \
        media_ventana(r["eco"], MATURE, TRANCHE), int(r["vivas"][-1])


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 78)
    out("EL UTERO -- robustez de escala: mundo 1024 y 80 semillas nuevas")
    out("=" * 78)
    out(f"{TICKS} ticks, memoria ON, linaje {T_FILTRO}, maduro {MATURE}, workers={WORKERS}")
    out("predicciones P1/P2 en el docstring, escritas antes de correr")
    out("")
    jobs = [(b, a, s, None) for b, cfg in BLOQUES.items() for a in ARMS for s in cfg["seeds"]]
    filt: dict = {}
    deaths: dict = {}
    eco: dict = {}
    vivas: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (b, a, s, f, d, e, v) in enumerate(ex.map(job, jobs), 1):
            filt[(b, a, s)], deaths[(b, a, s)], eco[(b, a, s)], vivas[(b, a, s)] = f, d, e, v
            if i % 40 == 0:
                print(f"  ... {i}/{len(jobs)} corridas", flush=True)
        cand = [(b, a, s, deaths[(b, a, s)]) for (b, a, s), f in filt.items() if f >= FILT_MIN]
        sh: dict = {}
        for b, a, s, f, _, _, _ in ex.map(job, cand):
            sh[(b, a, s)] = f

    out("-" * 78)
    out(f"  {'bloque':<14} {'brazo':<4} {'sostenidas':>10} {'tasa':>6} {'Wilson 95%':>16} "
        f"{'semillas':<28} {'eco med':>7} {'vivas med':>9}")
    tasas = {}
    for b, cfg in BLOQUES.items():
        for a in ARMS:
            ss = [s for s in cfg["seeds"] if filt[(b, a, s)] >= FILT_MIN
                  and filt[(b, a, s)] >= SHADOW_X * sh.get((b, a, s), 0.0)]
            n = len(cfg["seeds"])
            lo, hi = wilson(len(ss), n)
            tasas[(b, a)] = (len(ss), n)
            e = float(np.median([eco[(b, a, s)] for s in ss])) if ss else float("nan")
            v = float(np.median([vivas[(b, a, s)] for s in cfg["seeds"]]))
            out(f"  {b:<14} {a:<4} {len(ss):>7}/{n:<3} {len(ss)/n:>6.3f} [{lo:.3f}, {hi:.3f}]  "
                f"{str(ss):<28} {e:>7.2f} {v:>9.0f}")
    out("")
    out("  referencia publicada (256, semillas 0-39): v5 2/40 = 0.050, v6 3/40 = 0.075")
    out("")
    out("=" * 78)
    out("PREDICCIONES")
    for a in ARMS:
        k0, n0 = PREVIO_256[a]
        k1, n1 = tasas[("256x80nuevas", a)]
        k, n = k0 + k1, n0 + n1
        lo, hi = wilson(k0, n0)
        p1 = k1 / n1
        out(f"  P1 {a}: 80 semillas nuevas a 256 -> {k1}/{n1} = {p1:.3f}; Wilson del 40 previo "
            f"[{lo:.3f}, {hi:.3f}] -> {'dentro' if lo <= p1 <= hi else 'FUERA'}; "
            f"tasa combinada {k}/{n} = {k/n:.3f} {wilson(k, n)}")
    for a in ARMS:
        k0, n0 = PREVIO_256[a]
        k2, n2 = tasas[("1024x40", a)]
        r = (k2 / n2) / max(k0 / n0, 1e-9)
        out(f"  P2 {a}: 1024 celdas -> {k2}/{n2} vs {k0}/{n0} a 256 (ratio {r:.2f}) -> "
            f"{'SUBE >=2x: la pared era jaula' if r >= 2 else ('no baja' if r >= 1 else 'BAJA')}")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
