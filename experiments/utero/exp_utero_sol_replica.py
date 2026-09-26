"""
Réplica del vestigio de anticipación (docs/PLAN_INTELIGENCIA.md, control
obligatorio antes de creer).

Corrida 2 del programa del sol (`exp_utero_sol.py`, brazo CONSECUENTE:
`sol_sonda=True`) disparó la regla pre-registrada: anticipación positiva en
3/40 semillas (0, 1, 12) contra 1 en la sombra y 0 sin sol. Está en el umbral
mínimo (≥ 3) y la p binomial contra la tasa nominal es 0.32: compatible con
azar. El plan exige, antes de creerlo: (a) otro sembrado del sol, (b) el orden
de estaciones permutado.

BRAZOS (mismo sustrato v6 + sol_sonda; 40 semillas; 20000 ticks):
  sol1        sol con seed 1 (otras duraciones, mismo orden A→B→C)
  sol2        sol con seed 2
  permutado   sol seed 0 con orden PERMUTADO (mismas duraciones que la corrida
              2; sucesor al azar): quita la regularidad de orden y deja todo lo
              demás igual. Si la anticipación viniera de aprender el orden,
              aquí debe desaparecer.
  sin         sin sol, evaluado con el calendario de sol1
  sombra      sombra de sol1
PREDICCIONES (antes de mirar):
  P1 Si el vestigio es real, sol1 y sol2 dan ≥ 3/40 positivas cada uno y ≥ 2×
     el máximo de los controles; y las positivas de la corrida 2 (0, 1, 12) no
     tienen por qué repetirse (otro calendario), pero el CONTEO sí.
  P2 permutado da un conteo al nivel de los controles.
  P3 Si sol1 y sol2 quedan al nivel de los controles, el vestigio de la corrida
     2 fue un falso positivo del umbral (esperado 2/40 al 5%).
VEREDICTO: REPLICA si P1 y P2; FALSO POSITIVO si P3; AMBIGUO en otro caso.
Además se reporta la corrida 2 acumulada: conteo total de positivas en 120
semillas-sol (3 soles) contra la tasa nominal (esperado 6), p binomial.

    PYTHONPATH=src python experiments/utero/exp_utero_sol_replica.py
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

from zeta_life.utero.inteligencia import anticipacion, aprendizaje, correr_series  # noqa: E402
from zeta_life.utero.sol import Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 20000
SEEDS = list(range(40))
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100, sol_sonda=True)
ALPHA, MIN_SEEDS, RATIO = 0.05, 3, 2.0
PREVIO = {"conteo": 3, "n": 40, "semillas": [0, 1, 12]}
WORKERS = max(1, min(10, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol_replica"


def soles() -> dict:
    return {"sol1": Sol(seed=1, ticks=TICKS), "sol2": Sol(seed=2, ticks=TICKS),
            "permutado": Sol(seed=0, ticks=TICKS, orden="permutado")}


def job(seed: int) -> tuple:
    S = soles()
    out = {}
    series = {}
    for arm, sol in S.items():
        series[arm] = correr_series(seed, FLAGS, sol, TICKS, n0=N0, max_n=MAX_N)
    series["sin"] = correr_series(seed, FLAGS, None, TICKS, n0=N0, max_n=MAX_N)
    series["sombra"] = correr_series(seed, FLAGS, S["sol1"], TICKS,
                                     shadow=list(series["sol1"]["muertes"].astype(int)),
                                     n0=N0, max_n=MAX_N)
    cal = {"sol1": S["sol1"], "sol2": S["sol2"], "permutado": S["permutado"],
           "sin": S["sol1"], "sombra": S["sol1"]}
    for arm, ser in series.items():
        out[("A", arm)] = anticipacion(ser["actividad"], cal[arm], rng_seed=seed)
        out[("L", arm)] = aprendizaje(ser["actividad"], cal[arm], rng_seed=seed)
        out[("vivas", arm)] = float(np.median(ser["vivas"][6000:]))
    return seed, out


def binom_p(k: int, n: int, p0: float) -> float:
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    arms = ("sol1", "sol2", "permutado", "sin", "sombra")
    out("=" * 80)
    out("REPLICA DEL VESTIGIO DE ANTICIPACION (sol consecuente): otros soles y orden permutado")
    out("=" * 80)
    out(f"flags {FLAGS}; 40 semillas; {TICKS} ticks; previo: {PREVIO}; workers={WORKERS}")
    out("predicciones y veredicto en el docstring, escritos antes de correr")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            if i % 10 == 0:
                print(f"  ... {i}/40 semillas", flush=True)

    def conteo(vara, arm, signo):
        key = "estadistico" if vara == "A" else "rho"
        return [s for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"])
                and res[s][(vara, arm)]["p"] < ALPHA and (res[s][(vara, arm)][key] > 0 or not signo)]

    for vara, signo, titulo in (("A", True, "ANTICIPACION"), ("L", False, "APRENDIZAJE POR RECURRENCIA")):
        out("-" * 80)
        out(f"{vara}. {titulo}: positivas por brazo (p<0.05" + (", stat>0" if signo else "") + ")")
        C = {arm: conteo(vara, arm, signo) for arm in arms}
        for arm in arms:
            n_eval = sum(1 for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"]))
            out(f"  {arm:<10} {len(C[arm]):>2}/{n_eval}  {C[arm]}   p binomial vs 0.05: "
                f"{binom_p(len(C[arm]), max(n_eval, 1), ALPHA):.3f}")
        if vara == "A":
            CA = C
        out("")
    out("  vivas mediana (maduro) por brazo: " + ", ".join(
        f"{arm} {np.median([res[s][('vivas', arm)] for s in SEEDS]):.0f}" for arm in arms))

    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    ctrl = max(len(CA["sin"]), len(CA["sombra"]))
    ok1 = len(CA["sol1"]) >= MIN_SEEDS and len(CA["sol1"]) >= RATIO * max(ctrl, 1)
    ok2 = len(CA["sol2"]) >= MIN_SEEDS and len(CA["sol2"]) >= RATIO * max(ctrl, 1)
    perm_bajo = len(CA["permutado"]) <= max(ctrl, 2)
    total = PREVIO["conteo"] + len(CA["sol1"]) + len(CA["sol2"])
    p_total = binom_p(total, 3 * 40, ALPHA)
    if ok1 and ok2 and perm_bajo:
        v = "REPLICA"
    elif not ok1 and not ok2:
        v = "FALSO POSITIVO"
    else:
        v = "AMBIGUO"
    out(f"=> {v}: sol1 {len(CA['sol1'])}, sol2 {len(CA['sol2'])}, permutado {len(CA['permutado'])}, "
        f"controles max {ctrl}; acumulado 3 soles {total}/120 (esperado 6 al azar), p binomial {p_total:.3f}")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
