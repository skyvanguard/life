"""
§20 — ¿EVOLUCIONA SIN EL BIEN COMÚN? §17 repetido con la difusión de energía apagada.
(docs/PLAN_INTELIGENCIA.md §20; ledger 2026-09-27)

HIPÓTESIS (escrita antes de correr). §17: el sustrato no evoluciona (la
mortalidad per cápita en la hambruna baja más en el brazo congelado que con
variación). §18: la energía al empezar la hambruna predice quién sobrevive en
casi todos los mundos; el genoma, en la mitad y débilmente, aunque su efecto
es repetible. En la ecología hay DIFUSIÓN CONSERVATIVA DE ENERGÍA entre
vecinas (e_dif = 0.25): la reserva es un bien común local. Un programa que
ingresa más (por su materia frente al sol) reparte la ganancia con sus
vecinas, sean del genoma que sean; la ventaja heredable se socializa y la
selección individual sobre el ingreso se neutraliza (polizón). Predicción: con
e_dif = 0 la mortalidad per cápita en la hambruna baja MÁS con variación
(abierta o cerrada) que en el congelado. Si no ocurre, la difusión no era la
causa y quedan el canje supervivencia/fecundidad o la posición.

DISEÑO Y VEREDICTO: idénticos a §17 (mismos brazos, semillas, sol, ticks,
lectura primaria y regla), con la única diferencia e_dif = 0.0. Viabilidad
comprobada en humo antes de lanzar (los tres brazos viven sin difusión).
  EVOLUCIONA (brazo X) si razón_X < razón_congelado en ≥ 75% de los pares
  vivos (n ≥ 8), p signo < 0.05, y mediana ≤ 0.7 · la del congelado.

    PYTHONPATH=src python experiments/utero/exp_utero_evoluciona2.py
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
from zeta_life.utero.inteligencia import correr_series  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
TICKS = 120000
SEEDS = list(range(20))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
# §20: la ÚNICA diferencia con §17 es e_dif = 0.0 (sin difusión de energía entre vecinas)
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.0, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
ARMS = {"abierto": dict(escritura_total=True),
        "cerrado": dict(),
        "congelado": dict(congelado=True)}
TRANSITORIO = 6000
MIN_HAMBRUNAS = 4
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_evoluciona2"


def fabrica(seed: int, shadow, **flags) -> UteroCreciente:
    return UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True,
                          log_events=True, shadow_deaths=shadow, **flags)


def per_capita(ser: dict, sol: Sol) -> list[float]:
    """Mortalidad per cápita en cada hambruna madura: muertes / vivas medias durante A_k."""
    out = []
    for nombre, ini, fin in sol.estaciones:
        if nombre != "A" or ini < TRANSITORIO or fin > TICKS:
            continue
        vivas = ser["vivas"][ini:fin].mean()
        if vivas <= 0:
            continue
        out.append(float(ser["muertes"][ini:fin].sum() / vivas))
    return out


def spearman(x, y) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def lecturas(ser: dict, sol: Sol) -> dict:
    pc = per_capita(ser, sol)
    n = len(pc)
    h = n // 2
    razon = float(np.mean(pc[h:]) / np.mean(pc[:h])) if (h >= MIN_HAMBRUNAS and np.mean(pc[:h]) > 0) else float("nan")
    return dict(pc=pc, n_hambrunas=n, razon=razon,
                tendencia=spearman(np.arange(n), np.array(pc)) if n >= MIN_HAMBRUNAS else float("nan"),
                pc_media=float(np.mean(pc)) if pc else float("nan"),
                vivas_med=float(np.median(ser["vivas"][TRANSITORIO:])), vivas_fin=float(ser["vivas"][-1]),
                genomas=int(np.nansum(ser["novedad"])))


def job(seed: int) -> tuple:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    out = {}
    for arm, extra in ARMS.items():
        ser = correr_series(seed, {**BASE, **extra}, sol, TICKS, fabrica=fabrica)
        out[arm] = lecturas(ser, sol)
    return seed, out


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("EVOLUCIONA SIN BIEN COMUN? (e_dif=0) -- mortalidad PER CAPITA en hambrunas tardias vs tempranas, contra un brazo CONGELADO")
    out("=" * 80)
    out(f"ecologia {BASE}; brazos {list(ARMS)}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
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
    out(f"  {'brazo':<10} {'vivas med':>9} {'vivas fin':>9} {'hambrunas':>9} {'pc media A':>10} {'razon t/t':>9} {'tendencia':>9} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<10} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'n_hambrunas'):>9.0f} "
            f"{med(arm, 'pc_media'):>10.3f} {med(arm, 'razon'):>9.2f} {med(arm, 'tendencia'):>9.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("PAREADO por semilla contra CONGELADO (razon tardia/temprana de la mortalidad per capita)")
    veredicto = {}
    for arm in ("abierto", "cerrado"):
        pares = [(res[s][arm]["razon"], res[s]["congelado"]["razon"]) for s in SEEDS
                 if not np.isnan(res[s][arm]["razon"]) and not np.isnan(res[s]["congelado"]["razon"])]
        k = sum(1 for a, b in pares if a < b)
        n = len(pares)
        ma = float(np.median([a for a, _ in pares])) if pares else float("nan")
        mc = float(np.median([b for _, b in pares])) if pares else float("nan")
        ok = n >= 8 and k / n >= 0.75 and signo_p(k, n) < 0.05 and ma <= 0.7 * mc
        veredicto[arm] = (ok, k, n, ma, mc)
        out(f"  {arm:<10} razon < congelado en {k}/{n} pares (p signo {signo_p(k, n):.3f}); medianas {ma:.2f} vs {mc:.2f} -> {'EVOLUCIONA' if ok else 'no'}")
        out(f"    por semilla ({arm} | congelado): " + " ".join(f"{a:.2f}|{b:.2f}" for a, b in pares))
    out("")
    out("  mortalidad per capita media en A, pareada contra congelado (menor = el brazo vivo muere menos):")
    for arm in ("abierto", "cerrado"):
        pares = [(res[s][arm]["pc_media"], res[s]["congelado"]["pc_media"]) for s in SEEDS
                 if not np.isnan(res[s][arm]["pc_media"]) and not np.isnan(res[s]["congelado"]["pc_media"])]
        k = sum(1 for a, b in pares if a < b)
        out(f"    {arm:<10} menor que congelado en {k}/{len(pares)} (p signo {signo_p(k, len(pares)):.3f})")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(v[2] < 8 for v in veredicto.values()):
        out("=> SIN DATOS: menos de 8 pares vivos con >= 4 hambrunas por mitad.")
    elif any(v[0] for v in veredicto.values()):
        out("=> EVOLUCIONA en " + ", ".join(a for a, v in veredicto.items() if v[0]) + ": la mortalidad per capita en la hambruna baja con las hambrunas sucesivas mas que en el brazo congelado.")
    else:
        out("=> NO EVOLUCIONA: lo que baja, baja igual en el brazo congelado (ecologia, no herencia). Con 23 variantes viables/1000 ticks, la seleccion no tiene sobre que actuar en esta vara.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
