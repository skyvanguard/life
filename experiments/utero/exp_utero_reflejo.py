"""
§37 — UNA PERILLA DE HISTORIA PROPIA: ¿la regularidad del orden selecciona
una ganancia heredable sobre la tendencia de la energía? (docs/PLAN_INTELIGENCIA.md
§37; ledger 2026-09-27)

ANTECEDENTE. Lo que evoluciona en el útero son perillas continuas heredables
sobre la expresión de la física (§34–§35, replicado). §36: con perillas
escribibles por el programa no hay regulación por el orden, porque moldear
un comportamiento exige evolución de programa y ese paisaje es plano. Aquí
la perilla es de HISTORIA PROPIA: θ_eff = θ + g·tanh((ē − e)/e0), con ē la
media lenta (τ = 200) de la energía de la celda y g una ganancia heredable
continua (nace en 0; ±ε_g al nacer desde la materia de la madre). Cuando la
energía cae respecto de su historia, la expresión se desplaza; el signo y la
magnitud son heredables. Bajo el orden regular la estación templada (C, luz
0.40) precede siempre a la hambruna (A, 0.08): una caída de energía anuncia
el hambre y un desplazamiento anti-sol a tiempo paga; bajo el permutado la
caída no anuncia nada fijo.

DISEÑO. Ecología cerrada N = 512, L0 = 14, 120000 ticks, 12 semillas, sol
seed 0. Programas CONGELADOS en todos los brazos (sin carga de programa: se
mide la perilla). θ, s heredables (ε = 0.05), g heredable (ε_g = 0.05).
Brazos: clima (A→B→C), ciclo2 (A→C→B), permutado, nulo (clima; θ, s, g fijos).
LECTURA PRIMARIA R2_A (regla de v14): mortalidad per cápita en la hambruna,
madura, pareada por semilla entre mundos vivos; clima < permutado en ≥ 75%
de los pares (n ≥ 8), p signo < 0.05, razón mediana ≤ 0.5; ídem ciclo2.
  VESTIGIO              si cumple en clima Y ciclo2 → regulación por el
                        orden; réplica con otro sol antes de creerlo.
  TIPOS DE TRANSICIÓN   si sólo en clima.
  NADA                  en otro caso.
SECUNDARIAS: ḡ_A (ganancia media de las vivas en A) y fracción con g > 0 por
brazo —¿se selecciona un signo bajo los órdenes regulares y no bajo el
permutado?—; w̄_A, s̄_A contra el nulo; partos A y B.

    PYTHONPATH=src python experiments/utero/exp_utero_reflejo.py
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
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 512
TICKS = 120000
SEEDS = list(range(12))
SOL_SEED = 0
L0 = 14.0
EPS = 0.05
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=L0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0,
            parametros=EPS, escala=True, reflejo=0.05, congelado=True)   # programas congelados: se mide la perilla
VIVO = dict()
NULO = dict(theta_fijo=True)
ARMS = {"clima": ("ciclico", VIVO), "ciclo2": ("ciclico_inverso", VIVO), "permutado": ("permutado", VIVO),
        "nulo": ("ciclico", NULO)}
TRANSITORIO = 6000
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_reflejo"


def correr(seed: int, orden: str, flags: dict) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, orden=orden, regimenes=REGS)
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE, **flags)
    vivas = np.zeros(TICKS)
    muertes = np.zeros(TICKS)
    partos = np.zeros(TICKS)
    w = np.full(TICKS, np.nan)
    sm = np.full(TICKS, np.nan)
    gm = np.full(TICKS, np.nan)
    gp = np.full(TICKS, np.nan)
    for t in range(TICKS):
        r = u.step()
        alive = u.alive
        n = int(alive.sum())
        vivas[t] = n
        muertes[t] = r["deaths"]
        partos[t] = r.get("colonized", 0) + r.get("invaded", 0) + r.get("grown", 0)
        if n:
            d = np.abs(u.v[alive] - float(sol(t)))
            d = np.minimum(d, 1.0 - d)
            w[t] = float(d.mean() + 0.05)
            sm[t] = float(u.esc[alive].mean())
            gm[t] = float(u.g[alive].mean())
            gp[t] = float((u.g[alive] > 0).mean())
    pcA, nA, nB, wA, sA, gA, gpA = [], [], [], [], [], [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < TRANSITORIO or fin > TICKS:
            continue
        v = vivas[ini:fin].mean()
        if v <= 0:
            continue
        if nombre == "A":
            pcA.append(float(muertes[ini:fin].sum() / v))
            nA.append(float(partos[ini:fin].sum() / v / (fin - ini) * 100))
            wA.append(float(np.nanmean(w[ini:fin])))
            sA.append(float(np.nanmean(sm[ini:fin])))
            gA.append(float(np.nanmean(gm[ini:fin])))
            gpA.append(float(np.nanmean(gp[ini:fin])))
        elif nombre == "B":
            nB.append(float(partos[ini:fin].sum() / v / (fin - ini) * 100))
    return dict(pc_A=float(np.mean(pcA)) if pcA else float("nan"), nac_A=float(np.mean(nA)) if nA else float("nan"),
                nac_B=float(np.mean(nB)) if nB else float("nan"), w_A=float(np.mean(wA)) if wA else float("nan"),
                s_A=float(np.mean(sA)) if sA else float("nan"), vivas_med=float(np.median(vivas[TRANSITORIO:])),
                vivas_fin=float(vivas[-1]), g_A=float(np.mean(gA)) if gA else float("nan"),
                gpos_A=float(np.mean(gpA)) if gpA else float("nan"), genomas=len(u.seen))


def job(seed: int) -> tuple:
    return seed, {arm: correr(seed, orden, flags) for arm, (orden, flags) in ARMS.items()}


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("REFLEJO: ganancia heredable sobre la historia de energia propia -- clima vs ciclo2 vs permutado vs nulo; programas congelados")
    out("=" * 80)
    out(f"ecologia {BASE}; vivo {VIVO}; nulo {NULO}; N={N}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res: dict = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, (seed, r) in enumerate(ex.map(job, SEEDS), 1):
            res[seed] = r
            print(f"  ... {i}/{len(SEEDS)} semillas", flush=True)

    def med(arm, k):
        v = [res[s][arm][k] for s in SEEDS]
        v = [x for x in v if not np.isnan(x)]
        return float(np.median(v)) if v else float("nan")

    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<10} {'vivas med':>9} {'vivas fin':>9} {'pc_A':>6} {'nac_B':>6} {'nac_A':>6} {'w_A':>6} {'s_A':>5} {'g_A':>6} {'g>0':>5} {'genomas':>8}")
    for arm in ARMS:
        out(f"  {arm:<10} {med(arm, 'vivas_med'):>9.0f} {med(arm, 'vivas_fin'):>9.0f} {med(arm, 'pc_A'):>6.2f} {med(arm, 'nac_B'):>6.2f} "
            f"{med(arm, 'nac_A'):>6.2f} {med(arm, 'w_A'):>6.3f} {med(arm, 's_A'):>5.2f} {med(arm, 'g_A'):>6.3f} {med(arm, 'gpos_A'):>5.2f} {med(arm, 'genomas'):>8.0f}")
    out("")
    out("-" * 80)
    out("R2_A. REGULACION POR ORDEN: mortalidad per capita en A, pareada contra permutado, entre mundos vivos")

    def r2(arm):
        pr = [(res[s][arm]["pc_A"], res[s]["permutado"]["pc_A"]) for s in SEEDS
              if res[s][arm]["vivas_fin"] > 0 and res[s]["permutado"]["vivas_fin"] > 0
              and not np.isnan(res[s][arm]["pc_A"]) and not np.isnan(res[s]["permutado"]["pc_A"])]
        k = sum(1 for a, b in pr if a < b)
        raz = float(np.median([a / b if b > 0 else np.nan for a, b in pr])) if pr else float("nan")
        ok = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.5
        return k, len(pr), raz, ok, pr

    R = {}
    for arm in ("clima", "ciclo2"):
        k, n, raz, ok, pr = r2(arm)
        R[arm] = ok
        out(f"  {arm:<8} < permutado en {k}/{n} (p signo {signo_p(k, n):.3f}); razon mediana {raz:.2f} -> {'si' if ok else 'no'}")
        out(f"    por semilla ({arm} | permutado): " + " ".join(f"{a:.2f}|{b:.2f}" for a, b in pr))
    out("")
    out("  EVOLUCIONA aqui? w_A del brazo vivo contra el nulo (clima):")
    pw = [(res[s]["clima"]["w_A"], res[s]["nulo"]["w_A"]) for s in SEEDS
          if not np.isnan(res[s]["clima"]["w_A"]) and not np.isnan(res[s]["nulo"]["w_A"])]
    kw = sum(1 for a, b in pw if a > b)
    out(f"    clima w_A > nulo en {kw}/{len(pw)} (p signo {signo_p(kw, len(pw)):.3f}); medianas {np.median([a for a, _ in pw]) if pw else float('nan'):.3f} vs {np.median([b for _, b in pw]) if pw else float('nan'):.3f}")
    out("  SIGNO de la ganancia g por brazo (mediana entre semillas de g_A y de la fraccion con g>0):")
    for arm in ARMS:
        gs = [res[s]["clima" if arm == "nulo" else arm]["g_A"] for s in SEEDS]
        out(f"    {arm:<10} g_A {med(arm, 'g_A'):>7.3f}  g>0 {med(arm, 'gpos_A'):.2f}  semillas con g_A>0: {sum(1 for x in [res[s][arm]['g_A'] for s in SEEDS] if x > 0)}/{len(SEEDS)}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if R["clima"] and R["ciclo2"]:
        out("=> VESTIGIO: bajo ambos ordenes regulares la hambruna mata menos que bajo el permutado. ANTES DE CREERLO: replicar con otro sol.")
    elif R["clima"]:
        out("=> TIPOS DE TRANSICION: solo el orden A<-C cumple; no es regularidad.")
    else:
        out("=> NADA: la hambruna no mata menos bajo el orden regular.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
