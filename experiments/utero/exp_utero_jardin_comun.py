"""
§23 — JARDÍN COMÚN: ¿el genoma evolucionado le gana a su ancestro?
(docs/PLAN_INTELIGENCIA.md §23; ledger 2026-09-27)

MOTIVO. §21: la selección barre programas fijos de forma determinista (el
mismo genoma gana en 5/5 réplicas). §17/§20/§22: con herencia de cambios no
aparece adaptación en la vara de mortalidad en la hambruna, a ninguna tasa.
Hipótesis restante: la vara mide el rasgo equivocado; lo que la ecología
selecciona es capacidad competitiva (colonizar, sostenerse), no sobrevivir a
la hambruna. La evolución experimental mide la adaptación sin nombrar el
rasgo: competencia en JARDÍN COMÚN del evolucionado contra el ancestro.

DISEÑO (por semilla s, 20 semillas, ecología de §17, sol seed 0 cíclico):
  ANCESTRO A_s: el genoma dominante al final de un mundo CONGELADO de la
    sopa s (30000 ticks) — el mejor programa fijo de esa sopa (§21).
  EVOLUCIONADO E_s: el genoma dominante al final de un mundo ABIERTO de la
    misma sopa tras 120000 ticks; dos regímenes: p = 0.02 (carga baja, §22) y
    p = 1 (escritura en cada parto).
  COMPETENCIA: mundo CONGELADO de 16 celdas, 8 con A_s y 8 con E_s, en dos
    disposiciones (E en las pares / E en las impares) para anular la posición;
    30000 ticks; medida = fracción de E entre las vivas al final (media de las
    dos disposiciones). Si E_s == A_s se registra "sin cambio" y no compite.
VEREDICTO (escrito antes de correr), por régimen:
  ADAPTA      si E gana (fracción ≥ 0.75) en ≥ 15/20 semillas.
  DEGRADA     si E pierde (fracción ≤ 0.25) en ≥ 15/20: la herencia de
              cambios empeora al mejor programa (carga pura).
  NEUTRAL     en otro caso (la evolución abierta no mejora ni empeora la
              competitividad frente al mejor programa fijo de la sopa).
  Si ADAPTA en p = 0.02: el sustrato evoluciona en el rasgo que la ecología
  selecciona y la línea vuelve a la regulación con ese régimen. Si NEUTRAL o
  DEGRADA en ambos: la variación no produce mejora competitiva en 120000
  ticks; el paisaje alrededor del ganador es plano o descendente.

    PYTHONPATH=src python experiments/utero/exp_utero_jardin_comun.py
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.nivel2 import huella  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
T_ANCESTRO, T_EVOL, T_COMP = 30000, 120000, 30000
SEEDS = list(range(20))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
REGIMENES_EVOL = {"p0.02": dict(escritura_total=True, tasa_germinal=0.02),
                  "p1": dict(escritura_total=True)}
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_jardin_comun"


def mundo(seed: int, ticks: int, **flags) -> UteroCreciente:
    sol = Sol(seed=SOL_SEED, ticks=ticks, regimenes=REGS)
    return UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                          **BASE, **flags)


def dominante(u: UteroCreciente):
    vivos = np.flatnonzero(u.alive)
    if len(vivos) == 0:
        return None
    cnt = Counter(huella(u.code[i]) for i in vivos)
    h, _ = cnt.most_common(1)[0]
    for i in vivos:
        if huella(u.code[i]) == h:
            return u.code[i].copy()
    return None


def competir(seed: int, A: np.ndarray, E: np.ndarray, disposicion: int) -> float:
    u = mundo(seed + 1000 * (disposicion + 1), T_COMP, congelado=True)
    hE = huella(E)
    for i in range(N0):
        es_E = (i % 2 == disposicion)
        u.code[i] = E if es_E else A
    for _ in range(T_COMP):
        u.step()
    vivos = np.flatnonzero(u.alive)
    if len(vivos) == 0:
        return float("nan")
    return float(np.mean([huella(u.code[i]) == hE for i in vivos]))


def job(seed: int) -> tuple:
    anc = mundo(seed, T_ANCESTRO, congelado=True)
    for _ in range(T_ANCESTRO):
        anc.step()
    A = dominante(anc)
    out = {"vivas_anc": int(anc.alive.sum())}
    if A is None:
        return seed, out
    for reg, flags in REGIMENES_EVOL.items():
        ev = mundo(seed, T_EVOL, **flags)
        for _ in range(T_EVOL):
            ev.step()
        E = dominante(ev)
        r = {"vivas_evol": int(ev.alive.sum())}
        if E is None:
            r["estado"] = "extinto"
        elif np.array_equal(E, A):
            r["estado"] = "sin cambio"
        else:
            r["estado"] = "compite"
            fr = [competir(seed, A, E, d) for d in (0, 1)]
            r["frac_E"] = fr
            r["frac_E_media"] = float(np.nanmean(fr)) if not all(np.isnan(fr)) else float("nan")
        out[reg] = r
    return seed, out


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("JARDIN COMUN -- el genoma evolucionado (abierto, 120k ticks) contra el mejor programa fijo de su sopa, en mundo congelado")
    out("=" * 80)
    out(f"ecologia {BASE}; regimenes {list(REGIMENES_EVOL)}; {len(SEEDS)} semillas; ancestro {T_ANCESTRO}, evolucion {T_EVOL}, competencia {T_COMP} ticks; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)
    veredictos = {}
    for reg in REGIMENES_EVOL:
        out("-" * 80)
        out(f"REGIMEN {reg}")
        out(f"  {'seed':>4} {'vivas anc':>9} {'vivas evol':>10} {'estado':<11} {'frac E (par, impar)':>20} {'media':>6}")
        gana = pierde = n = 0
        medias = []
        for s in SEEDS:
            r = res[s].get(reg)
            if r is None:
                out(f"  {s:>4} {res[s]['vivas_anc']:>9}   (ancestro extinto)")
                continue
            if r["estado"] != "compite":
                out(f"  {s:>4} {res[s]['vivas_anc']:>9} {r['vivas_evol']:>10} {r['estado']:<11}")
                if r["estado"] == "sin cambio":
                    n += 1
                continue
            n += 1
            m = r["frac_E_media"]
            medias.append(m)
            gana += m >= 0.75
            pierde += m <= 0.25
            out(f"  {s:>4} {res[s]['vivas_anc']:>9} {r['vivas_evol']:>10} {r['estado']:<11} {r['frac_E'][0]:>9.2f} {r['frac_E'][1]:>10.2f} {m:>6.2f}")
        out(f"  semillas evaluables {n}; E gana (>=0.75) {gana}; E pierde (<=0.25) {pierde}; mediana frac E {np.median(medias) if medias else float('nan'):.2f}")
        if gana >= 15:
            veredictos[reg] = "ADAPTA"
        elif pierde >= 15:
            veredictos[reg] = "DEGRADA"
        else:
            veredictos[reg] = "NEUTRAL"
        out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    for reg, v in veredictos.items():
        out(f"=> {reg}: {v}")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
