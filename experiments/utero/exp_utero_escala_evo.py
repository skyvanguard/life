"""
§16 — ESCALA: ¿el sustrato abierto (v16) EVOLUCIONA con más tiempo y más población?
(docs/PLAN_INTELIGENCIA.md §16; ledger 2026-09-27)

MOTIVO. Tras la cuarta jaula (la variación no escribía operandos) y su
apertura (v16, escritura total), la corrida pre-registrada no mostró ni
regulación ni siquiera ADAPTACIÓN medible: en 30000 ticks con ~30 vivas (~300
generaciones, ~15 hambrunas) la mortalidad en hambrunas sucesivas no baja
(L_A 1/40). La evolución experimental real opera sobre 10³–10⁴ generaciones y
poblaciones de 10³+. Antes de volver a preguntar por regulación hay que
establecer lo previo: ¿evoluciona algo? Aquí: 4× el tiempo (120000 ticks) y
~3× la población (luz finita L0 = 9 en vez de 3; max_n 512), misma ecología
v16 en todo lo demás (hambruna dura, parto costoso, registros lentos, sin
sembrar). Tres brazos: clima (A→B→C), permutado (mismas estaciones, sin
regularidad) y sombra (muertes al azar en igual número, sonda apagada: el
control de que "adaptación" no sea demografía).

LECTURAS (declaradas antes de correr):
  ADAPTACIÓN REFLEJA (¿evoluciona?): dentro de cada mundo, mortalidad media
  durante las hambrunas (A) de la SEGUNDA mitad de la corrida dividida por la
  de la PRIMERA mitad (ambas tras el transitorio de 6000 ticks). Adaptación =
  razón < 1. Se cuenta sobre los 2×20 mundos con sol (clima + permutado: la
  adaptación refleja no necesita regularidad) contra los 20 de sombra.
  Además L_A (Spearman de la ocurrencia k contra la mortalidad al entrar en A,
  nulo por permutación; habituación = rho < 0, p < 0.05), por brazo.
  REGULACIÓN POR ORDEN: R2_A como en v14–v16 (mortalidad en A pareada clima vs
  permutado entre mundos vivos: clima < permutado en ≥ 75% de los pares, p
  signo < 0.05, razón mediana ≤ 0.5).
  CONTACTO: muertes post/pre al entrar en cada estación (mediana); se informa.

VEREDICTO:
  EVOLUCIONA   si la razón tardía/temprana es < 1 en ≥ 70% de los mundos con
               sol (p signo < 0.05) Y la fracción en sombra es menor que la
               mitad de la de sol; o si L_A (habituación) da ≥ 5/40 con sol
               (p binomial < 0.05) y ≥ 2× la sombra.
  VESTIGIO     si además R2_A cumple (regulación por el orden, no sólo por la
               estación). Replicar con otro sol antes de creerlo.
  NADA         si ninguna de las dos.
  Si EVOLUCIONA sin VESTIGIO: el sustrato abierto adapta pero no regula por
  el orden; la pregunta siguiente es de tiempo (¿aparece con más?) y ya no de
  jaula. Si NADA: ni con 6× más partos por mundo aparece adaptación; la
  variación abierta es letal o neutra y hay que medir su espectro de efectos.

    PYTHONPATH=src python experiments/utero/exp_utero_escala_evo.py
"""

from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.inteligencia import aprendizaje, correr_series  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
TICKS = 120000
SEEDS = list(range(20))
SOL_SEED = 0
L0, E0, E_MANT, E_DIF, E_PARTO = 9.0, 2.0, 0.01, 0.25, 0.5
LENTOS, A_BASE, E_COSTO = 0.02, 0.08, 1.0
REGS = (("A", A_BASE, 0.02, 40),) + REGIMENES[1:]
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100,
             energia=True, luz_finita=L0, e0=E0, e_mant=E_MANT, e_dif=E_DIF,
             e_parto=E_PARTO, percepcion=False, lentos=LENTOS, e_costo=E_COSTO,
             escritura_total=True)
