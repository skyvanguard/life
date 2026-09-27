"""
§41 — ¿EL ENTORNO CONTIENE UN ÓPTIMO QUE DEPENDA DEL ORDEN? Competencia entre
estrategias con oráculo de estación, en el modelo reducido.
(docs/PLAN_INTELIGENCIA.md §41; ledger 2026-09-27)

QUÉ ES Y QUÉ NO. NO es el útero: es el modelo reducido (§39b). Y no es
evolución: no hay mutación. Es el MEJOR CASO para el orden: dos estrategias
fijas que CONOCEN la estación (oráculo), mezcladas mitad y mitad:
  X  no pare en la templada (C); pare en A y B.
  Y  no pare en la abundancia (B); pare en A y C.
Bajo clima (A→B→C→A) la estación que precede a la hambruna es C: si guardar
antes de la hambruna paga, debe ganar X. Bajo ciclo2 (A→C→B→A) la que la
precede es B: debe ganar Y. Si el entorno contiene un óptimo dependiente del
orden, la fracción final de X será > 0.5 bajo clima y < 0.5 bajo ciclo2.
Control: bajo el permutado no debe haber preferencia sistemática.

DISEÑO. 24 mundos por calendario, N = 256, 60000 ticks, sol seed 0, perillas
θ, s, g neutras (θ al azar, s = 1, g = 0) y fijas; X e Y asignadas al azar
celda a celda (mitad y mitad); las hijas copian exacto.
LECTURA (escrita antes de correr): fracción de X entre las vivas al final.
  HAY ÓPTIMO DE ORDEN  si X > 0.5 en ≥ 75% de los mundos bajo clima Y X < 0.5
                       en ≥ 75% bajo ciclo2 (p signo < 0.05 en ambos).
  NO HAY               si la preferencia tiene el mismo signo en ambos
                       calendarios o no hay preferencia: en esta ecología el
                       orden no cambia qué conviene; ninguna perilla puede
                       codificarlo y hay que cambiar el ENTORNO, no el tejido.

    PYTHONPATH=src python experiments/utero/exp_utero_orden_oraculo.py
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.sol import Sol  # noqa: E402

_spec = importlib.util.spec_from_file_location("q", HERE / "exp_utero_modelo_reducido_q.py")
Q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Q)
B = Q.B

W, N = 24, Q.N
TICKS = 60000
CALENDARIOS = {"clima": "ciclico", "ciclo2": "ciclico_inverso", "permutado": "permutado"}
X = np.array([1.0, 1.0, 0.0])          # propensión al parto en [A, B, C]: no pare en C
Y = np.array([1.0, 0.0, 1.0])          # no pare en B
RESULTS = HERE.parents[1] / "results"
NAME = "utero_orden_oraculo"


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("ORACULO DE ESTACION (modelo reducido, sin mutacion): X (no pare en C) contra Y (no pare en B), mitad y mitad")
    out("=" * 80)
    out(f"N={N}; {W} mundos por calendario; {TICKS} ticks; lectura pre-registrada (docstring)")
    out("")
    rng = np.random.default_rng(2028)
    res = {}
    t0 = time.time()
    for nombre, orden in CALENDARIOS.items():
        sol = Sol(seed=B.SOL_EVOL, ticks=TICKS, orden=orden, regimenes=B.REGS)
        est = Q.estaciones_por_tick(sol, TICKS)
        m = Q.ModeloQ(W, rng)
        es_x = rng.random((W, N)) < 0.5
        m.q = np.where(es_x[..., None], X, Y).astype(float)
        soles = np.tile(sol.serie, (W, 1))
        for t in range(TICKS):
            m.forzado = np.full(W, est[t])             # el nivel es la estación verdadera
            m.paso(soles[:, t:t + 1], True, None)      # fijo=True: las hijas copian exacto
        fx = np.array([np.all(m.q[w][m.alive[w]] == X, axis=1).mean() if m.alive[w].any() else np.nan
                       for w in range(W)])
        res[nombre] = (fx, m.alive.sum(axis=1))
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    out(f"  {'calendario':<10} {'vivas':>6} {'frac X mediana':>15} {'X>0.5':>7} {'X<0.5':>7}")
    k = {}
    for nombre, (fx, vivas) in res.items():
        f = fx[~np.isnan(fx)]
        k[nombre] = (int((f > 0.5).sum()), int((f < 0.5).sum()), len(f))
        out(f"  {nombre:<10} {np.median(vivas):>6.0f} {np.median(f):>15.2f} {k[nombre][0]:>4}/{len(f):<2} {k[nombre][1]:>4}/{len(f):<2}")
        out("    por mundo: " + " ".join(f"{x:.2f}" for x in fx))
    out("")
    out("=" * 80)
    out("LECTURA (regla escrita antes de correr)")
    a, b = k["clima"], k["ciclo2"]
    ok = (a[2] >= 8 and a[0] / a[2] >= 0.75 and B.signo_p(a[0], a[2]) < 0.05
          and b[2] >= 8 and b[1] / b[2] >= 0.75 and B.signo_p(b[1], b[2]) < 0.05)
    if ok:
        out("=> HAY OPTIMO DE ORDEN: X gana bajo clima e Y bajo ciclo2. El entorno contiene la senal; lo que falta es que la variacion y la seleccion la alcancen.")
    else:
        out("=> NO HAY OPTIMO DE ORDEN en esta ecologia: el orden no cambia que conviene. Ninguna perilla puede codificarlo; hay que cambiar el ENTORNO.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
