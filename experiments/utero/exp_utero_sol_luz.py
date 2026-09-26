"""
v11 FOTOSÍNTESIS bajo el sol — la luz cae sobre todo el tejido y la calibración
se hace por VIDA MEDIA de las celdas frente a la estación
(docs/PLAN_INTELIGENCIA.md; ledger 2026-09-26).

Diagnóstico tras ocho negativos: sin costo el tejido queda demasiado FRÍO
(cristal inerte); con el metabolismo de v9/v10 demasiado CALIENTE (recambio del
3–7% por tick, vidas de 20–30 ticks: nada vive una estación de 300–900 ticks,
no hay qué aprender), y el recambio lo ponía la GEOMETRÍA (sólo la superficie
comía) y no el clima. v11: la luz cae sobre todas las celdas (cosecha
e_gan·|v − sol(t)|), sin calor de superficie (empujaba la materia hacia el
hambre) y con la sonda fija (menos confusores); percepción de la propia
energía mantenida. Las manos (e_mant, e_gan) se calibran por vida mediana de
las celdas entre ~1 y ~10 estaciones, muertes concentradas tras los cambios de
estación y tejido vivo — nunca por las varas A/L.

v9 hizo al entorno esencial (sin sol el tejido muere) y no dio vestigio. El
diagnóstico de escala temporal lo explica: la memoria interna del tejido dura
6–150 ticks (materia interior), 4–42 (borde, descontado el sol), mientras las
estaciones duran 300–900; la única variable interna lenta es la energía
(τ≈e0/e_mant=200) y las reglas no la ven. v10: la energía entra a la física
como 5º registro de sólo lectura (los campos indexan mod 5): la celda puede
condicionar su materia, su reescritura y su parto en su propia reserva. Es la
tercera dimensión del boceto original —percepción del propio estado— que
nunca se había tocado. Todo lo demás igual a v9:

Seis entornos sin costo dieron el mismo muro: el tejido maduro converge a un
estado que el entorno no toca, y un sistema al que nada amenaza no tiene nada
que regular ni anticipar. `energia=True`: cada celda paga mantenimiento por
tick, cosecha en la superficie según su DESEQUILIBRIO con el vacío (|v − sol(t)|
en el toro: sólo el gradiente con el mundo alimenta, y el gradiente cambia por
estación), difunde energía con sus vecinas (conservativo), cede una parte a
la cría, y se vacía al agotarse. La conservación de Flow-Lenia/Kruszewski y el
decaimiento de Stringmol: la única presión que la literatura muestra
sostenida sin juez. Sustrato: línea 1-D v6 + sol que calienta (κ=0.5) + sonda
climática + metabolismo; 40 semillas; 20000 ticks. Manos declaradas: e0,
e_mant, e_gan, e_dif, e_parto — calibradas con un sondeo de 3 semillas
juzgado por vivas, muertes y contacto, NO por las varas A/L.

Vara enmendada: (1) CONTACTO previo — la tasa de muertes CAMBIA al inicio de
estación: post/pre ≥ 1.2 o ≤ 1/1.2 (bilateral: el humo de 2 semillas mostró
que bajo el orden cíclico las muertes BAJAN al cambiar de estación, 0.45, y
bajo el permutado suben, 2.67 — ambas son respuesta); (2) conteo con p
binomial < 0.05 contra la tasa nominal; (3) ≥ 2× el máximo de los controles
(sin sol, sombra) Y ≥ 2× el brazo con ORDEN PERMUTADO (mismas duraciones y
regímenes, sucesor al azar).

LECTURA NUEVA, declarada antes de la corrida completa a partir del humo:
  R2 — REGULACIÓN POR ORDEN. Muertes por tick en maduro, pareadas por semilla:
  clima (A→B→C) vs permutado. Si el tejido explota la regularidad, vive con
  menos muertes en el mundo predecible que en el impredecible con la MISMA
  estadística de regímenes. Control decisivo: ciclo2 (A→C→B), otra
  regularidad con otras transiciones. Si clima y ciclo2 son bajos y permutado
  alto → es la REGULARIDAD; si ciclo2 es tan letal como permutado → son los
  TIPOS de transición, no el orden. Criterio: clima < permutado en ≥ 27/40
  semillas (signo, p < 0.05) con razón mediana ≤ 0.5, y lo mismo para ciclo2
  vs permutado.

BRAZOS (40 semillas; 20000 ticks; MIN_SEEDS=5 para n=40 al 5% —esperado 2—
con p binomial < 0.05):
  clima        sol 0, orden cíclico A→B→C
  permutado    sol 0, orden permutado
  sin          sin sol (calendario del clima para las ventanas)
  sombra       sombra de "clima"
SERIES: actividad y muertes (declarado antes de correr, ver
`exp_utero_sol_acople.py`). Cuatro lecturas: A, A_m, L, L_m.
VEREDICTO (escrito antes de correr): VESTIGIO si alguna lectura cumple
(1)+(2)+(3) en el brazo clima; SIN CONTACTO si falla (1); NADA en otro caso.
Si VESTIGIO: barrido de κ y de la seed del sol antes de creerlo.

    PYTHONPATH=src python experiments/utero/exp_utero_sol_luz.py
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
SOL_SEED = 0
KAPPA = 0.5
E_MANT, E_GAN, E_DIF, E_PARTO = 0.005, 0.02, 0.25, 0.5   # calibrado por vida media/contacto: e_mant/e_gan = 0.25 = distancia tipica en el toro (la unica config con acople a la estacion; el resto bifurca en extincion o inmortalidad)
FLAGS = dict(memoria=True, invasion="asentada", eq_window=100,
             energia=True, energia_luz=True, e_mant=E_MANT, e_gan=E_GAN, e_dif=E_DIF,
             e_parto=E_PARTO, percepcion=True)
ALPHA, MIN_SEEDS, RATIO, CONTACTO = 0.05, 5, 2.0, 1.2
MATURE = (6000, 20000)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_sol_luz"
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
    out("v11 FOTOSINTESIS BAJO EL SOL -- linea 1-D, luz sobre todo el tejido + energia legible")
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
        out(f"=> SIN CONTACTO: muertes post/pre en clima = {cont['clima']:.2f} dentro de [1/{CONTACTO}, {CONTACTO}]. No se lee como 'sin inteligencia'.")
    elif cumplen or (r2["clima"]["ok"] and r2["ciclo2"]["ok"]):
        que = list(cumplen) + (["R2 regularidad"] if (r2["clima"]["ok"] and r2["ciclo2"]["ok"]) else [])
        out(f"=> VESTIGIO en {que} (contacto {cont['clima']:.2f}). ANTES DE CREERLO: barrido de kappa y de la seed del sol.")
    else:
        out(f"=> NADA (con contacto {cont['clima']:.2f}): ninguna lectura cumple; R2 {'solo tipos de transicion' if r2['clima']['ok'] else 'no'}.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
