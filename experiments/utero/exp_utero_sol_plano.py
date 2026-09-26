"""
El sol en el PLANO, con la vara ENMENDADA (docs/PLAN_INTELIGENCIA.md §5.3 y §6b).

En la línea 1-D el tejido maduro es un cristal: el sol que calienta mueve su
superficie (corr 0.92) y nada muere ni cambia (muertes 0.000 en maduro): SIN
CONTACTO. En el plano el tejido no es un cristal —llena la placa, muere y acuña
sin parar (muertes/tick 0.2, decenas de miles de genomas)— y la superficie de
contacto es grande (paredes + vacíos). Mismo sustrato (`UteroPlano` 32×32,
bloque 8×8, memoria + invasión asentada), sol que calienta la superficie
(κ=0.5) y sonda climática.

Vara enmendada: (1) CONTACTO previo — muertes post/pre ≥ 1.2 al inicio de
estación; (2) conteo con p binomial < 0.05 contra la tasa nominal; (3) ≥ 2×
el máximo de los controles (sin sol, sombra) Y ≥ 2× el brazo con ORDEN
PERMUTADO (mismas duraciones y regímenes, sucesor al azar).

BRAZOS (20 semillas; 12000 ticks, ~17 estaciones; MIN_SEEDS=4 para n=20 al 5%
—esperado 1— con p binomial < 0.05):
  clima        sol 0, orden cíclico A→B→C
  permutado    sol 0, orden permutado
  sin          sin sol (calendario del clima para las ventanas)
  sombra       sombra de "clima"
SERIES: actividad y muertes (declarado antes de correr, ver
`exp_utero_sol_acople.py`). Cuatro lecturas: A, A_m, L, L_m.
VEREDICTO (escrito antes de correr): VESTIGIO si alguna lectura cumple
(1)+(2)+(3) en el brazo clima; SIN CONTACTO si falla (1); NADA en otro caso.
Si VESTIGIO: barrido de κ y de la seed del sol antes de creerlo.

    PYTHONPATH=src python experiments/utero/exp_utero_sol_plano.py
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
from zeta_life.utero.plano import UteroPlano  # noqa: E402
from zeta_life.utero.sol import Sol  # noqa: E402

H = W = 32
BLOQUE = 8
TICKS = 12000
SEEDS = list(range(20))
SOL_SEED = 0
KAPPA = 0.5
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100, sol_acople=KAPPA, sol_sonda=True)
ALPHA, MIN_SEEDS, RATIO, CONTACTO = 0.05, 4, 2.0, 1.2
MATURE = (4000, 12000)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol_plano"
ARMS = ("clima", "permutado", "sin", "sombra")


def fabrica(seed: int, shadow, **flags) -> UteroPlano:
    return UteroPlano(h=H, w=W, seed=seed, bloque=BLOQUE, log_events=True,
                      shadow_deaths=shadow, **flags)


def job(seed: int) -> tuple:
    clima = Sol(seed=SOL_SEED, ticks=TICKS)
    perm = Sol(seed=SOL_SEED, ticks=TICKS, orden="permutado")
    series = {"clima": correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica),
              "permutado": correr_series(seed, FLAGS, perm, TICKS, fabrica=fabrica),
              "sin": correr_series(seed, FLAGS, None, TICKS, fabrica=fabrica)}
    series["sombra"] = correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica,
                                     shadow=list(series["clima"]["muertes"].astype(int)))
    cal = {"clima": clima, "permutado": perm, "sin": clima, "sombra": clima}
    out = {}
    for arm, ser in series.items():
        for tag, serie in (("", ser["actividad"]), ("_m", ser["muertes"])):
            out[("A" + tag, arm)] = anticipacion(serie, cal[arm], rng_seed=seed)
            out[("L" + tag, arm)] = aprendizaje(serie, cal[arm], rng_seed=seed)
        out[("contacto", arm)] = contacto(ser["muertes"], cal[arm])
        out[("vivas", arm)] = float(np.median(ser["vivas"][MATURE[0]:]))
        out[("muertes", arm)] = float(ser["muertes"][MATURE[0]:].mean())
    return seed, out


def contacto(muertes: np.ndarray, sol: Sol) -> float:
    ratios = []
    for _, ini, _ in sol.estaciones[1:-1]:
        if ini - 100 >= 0 and ini + 100 <= len(muertes):
            pre, post = muertes[ini - 100:ini].mean(), muertes[ini:ini + 100].mean()
            if pre > 0:
                ratios.append(post / pre)
    return float(np.median(ratios)) if ratios else float("nan")


def binom_p(k: int, n: int, p0: float) -> float:
    return float(sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)))


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("EL SOL EN EL PLANO, CON LA VARA ENMENDADA (contacto previo, p binomial, brazo permutado)")
    out("=" * 80)
    out(f"plano {H}x{W} bloque {BLOQUE}; flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring; PLAN §6b)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            if i % 5 == 0:
                print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)

    out("-" * 80)
    out("CONTACTO y ESTADO por brazo (mediana sobre semillas)")
    cont = {}
    for arm in ARMS:
        c = np.array([res[s][("contacto", arm)] for s in SEEDS])
        cont[arm] = float(np.nanmedian(c))
        out(f"  {arm:<10} muertes post/pre {cont[arm]:.3f}  vivas {np.median([res[s][('vivas', arm)] for s in SEEDS]):.0f}  "
            f"muertes/tick {np.median([res[s][('muertes', arm)] for s in SEEDS]):.3f}  "
            f"semillas con contacto>=1.2: {int(np.nansum(c >= CONTACTO))}")
    hay_contacto = cont["clima"] >= CONTACTO

    def conteo(vara, arm):
        key = "estadistico" if vara.startswith("A") else "rho"
        signo = vara.startswith("A")
        return [s for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"])
                and res[s][(vara, arm)]["p"] < ALPHA and (res[s][(vara, arm)][key] > 0 or not signo)]

    lecturas = ("A", "A_m", "L", "L_m")
    C = {v: {arm: conteo(v, arm) for arm in ARMS} for v in lecturas}
    out("")
    out("-" * 80)
    out("POSITIVAS POR LECTURA Y BRAZO (p<0.05; A con stat>0)")
    out(f"  {'lectura':<8} " + " ".join(f"{arm:>10}" for arm in ARMS) + "   p_binom(clima)  cumple(2)  cumple(3)")
    cumplen = []
    for v in lecturas:
        n_eval = sum(1 for s in SEEDS if not np.isnan(res[s][(v, "clima")]["p"]))
        k = len(C[v]["clima"])
        pb = binom_p(k, max(n_eval, 1), ALPHA)
        c2 = k >= MIN_SEEDS and pb < 0.05
        c3 = k >= RATIO * max(len(C[v]["sin"]), len(C[v]["sombra"]), 1) and k >= RATIO * max(len(C[v]["permutado"]), 1)
        if c2 and c3:
            cumplen.append(v)
        out(f"  {v:<8} " + " ".join(f"{len(C[v][arm]):>10}" for arm in ARMS) + f"   {pb:>13.3f}  {str(c2):>9}  {str(c3):>9}")
    for v in lecturas:
        out(f"  {v}: clima {C[v]['clima']}  permutado {C[v]['permutado']}  sin {C[v]['sin']}  sombra {C[v]['sombra']}")
    for v in ("L", "L_m"):
        hab = [s for s in C[v]["clima"] if res[s][(v, "clima")]["rho"] < 0]
        out(f"  habituacion en clima ({v}): {hab}")

    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if not hay_contacto:
        out(f"=> SIN CONTACTO: muertes post/pre en clima = {cont['clima']:.2f} < {CONTACTO}. No se lee como 'sin inteligencia'.")
    elif cumplen:
        out(f"=> VESTIGIO en {cumplen} (contacto {cont['clima']:.2f}). ANTES DE CREERLO: barrido de kappa y de la seed del sol.")
    else:
        out(f"=> NADA (con contacto {cont['clima']:.2f}): ninguna lectura cumple p binomial < 0.05 y 2x controles y 2x permutado.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
