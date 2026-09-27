"""
§26 — ¿EXISTE UN GRADIENTE DE INGRESO SELECCIONABLE? Control positivo del
gradiente en la ecología cerrada con luz escasa. (docs/PLAN_INTELIGENCIA.md §26;
ledger 2026-09-27)

HIPÓTESIS (escrita antes de correr). La sonda de ceguera mata a todo programa
cuya salida no dependa de la materia; los programas legales tienen materia
efectivamente pseudoaleatoria, y su peso de luz |v − sol| promedia lo mismo
(≈0.25 en el toro) para todos: no hay varianza heredable de aptitud en lo que
el sol mide, y por eso nada se adapta (§17–§25). Si es así, un programa LEGAL
que mantenga su materia lejos del sol debe ganar en cuanto la luz escasee, y
un programa de la misma forma pero sin ventaja de ingreso, no.

PROGRAMAS SEMBRADOS (ambos pasan la sonda y no quedan quietos; sin MUTO):
  ANTISOL  v' = 0.875 + 0.0625·vl  (materia en [0.875, 0.94]: distancia al sol
           0.28–0.40 en las tres estaciones contra ≈0.25 al azar; sensible a la
           materia por el término en vl).
  ESPEJO   v' = vl + 0.5 (mod 1): misma estructura, legal, pero en cadena
           alterna sol+0.5 / sol: ingreso medio ≈ al azar. Control emparejado.
DISEÑO. Ecología CERRADA (n0 = max_n = 64), CONGELADA (sin herencia de
cambios: sólo compiten programas fijos), luz escasa L0 = 1.75 (calibrado:
mortalidad per cápita en la hambruna 0.29, 18 vivas, 6/6 semillas vivas; la
calibración fue ruidosa: 1.25 → 0.13, 1.5 → 0.82, 1.75 → 0.29), sol seed 0
cíclico, 30000 ticks, 20 semillas. Cada mundo: 56 celdas al azar + 4 ANTISOL +
4 ESPEJO en posiciones barajadas por semilla. Medida: fracción de cada
programa entre las vivas a los 10000 y 30000 ticks (parten de 4/64 = 0.0625).
VEREDICTO por semilla: ANTISOL "gana" si su fracción final ≥ 0.25 (4× la
inicial) y ≥ 2× la de ESPEJO.
  GRADIENTE     si ANTISOL gana en ≥ 15/20 semillas → el ingreso es
                seleccionable y la falta de adaptación es de CAMINO (la
                variación no llega a programas así) o de vara.
  SIN GRADIENTE si ANTISOL gana en ≤ 5/20 → la sonda aplana el ingreso o el
                ingreso no manda; hay que cambiar el filtro o la ecología.
  MIXTO         en otro caso.
Se reporta también la fracción de ESPEJO (control de forma) y la de la sopa.

    PYTHONPATH=src python experiments/utero/exp_utero_gradiente.py
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
from zeta_life.utero.nivel2 import ADD, CONST, MUL, SPAWN, K, huella  # noqa: E402
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N = 64
TICKS = 30000
T_MED = 10000
SEEDS = list(range(20))
SOL_SEED = 0
L0 = 1.75
N_SEMBRADAS = 4
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=L0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0,
            congelado=True)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_gradiente"


def prog(*instrs) -> np.ndarray:
    code = np.zeros((K, 4), dtype=np.int64)
    for i, ins in enumerate(instrs):
        code[i, :len(ins)] = ins
    return code


# registros: r0 = vl, r1 = v, r2 = vr, r3 = R3 (salida = r3 mod 1)
ANTISOL = prog((CONST, 9, 0, 3),      # r3 = 0.25
               (MUL, 3, 3, 3),        # r3 = 0.0625
               (MUL, 3, 0, 3),        # r3 = 0.0625 * vl        (sensible a la materia)
               (CONST, 11, 0, 0),     # r0 = 0.75
               (ADD, 3, 0, 3),        # r3 += 0.75
               (CONST, 9, 0, 0),      # r0 = 0.25
               (CONST, 10, 0, 2),     # r2 = 0.5
               (MUL, 0, 2, 0),        # r0 = 0.125
               (ADD, 3, 0, 3),        # r3 = 0.875 + 0.0625 * vl
               (SPAWN, 1, 3, 15))     # pare a la derecha
ESPEJO = prog((CONST, 10, 0, 3),      # r3 = 0.5
              (ADD, 0, 3, 3),         # r3 = vl + 0.5
              (SPAWN, 1, 3, 15))


def correr(seed: int) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N, seed=seed, max_n=N, germinal=True, toroidal=True, sol=sol, **BASE)
    rng = np.random.default_rng(5000 + seed)
    pos = rng.permutation(N)
    for i in pos[:N_SEMBRADAS]:
        u.code[i] = ANTISOL
    for i in pos[N_SEMBRADAS:2 * N_SEMBRADAS]:
        u.code[i] = ESPEJO
    hA, hE = huella(ANTISOL), huella(ESPEJO)
    out = {}
    for t in range(1, TICKS + 1):
        u.step()
        if t in (T_MED, TICKS):
            vivos = [huella(u.code[i]) for i in np.flatnonzero(u.alive)]
            n = len(vivos)
            out[t] = dict(n=n, antisol=vivos.count(hA) / n if n else float("nan"),
                          espejo=vivos.count(hE) / n if n else float("nan"))
    return dict(seed=seed, **{f"{k}_{t}": v for t, d in out.items() for k, v in d.items()})


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("GRADIENTE DE INGRESO -- ANTISOL (materia lejos del sol) vs ESPEJO (misma forma, ingreso al azar), sembrados 4+4 en 56 al azar; cerrado, congelado, luz escasa")
    out("=" * 80)
    out(f"ecologia {BASE}; N={N}; {len(SEEDS)} semillas; {TICKS} ticks; sol seed {SOL_SEED}; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    res = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(correr, SEEDS):
            res[r["seed"]] = r
    out(f"  {'seed':>4} {'vivas 10k':>9} {'antisol 10k':>11} {'espejo 10k':>10} {'vivas 30k':>9} {'antisol 30k':>11} {'espejo 30k':>10} {'gana':>5}")
    gana = 0
    fa, fe = [], []
    for s in SEEDS:
        r = res[s]
        a, e = r[f"antisol_{TICKS}"], r[f"espejo_{TICKS}"]
        g = (not np.isnan(a)) and a >= 0.25 and a >= 2 * max(e if not np.isnan(e) else 0.0, 1e-9)
        gana += g
        fa.append(a)
        fe.append(e)
        out(f"  {s:>4} {r[f'n_{T_MED}']:>9} {r[f'antisol_{T_MED}']:>11.2f} {r[f'espejo_{T_MED}']:>10.2f} "
            f"{r[f'n_{TICKS}']:>9} {a:>11.2f} {e:>10.2f} {'si' if g else 'no':>5}")
    out(f"  ANTISOL gana en {gana}/{len(SEEDS)}; mediana antisol {np.nanmedian(fa):.2f}, espejo {np.nanmedian(fe):.2f} (inicio 0.0625 cada uno)")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if gana >= 15:
        out("=> GRADIENTE: el ingreso de luz es seleccionable; la falta de adaptacion es de CAMINO o de vara.")
    elif gana <= 5:
        out("=> SIN GRADIENTE: un programa legal con mas ingreso no gana; la sonda aplana el ingreso o el ingreso no manda.")
    else:
        out("=> MIXTO.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
