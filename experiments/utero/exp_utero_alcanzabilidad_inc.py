"""
§32 — ALCANZABILIDAD CON ESCRITURAS INCREMENTALES: ¿un operador de variación
de pasos pequeños (±1 en un solo campo) da una escalera de mejoras del rasgo
que las escrituras enteras no dan? (docs/PLAN_INTELIGENCIA.md §32; ledger
2026-09-27)

Mismo arnés y mismos padres que §28 (programas legales del tejido abierto,
fenotipo proxy w̄ = distancia toroidal media de la salida al sol de la
hambruna + 0.05, legalidad por la sonda). Modos: total (fila entera al azar,
como el germinal de v16), incremental (±1 en UN campo de una fila al azar:
opcode mod 10, operando mod 16) e incremental de dos pasos.
LECTURA (escrita antes de correr): ESCALERA si P(legal y Δw̄ ≥ +0.05) con
escrituras incrementales es ≥ 1% y ≥ 3× la de las totales → hay base para un
operador incremental en el sustrato y una corrida de escalada (§33). SIN
ESCALERA en otro caso: el mapa programa→materia es plano también para pasos
de un campo, y la evolvabilidad exige otro mapa, no otro operador.

    PYTHONPATH=src python experiments/utero/exp_utero_alcanzabilidad_inc.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.creciente import UteroCreciente  # noqa: E402
from zeta_life.utero.nivel2 import (  # noqa: E402
    ARG_RANGE,
    N_OPS,
    PROBE_EPS,
    K,
    _output_only,
    huella,
)
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

SEEDS = list(range(10))
T_FUENTE = 6000
MAX_PADRES_POR_MUNDO = 5
N_INPUTS = 200
N_TOTAL, N_OPCODE, N_DOS = 400, 400, 100
SOL_HAMBRUNA = 0.08
H = 0.6180339887498949
BANDA = 0.45
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=1.75,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0,
            escritura_total=True)
WORKERS = max(1, min(12, (os.cpu_count() or 4) // 2))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_alcanzabilidad_inc"
INPUTS = np.random.default_rng(12345).uniform(0.0, 1.0, size=(N_INPUTS, 3))


def _antisol() -> np.ndarray:
    spec = importlib.util.spec_from_file_location("g", HERE / "exp_utero_gradiente.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ANTISOL


def legal(code: np.ndarray) -> bool:
    ctx = (code, code, code)
    o = _output_only(code, 0.3, 0.7, 0.2, ctx, wrap=True, extra=[0.0, 0.0])
    p1 = _output_only(code, 0.0, 0.0, 0.0, ctx, wrap=True, extra=[0.0, 0.0])
    p2 = _output_only(code, H, H, H, ctx, wrap=True, extra=[0.0, 0.0])
    return not (abs(o - p1) < PROBE_EPS and abs(o - p2) < PROBE_EPS and abs(p1 - p2) < PROBE_EPS)


def w_bar(code: np.ndarray) -> float:
    ctx = (code, code, code)
    d = []
    for vl, v, vr in INPUTS:
        o = _output_only(code, float(vl), float(v), float(vr), ctx, wrap=True, extra=[0.0, 0.0])
        x = abs(o - SOL_HAMBRUNA)
        d.append(min(x, 1.0 - x))
    return float(np.mean(d) + 0.05)


def padres(seed: int) -> list:
    sol = Sol(seed=0, ticks=T_FUENTE, regimenes=REGS)
    u = UteroCreciente(n0=64, seed=seed, max_n=64, germinal=True, toroidal=True, sol=sol, **BASE)
    for _ in range(T_FUENTE):
        u.step()
    vistos, out = set(), []
    for i in np.flatnonzero(u.alive):
        h = huella(u.code[i])
        if h not in vistos:
            vistos.add(h)
            out.append(u.code[i].copy())
        if len(out) >= MAX_PADRES_POR_MUNDO:
            break
    return out


def vecinos(padre: np.ndarray, rng: np.random.Generator) -> dict:
    w0 = w_bar(padre)
    res = {"w0": w0, "legal0": legal(padre)}
    for modo, n in (("total", N_TOTAL), ("incremental", N_TOTAL), ("inc_dos", N_DOS)):
        ws = []
        for _ in range(n):
            c = padre.copy()
            pasos = 2 if modo == "inc_dos" else 1
            for _ in range(pasos):
                k = int(rng.integers(0, K))
                if modo == "total":
                    c[k] = [int(rng.integers(0, N_OPS))] + [int(x) for x in rng.integers(0, ARG_RANGE, size=3)]
                else:                       # incremental: +-1 en UN campo (op mod 10, operando mod 16)
                    f = int(rng.integers(0, 4))
                    d = int(rng.choice([-1, 1]))
                    c[k, f] = (int(c[k, f]) + d) % (N_OPS if f == 0 else ARG_RANGE)
            if legal(c):
                ws.append(w_bar(c))
            else:
                ws.append(np.nan)
        res[modo] = np.array(ws)
    return res


def job(seed: int) -> tuple:
    rng = np.random.default_rng(777 + seed)
    return seed, [vecinos(p, rng) for p in padres(seed)]


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("ALCANZABILIDAD -- vecindario a una y dos escrituras de programas legales: cuanto cambia la materia respecto del sol de la hambruna?")
    out("=" * 80)
    A = _antisol()
    out(f"sanidad: ANTISOL w_bar = {w_bar(A):.3f} (esperado ~0.55), legal = {legal(A)}")
    out(f"{len(SEEDS)} mundos fuente (abierto p=1, cerrado, L0=1.75, {T_FUENTE} ticks), hasta {MAX_PADRES_POR_MUNDO} padres por mundo; "
        f"{N_TOTAL} totales + {N_OPCODE} opcode + {N_DOS} dos-pasos por padre; {N_INPUTS} entradas; workers={WORKERS}")
    out("veredicto pre-registrado (docstring)")
    out("")
    todos = []
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for seed, lst in ex.map(job, SEEDS):
            todos.extend(lst)
    w0s = np.array([r["w0"] for r in todos])
    out(f"  padres: {len(todos)}; w_bar de los padres: mediana {np.median(w0s):.3f}, min {w0s.min():.3f}, max {w0s.max():.3f}; legales {sum(r['legal0'] for r in todos)}/{len(todos)}")
    out("")
    out(f"  {'modo':<8} {'variantes':>9} {'legales':>8} {'dw med':>7} {'dw p90':>7} {'dw max':>7} {'P(dw>=.1)':>9} {'P(dw>=.2)':>9} {'P(w>=.45)':>9}")
    P = {}
    for modo in ("total", "incremental", "inc_dos"):
        dws, ws, n_tot, n_leg = [], [], 0, 0
        for r in todos:
            arr = r[modo]
            n_tot += len(arr)
            ok = ~np.isnan(arr)
            n_leg += int(ok.sum())
            ws.extend(arr[ok].tolist())
            dws.extend((arr[ok] - r["w0"]).tolist())
        dws, ws = np.array(dws), np.array(ws)
        p1 = float(np.sum(dws >= 0.1) / max(n_tot, 1))
        p2 = float(np.sum(dws >= 0.2) / max(n_tot, 1))
        pb = float(np.sum(ws >= BANDA) / max(n_tot, 1))
        P[modo] = p2
        out(f"  {modo:<8} {n_tot:>9} {n_leg / max(n_tot, 1):>8.2f} {np.median(dws) if len(dws) else float('nan'):>7.3f} "
            f"{np.percentile(dws, 90) if len(dws) else float('nan'):>7.3f} {dws.max() if len(dws) else float('nan'):>7.3f} {p1:>9.4f} {p2:>9.4f} {pb:>9.4f}")
    out("")
    out("=" * 80)
    out("LECTURA §32 (escrita antes de correr): ESCALERA si P(legal y dw>=+0.05) incremental >= 3x total y >= 1%")
    p05 = {}
    for modo in ("total", "incremental"):
        dws, n_tot = [], 0
        for r in todos:
            arr = r[modo]
            n_tot += len(arr)
            ok = ~np.isnan(arr)
            dws.extend((arr[ok] - r["w0"]).tolist())
        p05[modo] = float(np.sum(np.array(dws) >= 0.05) / max(n_tot, 1))
    out(f"  P(legal y dw>=+0.05): total {p05['total']:.4f}, incremental {p05['incremental']:.4f}")
    if p05["incremental"] >= 0.01 and p05["incremental"] >= 3 * max(p05["total"], 1e-9):
        out("=> ESCALERA: las escrituras incrementales dan pasos pequenos positivos con frecuencia; implementar el operador y correr la escalada (§33).")
    else:
        out("=> SIN ESCALERA: el incremento de un campo tampoco produce pasos pequenos positivos con frecuencia; el paisaje es plano para este mapa programa->materia.")
    out("")
    out("VEREDICTO §28 (regla original; escrituras totales de un paso)")
    if P["total"] >= 0.01:
        out(f"=> SALTOS: P(legal y dw>=+0.2) = {P['total']:.4f} >= 1%: un salto grande nace cada pocos miles de ticks; §27 debio verlo -> viabilidad en contexto.")
    elif P["total"] < 0.001:
        out(f"=> SIN SALTOS: P(legal y dw>=+0.2) = {P['total']:.4f} < 0.1%: el rasgo solo se alcanza por pasos pequenos, neutros con N~14 -> poblacion efectiva.")
    else:
        out(f"=> INTERMEDIO: P(legal y dw>=+0.2) = {P['total']:.4f}.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
