"""
CONTROL POSITIVO — un organismo diseñado a mano que ANTICIPA la hambruna en la
ecología de v12/v13. (docs/PLAN_INTELIGENCIA.md §10; ledger 2026-09-26)

Catorce corridas sin vestigio no dicen nada si no sabemos (a) que anticipar es
VIABLE en este sustrato, (b) que es VENTAJOSO frente al tejido evolucionado, y
(c) que nuestras varas PUEDEN verlo. Este experimento no busca emergencia:
construye el organismo y lo mide. Si persiste, prospera y las varas lo ven,
los negativos anteriores significan "no emergió"; si no persiste, significan
"no podía"; si persiste pero las varas no lo ven, las varas están mal.

EL ORGANISMO ("el ahorrador"). Registros [vl, v, vr, R3, S1, S2] (lentos=λ,
sin percepción). Cada tick:
  1. S2 ← vl (escritura lenta, τ=1/λ): S2 sigue el nivel del sol que la celda
     siente en el vacío contiguo (o el de su vecina, que a su vez lo sigue):
     un DETECTOR DE ESTACIÓN (A≈0.17, C≈0.5, B≈0.75).
  2. THR(S2 > 0.5)·0.9375 → MUTO(pos_SPAWN): el opcode en la posición del
     SPAWN se reescribe a 9 (SPAWN) sólo en B, la abundancia, y a 0 (NOP) en C
     y A. Control de flujo por AUTO-REESCRITURA, la única forma de condicionar
     en este VM. Parir sólo en B = ahorrar en C, la estación que precede a la
     hambruna A: anticipación funcional de la hambruna.
  3. R3 = v·v (materia sensible, cae a 0: ingreso = |0 − sol| = sol, máximo).

BRAZOS (mismo sol seed 0, luz finita L0=3, e_mant=0.01, e0=2, λ=0.02):
  ahorrador     16 copias del organismo como población inicial (germinal ON:
                sus crías mutan; veremos si la estrategia se mantiene)
  evolucionado  población inicial aleatoria (= v13 con λ=0.02)
  ahorrador-perm el organismo bajo orden permutado (¿le sirve el orden?)
MEDIDAS (declaradas antes de correr):
  V. viabilidad: vivas por estación (A/B/C) en maduro; fracción de celdas que
     conservan la estructura del ahorrador (instrucciones 1–3 intactas).
  E. ventaja: energía media por celda al ENTRAR en A (ahorrador vs
     evolucionado) y muertes durante A.
  D. detectabilidad: nacimientos por estación (¿sólo en B?) y las varas A_n /
     A_e / L_A sobre el ahorrador.
VEREDICTO: VIABLE Y VENTAJOSO si el ahorrador persiste (≥ 20 vivas en maduro
en ≥ 1/2 de las semillas) y entra en A con más energía y muere menos en A que
el evolucionado; DETECTABLE si nacimientos en B ≥ 5× que en C y A. Si no es
viable, la anticipación no puede evolucionar aquí; si es viable y ventajoso
pero no emergió en 14 corridas, el cuello es el CAMINO evolutivo, no la
ventaja.

    PYTHONPATH=src python experiments/utero/exp_utero_control_positivo.py
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.inteligencia import anticipacion, aprendizaje  # noqa: E402
from zeta_life.utero.nivel2 import ADD, CONST, MUL, MUTO, SPAWN, THR, K  # noqa: E402
from zeta_life.utero.sol import Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 20000
SEEDS = list(range(20))
LAM = 0.02
FLAGS = dict(memoria=False, invasion="asentada", eq_window=100, energia=True, luz_finita=3.0,
             e0=2.0, e_mant=0.01, lentos=LAM)
POS_SPAWN = 6
MATURE = 6000
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_control_positivo"

# registros: 0 vl, 1 v, 2 vr, 3 R3, 4 S1, 5 S2  (campos indexan mod 6; 0 y 2 se usan de borrador)
POS_SPAWN = 9
AHORRADOR = np.zeros((K, 4), dtype=np.int64)
AHORRADOR[0] = (ADD, 0, 3, 5)        # S2 <- vl + R3(=0 al inicio): DETECTOR DE ESTACIÓN (escritura lenta)
AHORRADOR[1] = (CONST, 10, 0, 0)     # r0 <- 0.5  (umbral: C ≈ 0.5, B ≈ 0.75)
AHORRADOR[2] = (THR, 5, 0, 2)        # r2 <- 1 si S2 > 0.5 (estamos en B)
AHORRADOR[3] = (CONST, 11, 0, 0)     # r0 <- 0.75
AHORRADOR[4] = (MUL, 2, 0, 2)        # r2 <- THR·0.75
AHORRADOR[5] = (CONST, 13, 0, 0)     # r0 <- 1.25
AHORRADOR[6] = (MUL, 2, 0, 2)        # r2 <- THR·0.9375  -> int(·10) = 9 (SPAWN) en B, 0 (NOP) si no
AHORRADOR[7] = (MUTO, POS_SPAWN, 2, 0)   # reescribe SU PROPIO SPAWN según la estación: control de flujo
AHORRADOR[8] = (MUL, 1, 1, 3)        # R3 <- v·v : materia sensible (no ciega), v tiende a 0 = ingreso máximo
AHORRADOR[9] = (SPAWN, 1, 3, 12)     # pare a la derecha (sólo existe como SPAWN cuando la 7 lo restaura)


def firma(code: np.ndarray) -> bool:
    """La estructura del ahorrador sigue intacta (detector, umbral y reescritura del SPAWN)."""
    return all(tuple(code[k]) == tuple(AHORRADOR[k]) for k in (0, 2, 7, 8))


def correr(seed: int, arm: str) -> dict:
    orden = "permutado" if arm.endswith("perm") else "ciclico"
    sol = Sol(seed=0, ticks=TICKS, orden=orden)
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                       log_events=True, **FLAGS)
    if arm.startswith("ahorrador"):
        for i in range(N0):
            u.code[i] = AHORRADOR
    vivas = np.zeros(TICKS)
    nac = np.zeros(TICKS)
    muertes = np.zeros(TICKS)
    e_media = np.zeros(TICKS)
    firmas = np.zeros(TICKS)
    for t in range(TICKS):
        m = u.step()
        vivas[t] = int(u.alive.sum())
        nac[t] = m["colonized"] + m["grown"] + m.get("invaded", 0)
        muertes[t] = m["deaths"]
        e_media[t] = float(u.e[u.alive].mean()) if u.alive.any() else 0.0
        idx = np.flatnonzero(u.alive)
        firmas[t] = float(np.mean([firma(u.code[i]) for i in idx])) if len(idx) else 0.0
    # por estación (maduro)
    por = {"A": [], "B": [], "C": []}
    nac_por = {"A": [], "B": [], "C": []}
    e_entra_A, muertes_A = [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < MATURE:
            continue
        por[nombre].append(vivas[ini:fin].mean())
        nac_por[nombre].append(nac[ini:fin].sum() / max(fin - ini, 1) * 100)   # por 100 ticks
        if nombre == "A":
            e_entra_A.append(e_media[max(ini - 1, 0)])
            muertes_A.append(muertes[ini:fin].sum() / max(fin - ini, 1) * 100)
    return dict(seed=seed, arm=arm,
                vivas={k: float(np.mean(v)) if v else 0.0 for k, v in por.items()},
                nac={k: float(np.mean(v)) if v else 0.0 for k, v in nac_por.items()},
                e_A=float(np.mean(e_entra_A)) if e_entra_A else float("nan"),
                muertes_A=float(np.mean(muertes_A)) if muertes_A else float("nan"),
                firma=float(firmas[MATURE:].mean()), vivas_fin=float(vivas[-1]),
                A_n=anticipacion(-nac, sol, rng_seed=seed, regimenes=("C",)),
                A_e=anticipacion(e_media, sol, rng_seed=seed, regimenes=("C",), detrend=True),
                L_A=aprendizaje(muertes, sol, rng_seed=seed))


def job(a):
    return correr(*a)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    arms = ("ahorrador", "evolucionado", "ahorrador-perm")
    out("=" * 80)
    out("CONTROL POSITIVO -- el ahorrador: pare solo en la abundancia (B), ahorra en C, sobrevive A")
    out("=" * 80)
    out(f"flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; medidas declaradas en el docstring")
    out("")
    res: dict = {a: {} for a in arms}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in arms for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r

    out("-" * 80)
    out("V. VIABILIDAD (maduro): vivas por estacion, firma intacta, semillas con >=20 vivas")
    out(f"  {'brazo':<15} {'N_A':>6} {'N_B':>6} {'N_C':>6} {'firma':>6} {'>=20 vivas':>10} {'fin':>5}")
    for a in arms:
        R = res[a].values()
        viv = [r["vivas"] for r in R]
        out(f"  {a:<15} {np.median([v['A'] for v in viv]):>6.0f} {np.median([v['B'] for v in viv]):>6.0f} "
            f"{np.median([v['C'] for v in viv]):>6.0f} {np.median([r['firma'] for r in R]):>6.2f} "
            f"{sum(1 for r in R if r['vivas_fin'] >= 20):>7}/{len(SEEDS):<2} {np.median([r['vivas_fin'] for r in R]):>5.0f}")
    out("")
    out("E. VENTAJA: energia media al ENTRAR en A y muertes por 100 ticks durante A (medianas)")
    for a in arms:
        R = list(res[a].values())
        out(f"  {a:<15} e_entra_A {np.nanmedian([r['e_A'] for r in R]):>6.3f}   muertes_A/100t {np.nanmedian([r['muertes_A'] for r in R]):>6.2f}")
    out("")
    out("D. DETECTABILIDAD: nacimientos por 100 ticks por estacion (medianas) y varas")
    for a in arms:
        R = list(res[a].values())
        n = {k: np.median([r["nac"][k] for r in R]) for k in ("A", "B", "C")}
        pos = {v: sum(1 for r in R if not np.isnan(r[v]["p"]) and r[v]["p"] < 0.05
                      and (r[v].get("estadistico", 1) > 0 if v != "L_A" else True)) for v in ("A_n", "A_e", "L_A")}
        out(f"  {a:<15} nac A {n['A']:>6.2f}  B {n['B']:>6.2f}  C {n['C']:>6.2f}   "
            f"A_n {pos['A_n']:>2}/{len(SEEDS)}  A_e {pos['A_e']:>2}/{len(SEEDS)}  L_A {pos['L_A']:>2}/{len(SEEDS)}")

    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    ah, ev = list(res["ahorrador"].values()), list(res["evolucionado"].values())
    viable = sum(1 for r in ah if r["vivas_fin"] >= 20) >= len(SEEDS) / 2
    ventaja = (np.nanmedian([r["e_A"] for r in ah]) > np.nanmedian([r["e_A"] for r in ev])
               and np.nanmedian([r["muertes_A"] for r in ah]) < np.nanmedian([r["muertes_A"] for r in ev]))
    nB = np.median([r["nac"]["B"] for r in ah])
    detect = nB >= 5 * max(np.median([r["nac"]["A"] for r in ah]), np.median([r["nac"]["C"] for r in ah]), 1e-9)
    out(f"  viable: {viable}   ventajoso: {ventaja}   detectable (nace solo en B): {detect}")
    if not viable:
        out("=> NO VIABLE: la anticipacion disenada no persiste en este sustrato; no podia emerger.")
    elif viable and ventaja:
        out("=> VIABLE Y VENTAJOSO: anticipar paga aqui; que no emergiera en 14 corridas senala el CAMINO evolutivo.")
    else:
        out("=> VIABLE PERO SIN VENTAJA: la anticipacion no paga en esta ecologia; el entorno no la selecciona.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
