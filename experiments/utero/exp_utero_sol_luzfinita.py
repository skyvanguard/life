"""
v12 LUZ FINITA bajo el sol — capacidad de carga estacional: el escenario mínimo
donde anticipar paga (docs/PLAN_INTELIGENCIA.md; ledger 2026-09-26).

Diez negativos convergen en la bifurcación: con ingreso individual el tejido es
inmortal o se extingue, porque nada regula la población. Con un recurso
COMPARTIDO y FINITO —la luz de cada tick, L = L0·sol(t), repartida entre las
vivas según |v − sol|— la población se autorregula hacia N* = L/e_mant, que
sigue a la estación: A (sol bajo) es hambruna, B abundancia, C intermedia.
Calibración (4 semillas × 12 configuraciones, por capacidad de carga, vida y
contacto, nunca por A/L): con L0=3, e_mant=0.01 la población de la seed 13
sigue a la estación (93 / 159 / 167 celdas en A / B / C) y las muertes se
duplican al entrar en A; la percepción (mod 5) mata a la 13 y ayuda a la 35 y
la 21: la corrida principal va SIN percepción; si da nada, sigue una con ella.

BRAZOS: clima (A→B→C) · ciclo2 (A→C→B: la hambruna sigue a B) · permutado ·
sin sol · sombra de clima. 40 semillas, 20000 ticks.
LECTURAS (vara enmendada: contacto bilateral previo; p binomial < 0.05, ≥ 2×
controles y ≥ 2× permutado):
  A, A_m, L, L_m: como antes (actividad y muertes).
  A_n: ANTICIPACIÓN DE LA HAMBRUNA — en las estaciones largas que PRECEDEN a A
       (C en clima, B en ciclo2), ¿bajan los NACIMIENTOS alrededor del instante
       esperado del cambio, sin que haya ocurrido? (sobre −nacimientos).
  A_e: ¿sube la ENERGÍA MEDIA por celda en ese mismo instante? (ahorro previo).
  En permutado ninguna estación precede a A de forma fija: A_n/A_e se calculan
  sobre todas las largas (nulo estructural).
VEREDICTO (escrito antes de correr): VESTIGIO si alguna lectura cumple las
tres condiciones en clima o en ciclo2; SIN CONTACTO si las muertes no cambian
al entrar en A; NADA en otro caso. Si VESTIGIO: réplica con otro sembrado del
sol y barrido de L0 antes de creerlo.

CORRIDA 2 (réplica, declarada tras la corrida 1): A_e dio 9/40 (p<0.001) en
clima pero los controles 3/5/4 (≥2× exige 10) y el brazo SIN SOL con 5 mostró
que el estadístico sobre el NIVEL de energía está inflado por deriva. Cambios
declarados antes de correr: sol seed 1; percepción ON (la variable lenta
legible); A_e sobre la DERIVADA de la energía media (ritmo de ahorro). Mismo
veredicto. Se compara con la corrida 1: si A_e vuelve a superar la tasa
nominal en clima Y ahora supera 2× los controles, es vestigio; si no, la
corrida 1 fue el sesgo del nivel.

    PYTHONPATH=src python experiments/utero/exp_utero_sol_luzfinita.py
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
from zeta_life.utero.inteligencia import anticipacion, aprendizaje, correr_series  # noqa: E402
from zeta_life.utero.sol import Sol  # noqa: E402

N0, MAX_N = 16, 256
TICKS = 20000
SEEDS = list(range(40))
SOL_SEED = 1
KAPPA = 0.5
E_MANT, E_DIF, E_PARTO = 0.01, 0.25, 0.5
L0, E0, PERCEPCION = 3.0, 2.0, True         # corrida 2 (réplica): otro sol (seed 1), percepción ON, A_e sobre la derivada
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100,
             energia=True, luz_finita=L0, e0=E0, e_mant=E_MANT, e_dif=E_DIF,
             e_parto=E_PARTO, percepcion=PERCEPCION)
PRECEDE_A = {"clima": ("C",), "ciclo2": ("B",), "permutado": None, "sin": ("C",), "sombra": ("C",)}
ALPHA, MIN_SEEDS, RATIO, CONTACTO = 0.05, 5, 2.0, 1.2
MATURE = (6000, 20000)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol_luzfinita2"
ARMS = ("clima", "ciclo2", "permutado", "sin", "sombra")


def fabrica(seed: int, shadow, **flags) -> UteroCreciente:
    return UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                          log_events=True, shadow_deaths=shadow, **flags)


def job(seed: int) -> tuple:
    clima = Sol(seed=SOL_SEED, ticks=TICKS)
    ciclo2 = Sol(seed=SOL_SEED, ticks=TICKS, orden="ciclico_inverso")
    perm = Sol(seed=SOL_SEED, ticks=TICKS, orden="permutado")
    series = {"clima": correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica),
              "ciclo2": correr_series(seed, FLAGS, ciclo2, TICKS, fabrica=fabrica),
              "permutado": correr_series(seed, FLAGS, perm, TICKS, fabrica=fabrica),
              "sin": correr_series(seed, FLAGS, None, TICKS, fabrica=fabrica)}
    series["sombra"] = correr_series(seed, FLAGS, clima, TICKS, fabrica=fabrica,
                                     shadow=list(series["clima"]["muertes"].astype(int)))
    cal = {"clima": clima, "ciclo2": ciclo2, "permutado": perm, "sin": clima, "sombra": clima}
    out = {}
    for arm, ser in series.items():
        for tag, serie in (("", ser["actividad"]), ("_m", ser["muertes"])):
            out[("A" + tag, arm)] = anticipacion(serie, cal[arm], rng_seed=seed)
            out[("L" + tag, arm)] = aprendizaje(serie, cal[arm], rng_seed=seed)
        out[("A_n", arm)] = anticipacion(-ser["nacimientos"], cal[arm], rng_seed=seed,
                                         regimenes=PRECEDE_A[arm])
        em = np.nan_to_num(ser["e_media"], nan=0.0)
        dem = np.concatenate([[0.0], np.diff(em)])       # corrida 2: la DERIVADA (ritmo de ahorro), sin deriva
        out[("A_e", arm)] = anticipacion(dem, cal[arm], rng_seed=seed, regimenes=PRECEDE_A[arm])
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
    out("v12 LUZ FINITA BAJO EL SOL -- capacidad de carga estacional (hambruna en A)")
    out("=" * 80)
    out(f"linea n0={N0} max {MAX_N}; flags {FLAGS}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
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
    hay_contacto = cont["clima"] >= CONTACTO or cont["clima"] <= 1.0 / CONTACTO

    # ---- R2: regulación por orden (muertes pareadas por semilla) ----
    out("")
    out("-" * 80)
    out("R2. REGULACION POR ORDEN: muertes/tick en maduro, pareadas por semilla")
    r2 = {}
    for arm in ("clima", "ciclo2"):
        a = np.array([res[s][("muertes", arm)] for s in SEEDS])
        b = np.array([res[s][("muertes", "permutado")] for s in SEEDS])
        wins = int((a < b).sum())
        razon = float(np.median(a / np.maximum(b, 1e-9)))
        p_sign = binom_p(wins, len(SEEDS), 0.5)
        r2[arm] = dict(wins=wins, razon=razon, p=p_sign,
                       ok=wins >= 27 and p_sign < 0.05 and razon <= 0.5)
        out(f"  {arm:<7} < permutado en {wins}/{len(SEEDS)} semillas (p signo {p_sign:.3f}); "
            f"razon mediana {razon:.2f} -> {'CUMPLE' if r2[arm]['ok'] else 'no'}")
    if r2["clima"]["ok"] and r2["ciclo2"]["ok"]:
        out("  => ambos ordenes regulares viven con menos muertes que el permutado: es la REGULARIDAD")
    elif r2["clima"]["ok"] and not r2["ciclo2"]["ok"]:
        out("  => solo A->B->C es 'suave': son los TIPOS de transicion, no el orden")
    else:
        out("  => sin regulacion por orden")

    def conteo(vara, arm):
        key = "estadistico" if vara.startswith("A") else "rho"
        signo = vara.startswith("A")
        return [s for s in SEEDS if not np.isnan(res[s][(vara, arm)]["p"])
                and res[s][(vara, arm)]["p"] < ALPHA and (res[s][(vara, arm)][key] > 0 or not signo)]

    lecturas = ("A", "A_m", "L", "L_m", "A_n", "A_e")
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
        out(f"=> SIN CONTACTO: muertes post/pre en clima = {cont['clima']:.2f} dentro de [1/{CONTACTO}, {CONTACTO}]. No se lee como 'sin inteligencia'.")
    elif cumplen or (r2["clima"]["ok"] and r2["ciclo2"]["ok"]):
        que = list(cumplen) + (["R2 regularidad"] if (r2["clima"]["ok"] and r2["ciclo2"]["ok"]) else [])
        out(f"=> VESTIGIO en {que} (contacto {cont['clima']:.2f}). ANTES DE CREERLO: barrido de kappa y de la seed del sol.")
    else:
        out(f"=> NADA (con contacto {cont['clima']:.2f}): ninguna lectura cumple; R2 {'solo tipos de transicion' if r2['clima']['ok'] else 'no'}.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
