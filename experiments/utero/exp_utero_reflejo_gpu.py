"""
§37 (GPU) — UNA PERILLA DE HISTORIA PROPIA, en el motor por lotes.
(docs/PLAN_INTELIGENCIA.md §37–§38; ledger 2026-09-27)

La corrida de §37 en CPU se detuvo sin resultado (la CPU se comparte con
otras sesiones); ésta es la misma pregunta, con el mismo pre-registro, en el
motor en GPU validado en §38. Ver `exp_utero_reflejo.py` para el motivo.

DISEÑO. Ecología cerrada N = 512, L0 = 14, 120000 ticks, sol seed 0.
Programas CONGELADOS en todos los brazos (se mide la perilla sin carga de
programa). θ, s heredables (ε = 0.05) y g heredable (ε_g = 0.05):
θ_eff = θ + g·tanh((ē − e)/e0), ē media lenta de la energía propia (τ = 200).
Brazos: clima (A→B→C), ciclo2 (A→C→B), permutado, nulo (clima; θ, s, g fijos).
24 semillas (el doble que en CPU: en GPU el lote es casi gratis; declarado
antes de correr) → 96 mundos en un solo lote.
LECTURA PRIMARIA R2_A (regla de v14): mortalidad per cápita en la hambruna,
madura, pareada por semilla entre mundos vivos; clima < permutado en ≥ 75%
de los pares (n ≥ 8), p signo < 0.05, razón mediana ≤ 0.5; ídem ciclo2.
  VESTIGIO              si cumple en clima Y ciclo2 → regulación por el
                        orden; réplica con otro sol antes de creerlo.
  TIPOS DE TRANSICIÓN   si sólo en clima.
  NADA                  en otro caso.
SECUNDARIAS: ḡ_A y fracción con g > 0 por brazo (¿se selecciona un signo
bajo los órdenes regulares y no bajo el permutado?: semillas con ḡ_A > 0 por
brazo, prueba de signo); w̄_A, s̄_A del brazo clima contra el nulo; partos.

    PYTHONPATH=src python experiments/utero/exp_utero_reflejo_gpu.py
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.gpu import UteroGPU  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 512
TICKS = 120000
SEEDS = list(range(24))
SOL_SEED = 0
L0 = 14.0
EPS, EPS_G = 0.05, 0.05
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
ARMS = {"clima": ("ciclico", False), "ciclo2": ("ciclico_inverso", False),
        "permutado": ("permutado", False), "nulo": ("ciclico", True)}
TRANSITORIO = 6000
RESULTS = HERE.parents[1] / "results"
CKPT = HERE.parents[1] / "data" / "ckpt"          # gitignorado; puntos de control reanudables
NAME = "utero_reflejo_gpu"


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def lecturas(ser: dict, sol: Sol, cols: slice) -> dict:
    """Por mundo del brazo: medias sobre las hambrunas maduras."""
    pc, nA, nB, w, s, g, gp = [], [], [], [], [], [], []
    for nombre, ini, fin in sol.estaciones:
        if ini < TRANSITORIO or fin > TICKS:
            continue
        v = np.nanmean(ser["vivas"][ini:fin, cols], axis=0)
        v = np.where(v > 0, v, np.nan)
        if nombre == "A":
            pc.append(ser["muertes"][ini:fin, cols].sum(axis=0) / v)
            nA.append(ser["partos"][ini:fin, cols].sum(axis=0) / v / (fin - ini) * 100)
            for lst, k in ((w, "w"), (s, "s"), (g, "g"), (gp, "gpos")):
                lst.append(np.nanmean(ser[k][ini:fin, cols], axis=0))
        elif nombre == "B":
            nB.append(ser["partos"][ini:fin, cols].sum(axis=0) / v / (fin - ini) * 100)
    f = lambda x: np.nanmean(np.array(x), axis=0)   # noqa: E731
    return dict(pc_A=f(pc), nac_A=f(nA), nac_B=f(nB), w_A=f(w), s_A=f(s), g_A=f(g), gpos_A=f(gp),
                vivas_med=np.nanmedian(ser["vivas"][TRANSITORIO:, cols], axis=0),
                vivas_fin=ser["vivas"][-1, cols])


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    ns = len(SEEDS)
    soles = {a: Sol(seed=SOL_SEED, ticks=TICKS, orden=o, regimenes=REGS) for a, (o, _) in ARMS.items()}
    seeds, sol, fijo = [], [], []
    for a, (_, f) in ARMS.items():
        seeds += SEEDS
        sol += [soles[a].serie] * ns
        fijo += [f] * ns
    out("=" * 80)
    out("REFLEJO (GPU): ganancia heredable sobre la historia de energia propia -- clima vs ciclo2 vs permutado vs nulo; programas congelados")
    out("=" * 80)
    out(f"N={N}; L0={L0}; eps={EPS}; eps_g={EPS_G}; {ns} semillas x {len(ARMS)} brazos = {len(seeds)} mundos; {TICKS} ticks; sol seed {SOL_SEED}; "
        f"dispositivo {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    out("veredicto pre-registrado (docstring)")
    out("")
    g = UteroGPU(seeds, N, np.stack(sol), luz_finita=L0, congelado=True, parametros=EPS, escala=True,
                 reflejo=EPS_G, theta_fijo=fijo)
    t0 = time.time()
    CKPT.mkdir(parents=True, exist_ok=True)
    ser = g.correr(TICKS, checkpoint=str(CKPT / f"{NAME}.pt"), cada=5000)
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    res = {a: lecturas(ser, soles[a], slice(i * ns, (i + 1) * ns)) for i, a in enumerate(ARMS)}
    out("-" * 80)
    out("ESTADO por brazo (medianas)")
    out(f"  {'brazo':<10} {'vivas med':>9} {'vivas fin':>9} {'pc_A':>6} {'nac_B':>6} {'nac_A':>6} {'w_A':>6} {'s_A':>5} {'g_A':>7} {'g>0':>5}")
    for a in ARMS:
        r = res[a]
        m = lambda k: float(np.nanmedian(r[k]))   # noqa: E731
        out(f"  {a:<10} {m('vivas_med'):>9.0f} {m('vivas_fin'):>9.0f} {m('pc_A'):>6.2f} {m('nac_B'):>6.2f} {m('nac_A'):>6.2f} "
            f"{m('w_A'):>6.3f} {m('s_A'):>5.2f} {m('g_A'):>7.3f} {m('gpos_A'):>5.2f}")
    out("")
    out("-" * 80)
    out("R2_A. REGULACION POR ORDEN: mortalidad per capita en A, pareada contra permutado, entre mundos vivos")
    R = {}
    for a in ("clima", "ciclo2"):
        pr = [(x, y) for x, y, vx, vy in zip(res[a]["pc_A"], res["permutado"]["pc_A"], res[a]["vivas_fin"],
                                             res["permutado"]["vivas_fin"])
              if vx > 0 and vy > 0 and not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        R[a] = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.5
        out(f"  {a:<8} < permutado en {k}/{len(pr)} (p signo {signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} -> {'si' if R[a] else 'no'}")
        out(f"    por semilla ({a} | permutado): " + " ".join(f"{x:.2f}|{y:.2f}" for x, y in pr))
    out("")
    out("  SIGNO de la ganancia g por brazo (semillas con g_A > 0; prueba de signo bilateral aproximada):")
    for a in ARMS:
        ga = res[a]["g_A"]
        ga = ga[~np.isnan(ga)]
        kp = int((ga > 0).sum())
        p2 = min(1.0, 2 * min(signo_p(kp, len(ga)), signo_p(len(ga) - kp, len(ga))))
        out(f"    {a:<10} g_A mediana {np.median(ga) if len(ga) else float('nan'):>7.3f}; g_A > 0 en {kp}/{len(ga)} (p {p2:.3f})")
    pw = [(x, y) for x, y in zip(res["clima"]["w_A"], res["nulo"]["w_A"]) if not (np.isnan(x) or np.isnan(y))]
    kw = sum(1 for x, y in pw if x > y)
    out(f"  EVOLUCIONA aqui? clima w_A > nulo en {kw}/{len(pw)} (p signo {signo_p(kw, len(pw)):.3f}); medianas "
        f"{np.median([x for x, _ in pw]):.3f} vs {np.median([y for _, y in pw]):.3f}")
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
