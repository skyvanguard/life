"""
§39 (GPU) — TRASPLANTE RECÍPROCO: ¿las perillas heredables de una población
codifican el ORDEN de las estaciones bajo el que evolucionó?
(docs/PLAN_INTELIGENCIA.md §39; ledger 2026-09-27)

MOTIVO. El cálculo de campo medio (§37b) mostró que la ganancia g sobre la
historia de energía propia es un REFLEJO: paga con cualquier orden, y donde
más paga es bajo el permutado; la lectura regular-contra-permutado (R2_A) no
puede dar vestigio con esa perilla. Pero mostró también que el orden decide
CUÁL g conviene (g = −0.5: cero hambre bajo clima, 15% de la hambruna sin
energía bajo ciclo2). Las mismas estaciones con las mismas duraciones, en
otro orden, premian perillas distintas. El test clásico de adaptación local:
trasplante recíproco.

DISEÑO. Ecología cerrada N = 512, L0 = 14. Programas CONGELADOS (se miden
las perillas); θ, s, g heredables (ε = 0.05, ε_g = 0.05). 24 semillas.
  FASE 1 (evolución, 120000 ticks, sol seed 0): tres orígenes — clima
    (A→B→C), ciclo2 (A→C→B), permutado. 72 mundos en un lote.
  FASE 2 (ensayo, 40000 ticks, sol seed 1: OTRO calendario, otras duraciones;
    lo único que se conserva es el orden): cada población evolucionada se
    copia y se corre bajo clima y bajo ciclo2, con las perillas FIJAS
    (theta_fijo: se mide el desempeño, no se sigue evolucionando). 144 mundos.
LECTURA PRIMARIA (ENMENDADA antes de correr, tras el modelo reducido §39b):
mortalidad per cápita en la hambruna durante el ensayo (hambrunas con inicio
≥ 4000), pareada por semilla, con el criterio LOCAL CONTRA FORÁNEO (Kawecki y
Ebert 2004): dentro de cada destino, la población que evolucionó allí contra
la que evolucionó bajo el otro orden regular.
  VENTAJA LOCAL (destino clima):  clima→clima   < ciclo2→clima.
  VENTAJA LOCAL (destino ciclo2): ciclo2→ciclo2 < clima→ciclo2.
  Cada una cumple si se da en ≥ 75% de los pares vivos (n ≥ 8), p signo <
  0.05, razón mediana ≤ 0.8.
  VESTIGIO    si hay ventaja local en AMBOS destinos → las perillas
              heredables codifican el orden de las estaciones. Réplica con
              otro sol antes de creerlo.
  ASIMÉTRICO  si sólo en un destino: adaptación a un orden, no demostrada
              como adaptación AL orden; se reporta sin llamarla vestigio.
  NADA        si en ninguno.
Motivo de la enmienda: el criterio original (en casa contra fuera) confunde
adaptación con calidad del entorno; el modelo reducido mostró que el
calendario clima es más benigno que ciclo2 para cualquier origen (control
permutado 22/24). Se sigue informando como secundaria.
CONTROL: origen permutado ensayado bajo clima y ciclo2 (sin casa): fija
cuánto de la diferencia entre calendarios es del entorno. SECUNDARIAS: la
distribución de g y θ por origen al final de la fase 1 (¿difieren clima y
ciclo2 como predice el campo medio?), w̄_A, s̄.

    PYTHONPATH=src python experiments/utero/exp_utero_trasplante_gpu.py
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
T_EVOL, T_ENSAYO = 120000, 40000
SEEDS = list(range(24))
SOL_EVOL, SOL_ENSAYO = 0, 1
L0 = 14.0
EPS, EPS_G = 0.05, 0.05
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
ORIGENES = {"clima": "ciclico", "ciclo2": "ciclico_inverso", "permutado": "permutado"}
DESTINOS = {"clima": "ciclico", "ciclo2": "ciclico_inverso"}
TRANS_ENSAYO = 4000
RESULTS = HERE.parents[1] / "results"
CKPT = HERE.parents[1] / "data" / "ckpt"
NAME = "utero_trasplante_gpu"
KW = dict(luz_finita=L0, congelado=True, parametros=EPS, escala=True, reflejo=EPS_G)


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def pc_hambruna(ser: dict, sol: Sol, ticks: int, cols: slice, desde: int) -> np.ndarray:
    pc = []
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A" and ini >= desde and fin <= ticks:
            v = np.nanmean(ser["vivas"][ini:fin, cols], axis=0)
            pc.append(ser["muertes"][ini:fin, cols].sum(axis=0) / np.where(v > 0, v, np.nan))
    return np.nanmean(np.array(pc), axis=0)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    ns = len(SEEDS)
    CKPT.mkdir(parents=True, exist_ok=True)
    out("=" * 80)
    out("TRASPLANTE RECIPROCO (GPU): las perillas heredables codifican el ORDEN bajo el que evolucionaron?")
    out("=" * 80)
    out(f"N={N}; L0={L0}; eps={EPS}; eps_g={EPS_G}; {ns} semillas; evolucion {T_EVOL} ticks (sol {SOL_EVOL}), ensayo {T_ENSAYO} ticks (sol {SOL_ENSAYO}); "
        f"dispositivo {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    out("veredicto pre-registrado (docstring)")
    out("")
    # ---------------------------------------------------------------- fase 1: evolución
    sol1 = {o: Sol(seed=SOL_EVOL, ticks=T_EVOL, orden=ord_, regimenes=REGS) for o, ord_ in ORIGENES.items()}
    seeds, sol = [], []
    for o in ORIGENES:
        seeds += SEEDS
        sol += [sol1[o].serie] * ns
    g = UteroGPU(seeds, N, np.stack(sol), **KW)
    t0 = time.time()
    g.correr(T_EVOL, checkpoint=str(CKPT / f"{NAME}_fase1.pt"), cada=5000)
    out(f"fase 1 (evolucion): {(time.time() - t0) / 60:.1f} min")
    est = g.estado()
    vivas1 = g.alive.sum(dim=1).cpu().numpy()
    out(f"  {'origen':<10} {'vivas':>6} {'g media':>8} {'g>0':>5} {'|g| media':>9} {'s media':>8} {'R_theta':>8}")
    for i, o in enumerate(ORIGENES):
        sl = slice(i * ns, (i + 1) * ns)
        al = g.alive[sl]
        den = al.sum().clamp_min(1)
        gm = float((g.g[sl] * al).sum() / den)
        gp = float(((g.g[sl] > 0) & al).sum() / den)
        ga = float((g.g[sl].abs() * al).sum() / den)
        sm = float((g.esc[sl] * al).sum() / den)
        ang = 2 * math.pi * g.theta[sl]
        R = float(torch.sqrt(((torch.cos(ang) * al).sum() / den) ** 2 + ((torch.sin(ang) * al).sum() / den) ** 2))
        out(f"  {o:<10} {np.median(vivas1[sl]):>6.0f} {gm:>8.3f} {gp:>5.2f} {ga:>9.3f} {sm:>8.2f} {R:>8.2f}")
    out("")
    # ---------------------------------------------------------------- fase 2: ensayo con perillas fijas
    sol2 = {d: Sol(seed=SOL_ENSAYO, ticks=T_ENSAYO, orden=ord_, regimenes=REGS) for d, ord_ in DESTINOS.items()}
    nb = len(ORIGENES) * ns
    seeds2, sol_2 = [], []
    for d in DESTINOS:
        seeds2 += seeds
        sol_2 += [sol2[d].serie] * nb
    h = UteroGPU(seeds2, N, np.stack(sol_2), theta_fijo=True, **KW)
    h.restaurar({k: (torch.cat([v] * len(DESTINOS), dim=0) if torch.is_tensor(v) and v.ndim >= 1 and k != "gen" else v)
                 for k, v in est.items() if k != "gen"} | {"gen": h.gen.get_state().cpu(), "tick": 0})
    t0 = time.time()
    ser = h.correr(T_ENSAYO, checkpoint=str(CKPT / f"{NAME}_fase2.pt"), cada=5000)
    out(f"fase 2 (ensayo): {(time.time() - t0) / 60:.1f} min")
    pc = {}
    for j, d in enumerate(DESTINOS):
        for i, o in enumerate(ORIGENES):
            sl = slice(j * nb + i * ns, j * nb + (i + 1) * ns)
            pc[(o, d)] = pc_hambruna(ser, sol2[d], T_ENSAYO, sl, TRANS_ENSAYO)
    out("  mortalidad per capita en la hambruna (mediana entre semillas), origen -> destino:")
    out(f"  {'origen':<10} " + " ".join(f"{'-> ' + d:>12}" for d in DESTINOS))
    for o in ORIGENES:
        out(f"  {o:<10} " + " ".join(f"{np.nanmedian(pc[(o, d)]):>12.3f}" for d in DESTINOS))
    out("")
    out("-" * 80)
    out("VENTAJA DE CASA (pareado por semilla)")
    casa = {}
    for o, propio, ajeno in (("clima", "clima", "ciclo2"), ("ciclo2", "ciclo2", "clima")):
        pr = [(x, y) for x, y in zip(pc[(o, propio)], pc[(o, ajeno)]) if not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        casa[o] = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.8
        out(f"  origen {o:<7}: en casa < fuera en {k}/{len(pr)} (p signo {signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} -> {'si' if casa[o] else 'no'}")
    prp = [(x, y) for x, y in zip(pc[("permutado", "clima")], pc[("permutado", "ciclo2")]) if not (np.isnan(x) or np.isnan(y))]
    kp = sum(1 for x, y in prp if x < y)
    out(f"  control (origen permutado, sin casa): clima < ciclo2 en {kp}/{len(prp)} (el efecto del ENTORNO solo)")
    out("")
    out("-" * 80)
    out("LOCAL CONTRA FORANEO (dentro de cada destino, pareado por semilla; criterio de Kawecki y Ebert 2004)")
    local = {}
    for d, foraneo in (("clima", "ciclo2"), ("ciclo2", "clima")):
        pr = [(x, y) for x, y in zip(pc[(d, d)], pc[(foraneo, d)]) if not (np.isnan(x) or np.isnan(y))]
        k = sum(1 for x, y in pr if x < y)
        raz = float(np.median([x / y if y > 0 else np.nan for x, y in pr])) if pr else float("nan")
        local[d] = len(pr) >= 8 and k / len(pr) >= 0.75 and signo_p(k, len(pr)) < 0.05 and raz <= 0.8
        prp2 = [(x, y) for x, y in zip(pc[(d, d)], pc[("permutado", d)]) if not (np.isnan(x) or np.isnan(y))]
        kp2 = sum(1 for x, y in prp2 if x < y)
        out(f"  destino {d:<7}: local < foraneo ({foraneo}) en {k}/{len(pr)} (p signo {signo_p(k, len(pr)):.3f}); razon mediana {raz:.2f} "
            f"-> {'si' if local[d] else 'no'};  local < origen permutado en {kp2}/{len(prp2)}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr; criterio primario: local contra foraneo en AMBOS destinos)")
    if local["clima"] and local["ciclo2"]:
        out("=> VESTIGIO: a cada poblacion le va mejor bajo el orden en el que evoluciono, con otro calendario y las perillas fijas. "
            "Sus perillas heredables codifican el orden de las estaciones. ANTES DE CREERLO: replicar con otro sol.")
    elif local["clima"] != local["ciclo2"]:
        out("=> ASIMETRICO: ventaja local en un solo destino; adaptacion a un orden, no demostrada como adaptacion AL orden. No es vestigio.")
    else:
        out("=> NADA: ninguna poblacion tiene ventaja local.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
