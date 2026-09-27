"""
§41c — CONFIRMATORIA: las dos ganadoras del torneo, cara a cara y con más
potencia. (docs/PLAN_INTELIGENCIA.md §41; ledger 2026-09-27)

El torneo (§41b) fue NO CONCLUYENTE por la regla, con la deriva de ocho
estrategias en 256 lugares, pero señaló dos candidatas: parir SÓLO en la
estación que sigue a la hambruna — sólo en B bajo clima (A→B→C), sólo en C
bajo ciclo2 (A→C→B). Hipótesis confirmatoria, declarada antes de correr:
  X = pare sólo en B;  Y = pare sólo en C;  mitad y mitad; sin mutación;
  oráculo de estación; modelo reducido (NO el útero).
  48 mundos por calendario, N = 512 lugares (L0 = 14), 60000 ticks.
  HAY ÓPTIMO DE ORDEN si X > 0.5 en ≥ 75% de los mundos bajo clima Y X < 0.5
  en ≥ 75% bajo ciclo2 (p signo < 0.05 en ambos). NO HAY en otro caso.
Si se confirma: el entorno contiene un óptimo que depende del orden (parir
cuando la hambruna acaba de pasar y no en otro momento), y una perilla que
lo codifique necesita distinguir "después de la hambruna" de "antes": una
memoria de la estación anterior, no el ingreso presente.

    PYTHONPATH=src python experiments/utero/exp_utero_orden_confirmatoria.py
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

W = 48
B.N = Q.N = N = 512                  # doble de lugares; misma luz por lugar
B.L0 = 14.0
TICKS = 60000
CALENDARIOS = {"clima": "ciclico", "ciclo2": "ciclico_inverso", "permutado": "permutado"}
X = np.array([0.0, 1.0, 0.0])          # propensión al parto en [A, B, C]: pare SÓLO en B
Y = np.array([0.0, 0.0, 1.0])          # pare SÓLO en C
RESULTS = HERE.parents[1] / "results"
NAME = "utero_orden_confirmatoria"


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("CONFIRMATORIA (modelo reducido, sin mutacion, oraculo): X (pare solo en B) contra Y (pare solo en C), mitad y mitad")
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
        out("=> HAY OPTIMO DE ORDEN: parir solo en la estacion que sigue a la hambruna gana en cada calendario. El entorno contiene la senal.")
    else:
        out("=> NO HAY OPTIMO DE ORDEN en esta ecologia: el orden no cambia que conviene. Ninguna perilla puede codificarlo; hay que cambiar el ENTORNO.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
