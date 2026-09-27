"""
§41b — TORNEO DE ESTRATEGIAS CON ORÁCULO: control adversarial de §41.
(docs/PLAN_INTELIGENCIA.md §41; ledger 2026-09-27)

§41 dio HAY ÓPTIMO DE ORDEN enfrentando sólo dos estrategias (X no pare en
C, Y no pare en B). Dos objeciones propias antes de creerlo: (1) el mecanismo
puede ser recolonizar en la estación que SIGUE a la hambruna, no guardar en
la que la precede; (2) si una tercera estrategia (p.ej. parir siempre) les
gana a las dos en ambos calendarios, el óptimo real no depende del orden.

DISEÑO. Modelo reducido (NO el útero), sin mutación, oráculo de estación.
Las OCHO estrategias posibles de parto por estación, (A, B, C) ∈ {0,1}³,
mezcladas en partes iguales celda a celda. 24 mundos por calendario (clima,
ciclo2, permutado), N = 256, 60000 ticks, sol seed 0.
LECTURA (escrita antes de correr): fracción final de cada estrategia entre
las vivas, por mundo; ganadora de un calendario = la de mayor mediana.
  ÓPTIMO DEPENDIENTE DEL ORDEN si la ganadora de clima y la de ciclo2 son
      DISTINTAS, y además cada una supera a la otra en su calendario en ≥ 75%
      de los mundos (p signo < 0.05).
  ÓPTIMO INDEPENDIENTE si gana la misma estrategia en los dos calendarios:
      el orden no cambia qué conviene, y §41 fue un artefacto del par elegido.

    PYTHONPATH=src python experiments/utero/exp_utero_orden_torneo.py
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
ESTRATEGIAS = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], dtype=float)   # (8, 3): A, B, C
RESULTS = HERE.parents[1] / "results"
NAME = "utero_orden_torneo"


def nombre_e(e) -> str:
    return "".join(n for n, x in zip("ABC", e) if x > 0) or "nunca"


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("TORNEO CON ORACULO (modelo reducido, sin mutacion): las 8 estrategias de parto por estacion, partes iguales")
    out("=" * 80)
    out(f"N={N}; {W} mundos por calendario; {TICKS} ticks; lectura pre-registrada (docstring); la estrategia se nombra por las estaciones en que pare")
    out("")
    rng = np.random.default_rng(2029)
    fr = {}
    t0 = time.time()
    for nombre, orden in CALENDARIOS.items():
        sol = Sol(seed=B.SOL_EVOL, ticks=TICKS, orden=orden, regimenes=B.REGS)
        est = Q.estaciones_por_tick(sol, TICKS)
        m = Q.ModeloQ(W, rng)
        cual = rng.integers(0, 8, size=(W, N))
        m.q = ESTRATEGIAS[cual]
        soles = np.tile(sol.serie, (W, 1))
        for t in range(TICKS):
            m.forzado = np.full(W, est[t])
            m.paso(soles[:, t:t + 1], True, None)
        f = np.zeros((W, 8))
        for w in range(W):
            if m.alive[w].any():
                qa = m.q[w][m.alive[w]]
                for k in range(8):
                    f[w, k] = np.all(qa == ESTRATEGIAS[k], axis=1).mean()
            else:
                f[w] = np.nan
        fr[nombre] = f
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    out("  fraccion final (mediana entre mundos) por estrategia:")
    out(f"  {'pare en':<8} " + " ".join(f"{c:>10}" for c in CALENDARIOS))
    for k in range(8):
        out(f"  {nombre_e(ESTRATEGIAS[k]):<8} " + " ".join(f"{np.nanmedian(fr[c][:, k]):>10.2f}" for c in CALENDARIOS))
    gan = {c: int(np.nanargmax(np.nanmedian(fr[c], axis=0))) for c in CALENDARIOS}
    out("")
    for c in CALENDARIOS:
        g = gan[c]
        out(f"  ganadora de {c:<10}: pare en {nombre_e(ESTRATEGIAS[g]):<6} (mediana {np.nanmedian(fr[c][:, g]):.2f}; la mayor en {int((np.nanargmax(fr[c], axis=1) == g).sum())}/{W} mundos)")
    out("")
    out("=" * 80)
    out("LECTURA (regla escrita antes de correr)")
    a, b = gan["clima"], gan["ciclo2"]
    if a == b:
        out(f"=> OPTIMO INDEPENDIENTE DEL ORDEN: gana la misma estrategia (pare en {nombre_e(ESTRATEGIAS[a])}) bajo clima y bajo ciclo2. §41 fue un artefacto del par elegido.")
    else:
        k1 = int((fr["clima"][:, a] > fr["clima"][:, b]).sum())
        k2 = int((fr["ciclo2"][:, b] > fr["ciclo2"][:, a]).sum())
        ok = k1 / W >= 0.75 and B.signo_p(k1, W) < 0.05 and k2 / W >= 0.75 and B.signo_p(k2, W) < 0.05
        out(f"  bajo clima, '{nombre_e(ESTRATEGIAS[a])}' supera a '{nombre_e(ESTRATEGIAS[b])}' en {k1}/{W} (p {B.signo_p(k1, W):.3f}); "
            f"bajo ciclo2, '{nombre_e(ESTRATEGIAS[b])}' supera a '{nombre_e(ESTRATEGIAS[a])}' en {k2}/{W} (p {B.signo_p(k2, W):.3f})")
        out("=> OPTIMO DEPENDIENTE DEL ORDEN: las ganadoras difieren y cada una supera a la otra en su calendario." if ok
            else "=> NO CONCLUYENTE: las ganadoras difieren pero no se superan con la regla exigida.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