TRANSITORIO = 6000
ALPHA, MIN_SEEDS, RATIO = 0.05, 5, 2.0
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_escala_evo"
ARMS = ("clima", "permutado", "sombra")


def fabrica(seed: int, shadow, **flags) -> UteroCreciente:
    return UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                          log_events=True, shadow_deaths=shadow, **flags)


def solo_A(sol: Sol) -> Sol:
    s = type(sol)(seed=sol.seed, ticks=sol.ticks, orden=sol.orden, regimenes=REGS)
    s.estaciones = [e for e in sol.estaciones if e[0] == "A"] + [sol.estaciones[-1]]
    return s


def lecturas(ser: dict, sol: Sol, seed: int) -> dict:
    muertes, vivas = ser["muertes"], ser["vivas"]
    mitad = TRANSITORIO + (TICKS - TRANSITORIO) // 2
    temp, tard, ratios = [], [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < TRANSITORIO or fin > TICKS:
            continue
        if nombre == "A":
            (temp if fin <= mitad else tard).append(muertes[ini:fin].mean())
        if 0 < ini and ini + 100 <= TICKS and muertes[ini - 100:ini].mean() > 0:
            ratios.append(muertes[ini:ini + 100].mean() / muertes[ini - 100:ini].mean())
    la = aprendizaje(muertes, solo_A(sol), rng_seed=seed)
    return dict(
        mA_temp=float(np.mean(temp)) if temp else float("nan"),
        mA_tard=float(np.mean(tard)) if tard else float("nan"),
        adapt=(float(np.mean(tard) / np.mean(temp)) if temp and tard and np.mean(temp) > 0 else float("nan")),
        mA=float(np.mean(temp + tard)) if (temp or tard) else float("nan"),
        contacto=float(np.median(ratios)) if ratios else float("nan"),
        LA_rho=float(la["rho"]), LA_p=float(la["p"]),
        vivas_fin=float(vivas[-1]), vivas_med=float(np.median(vivas[TRANSITORIO:])),
        muertes_t=float(muertes[TRANSITORIO:].mean()), genomas=int(np.nansum(ser["novedad"])),
    )


def job(seed: int) -> tuple:
    clima = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    perm = Sol(seed=SOL_SEED, ticks=TICKS, orden="permutado", regimenes=REGS)
    s_clima = correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica)
    s_perm = correr_series(seed, FLAGS, perm, TICKS, fabrica=fabrica)
    s_somb = correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica,
                           shadow=list(s_clima["muertes"].astype(int)))
    return seed, {"clima": lecturas(s_clima, clima, seed),
                  "permutado": lecturas(s_perm, perm, seed),
                  "sombra": lecturas(s_somb, clima, seed)}


