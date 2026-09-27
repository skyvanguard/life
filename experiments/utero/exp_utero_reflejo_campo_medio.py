"""
§37b — CAMPO MEDIO: ¿puede el diseño de §37 distinguir el orden regular del
permutado? (docs/PLAN_INTELIGENCIA.md §37; ledger 2026-09-27)

Cálculo, no simulación del útero (numpy, segundos, sin GPU). Antes de gastar
cómputo en §37 se pregunta qué predice el propio diseño. Un linaje raro con
ganancia g (θ_eff = θ + g·tanh((ē − e)/e0)) entre N residentes con g = 0 y la
misma θ y escala s. La materia visible es θ_eff + s·y con y uniforme (la
salida de un programa legal es pseudoaleatoria, §28); el peso de luz es la
distancia toroidal media al sol + 0.05; el ingreso del linaje es
L0·sol·w_m/(N·w_r); su energía sigue e ← e − e_mant + ingreso, con ē su media
lenta (τ = 200). Manos del modelo: un solo linaje, sin partos; N fijado en el
EQUILIBRIO de energía del residente (ingreso medio = mantenimiento), para que
la energía suba en la abundancia y caiga en la hambruna; la energía no baja de
0 y el tiempo pasado en 0 es el análogo de morir de hambre; θ de los
residentes = la que maximiza su peso de luz en la hambruna.
(Primera versión, descartada: N = 150 dejaba al linaje siempre con energía
sobrante; la tendencia nunca cambiaba de signo y g actuaba como un corrimiento
fijo. Modelo degenerado, registrado.)

LECTURAS: para cada calendario (clima A→B→C, ciclo2 A→C→B, permutado), el
fracción de los ticks de HAMBRUNA que el linaje pasa sin energía (hambre), en
función de g, y su ingreso total relativo al residente; la g que minimiza el
hambre y su ventaja sobre g = 0. PREDICCIÓN que se deriva: si la ventaja de la
mejor g es parecida en los tres calendarios, la ganancia es un REFLEJO sobre
el estado presente (detecta abundancia/hambre por la tendencia de su energía)
y paga igual con o sin regularidad: §37 no puede dar VESTIGIO por R2_A y hay
que rediseñar la perilla antes de correrlo. Si la ventaja es claramente mayor
bajo los órdenes regulares (≥ 1.5×), el diseño sí discrimina.

    PYTHONPATH=src python experiments/utero/exp_utero_reflejo_campo_medio.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

TICKS = 120000
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
L0, E_MANT, E0, TAU, S_ESC = 14.0, 0.01, 2.0, 200.0, 0.7
Y = (np.arange(64) + 0.5) / 64                       # salida pseudoaleatoria del programa
GS = np.round(np.arange(-2.0, 2.01, 0.25), 2)
TRANSITORIO = 6000
RESULTS = HERE.parents[1] / "results"
NAME = "utero_reflejo_campo_medio"


def peso(theta_eff, sol):
    d = np.abs((theta_eff[..., None] + S_ESC * Y) % 1.0 - sol[..., None])
    return np.minimum(d, 1.0 - d).mean(axis=-1) + 0.05


def correr(sol: Sol, theta: float) -> dict:
    s = sol.serie
    enA = np.zeros(TICKS, dtype=bool)
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A" and ini >= TRANSITORIO:
            enA[ini:min(fin, TICKS)] = True
    w_r = peso(np.full(TICKS, theta), s)                # residente: g = 0
    n_eq = L0 * float(s[TRANSITORIO:].mean()) / E_MANT  # equilibrio de energia del residente
    g = GS.copy()
    hambre = np.zeros(len(g))
    n_A = 0
    e = np.full(len(g), E0)
    el = np.full(len(g), E0)
    ing_A = np.zeros(len(g))
    ing_T = np.zeros(len(g))
    for t in range(TICKS):
        th = (theta + g * np.tanh((el - e) / E0)) % 1.0
        w_m = peso(th, np.full(len(g), s[t]))
        ing = L0 * s[t] * w_m / (n_eq * w_r[t])
        e = np.maximum(e - E_MANT + ing, 0.0)
        el += (e - el) / TAU
        if t >= TRANSITORIO:
            ing_T += ing
            if enA[t]:
                ing_A += ing
                hambre += (e <= 0.0)
                n_A += 1
    i0 = int(np.flatnonzero(GS == 0.0)[0])
    return dict(rel_A=ing_A / ing_A[i0], rel_T=ing_T / ing_T[i0], hambre=hambre / max(n_A, 1), n_eq=n_eq)


def main() -> None:
    lines: list[str] = []

    def out(x: str = "") -> None:
        print(x, flush=True)
        lines.append(x)

    out("=" * 80)
    out("CAMPO MEDIO de §37 -- ingreso de un linaje con ganancia g relativo al residente (g = 0), por calendario")
    out("=" * 80)
    soles = {"clima": Sol(seed=0, ticks=TICKS, regimenes=REGS),
             "ciclo2": Sol(seed=0, ticks=TICKS, orden="ciclico_inverso", regimenes=REGS),
             "permutado": Sol(seed=0, ticks=TICKS, orden="permutado", regimenes=REGS)}
    # theta del residente: la que maximiza el peso medio en la hambruna (lo que §34 selecciona)
    cand = np.arange(0.0, 1.0, 0.02)
    sA = soles["clima"].serie[[t for n_, i, f in soles["clima"].estaciones if n_ == "A" for t in range(i, min(f, TICKS))]]
    theta = float(cand[np.argmax([peso(np.full(len(sA), c), sA).mean() for c in cand])])
    out(f"modelo: L0={L0}, N = equilibrio de energia, e_mant={E_MANT}, tau={TAU}, s={S_ESC}; theta residente = {theta:.2f} (maximo de peso en la hambruna)")
    out("")
    res = {k: correr(v, theta) for k, v in soles.items()}
    out("  fraccion de la hambruna sin energia (menor = mejor), e ingreso total relativo, por g:")
    out(f"  {'g':>6} " + " ".join(f"{k + ' hambre':>16} {k + ' ing':>14}" for k in soles))
    for j, g in enumerate(GS):
        out(f"  {g:>6.2f} " + " ".join(f"{res[k]['hambre'][j]:>16.3f} {res[k]['rel_T'][j]:>14.3f}" for k in soles))
    out("")
    i0 = int(np.flatnonzero(GS == 0.0)[0])
    vent = {}
    for k in soles:
        h = res[k]["hambre"]
        j = int(np.argmin(h))
        vent[k] = float(h[i0] - h[j])
        out(f"  {k:<10} N_eq {res[k]['n_eq']:.0f}; hambre con g=0: {h[i0]:.3f}; mejor g {GS[j]:+.2f} con hambre {h[j]:.3f} "
            f"(reduccion {vent[k]:.3f}); ingreso total de esa g {res[k]['rel_T'][j]:.3f}")
    out("")
    out("=" * 80)
    out("LECTURA (regla escrita antes de calcular; ventaja = reduccion del hambre en la hambruna)")
    reg = min(vent["clima"], vent["ciclo2"])
    if max(vent.values()) <= 0.005:
        out("=> SIN VENTAJA: ninguna g reduce el hambre en ningun calendario; la perilla no tiene gradiente.")
    elif vent["permutado"] > 0 and reg >= 1.5 * vent["permutado"] or (vent["permutado"] <= 0.005 < reg):
        out(f"=> DISCRIMINA: la reduccion del hambre bajo los ordenes regulares ({reg:.3f}) es >= 1.5x la del permutado ({vent['permutado']:.3f}).")
    else:
        out(f"=> REFLEJO: la mejor g paga parecido con y sin regularidad (clima {vent['clima']:.3f}, ciclo2 {vent['ciclo2']:.3f}, "
            f"permutado {vent['permutado']:.3f}); §37 no puede dar VESTIGIO por R2_A con esta perilla.")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