def binom_p(k: int, n: int, p0: float) -> float:
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def signo_p(k: int, n: int) -> float:
    return binom_p(k, n, 0.5)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("ESCALA (v16 abierto): 4x tiempo, ~3x poblacion -- evoluciona algo? adaptacion refleja y R2_A")
    out("=" * 80)
    out(f"linea n0={N0} max {MAX_N}; flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)

    def med(arm, k):
        v = [res[s][arm][k] for s in SEEDS]
        v = [x for x in v if not (isinstance(x, float) and np.isnan(x))]
        return float(np.median(v)) if v else float("nan")

    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<10} {'vivas med':>9} {'vivas fin':>9} {'muertes/t':>9} {'mort A':>7} {'contacto':>8} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<10} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'muertes_t'):>9.3f} "
            f"{med(arm, 'mA'):>7.3f} {med(arm, 'contacto'):>8.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("ADAPTACION REFLEJA: mortalidad en A, segunda mitad / primera mitad (razon < 1 = adapta)")
    conteo = {}
    for arm in ARMS:
        r = [res[s][arm]["adapt"] for s in SEEDS]
        r = [x for x in r if not np.isnan(x)]
        k = sum(1 for x in r if x < 1.0)
        conteo[arm] = (k, len(r))
        out(f"  {arm:<10} razon mediana {np.median(r) if r else float('nan'):.2f}; adapta en {k}/{len(r)} (p signo {signo_p(k, len(r)):.3f})")
    k_sol = conteo["clima"][0] + conteo["permutado"][0]
    n_sol = conteo["clima"][1] + conteo["permutado"][1]
    k_som, n_som = conteo["sombra"]
    frac_sol = k_sol / max(n_sol, 1)
    frac_som = k_som / max(n_som, 1)
    adapta = (frac_sol >= 0.70 and signo_p(k_sol, n_sol) < 0.05 and frac_som < frac_sol / 2)
    out(f"  con sol {k_sol}/{n_sol} ({frac_sol:.2f}, p signo {signo_p(k_sol, n_sol):.3f}); sombra {k_som}/{n_som} ({frac_som:.2f}) -> {'ADAPTA' if adapta else 'no'}")
    out("")
    out("  L_A (habituacion: rho<0, p<0.05) por brazo:")
    LA = {}
    for arm in ARMS:
        LA[arm] = [s for s in SEEDS if res[s][arm]["LA_p"] < ALPHA and res[s][arm]["LA_rho"] < 0]
        out(f"    {arm:<10} {len(LA[arm])}/{len(SEEDS)}  {LA[arm]}")
    k_la = len(LA["clima"]) + len(LA["permutado"])
    la_ok = k_la >= MIN_SEEDS and binom_p(k_la, 2 * len(SEEDS), ALPHA) < 0.05 and k_la >= RATIO * max(len(LA["sombra"]), 1) * 2
    out(f"    con sol {k_la}/{2 * len(SEEDS)} (p binomial {binom_p(k_la, 2 * len(SEEDS), ALPHA):.3f}) vs sombra {len(LA['sombra'])}/{len(SEEDS)} -> {'habituacion' if la_ok else 'no'}")
    out("")
    out("-" * 80)
    out("R2_A. REGULACION POR ORDEN: mortalidad en A pareada, clima vs permutado, entre mundos vivos")
    pares = [(res[s]["clima"]["mA"], res[s]["permutado"]["mA"]) for s in SEEDS
             if res[s]["clima"]["vivas_fin"] > 0 and res[s]["permutado"]["vivas_fin"] > 0
             and not np.isnan(res[s]["clima"]["mA"]) and not np.isnan(res[s]["permutado"]["mA"])]
    k = sum(1 for a, b in pares if a < b)
    razon = float(np.median([a / b if b > 0 else np.nan for a, b in pares])) if pares else float("nan")
    r2 = len(pares) >= 8 and k / len(pares) >= 0.75 and signo_p(k, len(pares)) < 0.05 and razon <= 0.5
    out(f"  clima < permutado en {k}/{len(pares)} pares vivos (p signo {signo_p(k, max(len(pares), 1)):.3f}); razon mediana {razon:.2f} -> {'si' if r2 else 'no'}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    evol = adapta or la_ok
    if evol and r2:
        out("=> VESTIGIO: adapta Y regula por el orden. ANTES DE CREERLO: replicar con otro sembrado del sol.")
    elif evol:
        out(f"=> EVOLUCIONA sin vestigio: adaptacion refleja {'por razon tardia/temprana' if adapta else ''}{' y ' if adapta and la_ok else ''}{'por habituacion L_A' if la_ok else ''}; R2_A no.")
    else:
        out(f"=> NADA: ni adaptacion refleja (sol {frac_sol:.2f} vs sombra {frac_som:.2f}; L_A {k_la}/{2 * len(SEEDS)}) ni regulacion (R2_A {k}/{len(pares)}, razon {razon:.2f}).")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
