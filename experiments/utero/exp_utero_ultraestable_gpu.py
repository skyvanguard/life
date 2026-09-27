"""
§43 (GPU) — ULTRAESTABILIDAD: ¿un tejido que reescribe su regla cuando le va
mal y la conserva cuando le va bien aprende en vida?
(docs/PLAN_INTELIGENCIA.md §43; ledger 2026-09-27)

CAMBIO DE RUMBO. El programa del sol derivó hacia la biología: metabolismo,
selección, historia de vida, perillas heredables diseñadas desde afuera.
Eso es evolución de poblaciones, y la idea original de Fran es otra: una IA
que NACE y aprende en vida, no una que se selecciona entre generaciones ni
una que encuentra patrones en datos. En el útero lo único que juzga es la
muerte: una celda reescribe su regla sin saber si le va bien o mal; por eso
produce novedad y no competencia. Falta que las consecuencias vuelvan sobre
la reescritura. Ashby (1948) lo llamó ultraestabilidad y lo construyó en el
homeostato: reconfigurarse cuando las variables esenciales salen de rango y
dejar de hacerlo cuando vuelven. Sin maestro, sin datos, sin objetivo.

QUÉ SE CAMBIA. Una sola cosa, y respeta los tres principios (la regla es
estado, el lazo es interno, persistir es el único criterio): las
auto-reescrituras de una celda (MUTO, COPY) se aplican sólo en los ticks en
que su ingreso de luz no cubre su mantenimiento (déficit metabólico propio).
No hay perillas θ, s, g: es la física original del útero, con escritura
total. La cría copia exacto la regla de la madre (sin germinal): toda la
variación viene de reescrituras hechas en vida.

DISEÑO. Ecología cerrada N = 512, L0 = 14, sol seed 0 cíclico, 120000 ticks,
24 semillas, la misma sopa por semilla en los cuatro brazos (96 mundos):
  ultra      reescribe sólo cuando le va mal.
  siempre    reescribe siempre (el útero original).
  invertido  reescribe sólo cuando le va BIEN (control adversarial: la misma
             cantidad de compuerta, con el signo al revés).
  nunca      no reescribe (congelado): lo que logra la sola criba entre las
             reglas de la sopa.
LECTURAS, sobre la segunda mitad de la corrida, pareadas por semilla:
  COSECHA  peso de luz medio de las vivas (w̄ = distancia toroidal media de
           la materia al sol + 0.05): qué tan bien cosecha la regla que el
           tejido tiene.
  MUERTE   muertes por celda viva y por tick.
  DENSIDAD vivas medias (el confusor de §30–§31: menos vivas = más luz por
           celda). Una ventaja en MUERTE sólo cuenta si las vivas del brazo
           ultra son ≥ 0.9 × las del control.
  "ultra supera a X" = COSECHA mayor en ≥ 75% de los pares Y MUERTE menor en
  ≥ 75% de los pares (p signo < 0.05 en ambas), sin pagar con densidad.
VEREDICTO (escrito antes de correr):
  APRENDE EN VIDA  si ultra supera a siempre, a invertido Y a nunca. Primer
                   vestigio: las reglas halladas en vida, guiadas por la
                   propia situación, son mejores que las que deja la criba.
                   Antes de creerlo: réplica con otro sol.
  COMPUERTA        si ultra supera a siempre y a invertido pero no a nunca:
                   la compuerta sólo limita el daño de reescribir; no
                   encuentra nada mejor que lo que ya había en la sopa.
  NADA             en otro caso.

    PYTHONPATH=src python experiments/utero/exp_utero_ultraestable_gpu.py
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
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
ARMS = {"ultra": dict(ultra=1, congelado=False), "siempre": dict(ultra=0, congelado=False),
        "invertido": dict(ultra=-1, congelado=False), "nunca": dict(ultra=0, congelado=True)}
RESULTS = HERE.parents[1] / "results"
CKPT = HERE.parents[1] / "data" / "ckpt"
NAME = "utero_ultraestable_gpu"


def signo_p(k: int, n: int) -> float:
    return float(sum(math.comb(n, j) * 0.5 ** n for j in range(k, n + 1))) if n > 0 else 1.0


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    ns = len(SEEDS)
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    seeds, ultra, cong = [], [], []
    for a in ARMS.values():
        seeds += SEEDS
        ultra += [a["ultra"]] * ns
        cong += [a["congelado"]] * ns
    out("=" * 80)
    out("ULTRAESTABILIDAD (GPU): reescribir la propia regla solo cuando a la celda le va mal -- aprende en vida?")
    out("=" * 80)
    out(f"N={N}; L0={L0}; {ns} semillas x {len(ARMS)} brazos = {len(seeds)} mundos; {TICKS} ticks; sol seed {SOL_SEED}; "
        f"escritura total, sin germinal, sin perillas; dispositivo {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    out("veredicto pre-registrado (docstring)")
    out("")
    CKPT.mkdir(parents=True, exist_ok=True)
    g = UteroGPU(seeds, N, np.tile(sol.serie, (len(seeds), 1)), luz_finita=L0, escritura_total=True, germinal=False,
                 congelado=cong, ultraestable=ultra)
    t0 = time.time()
    ser = g.correr(TICKS, checkpoint=str(CKPT / f"{NAME}.pt"), cada=5000)
    out(f"corrida: {(time.time() - t0) / 60:.1f} min")
    m = TICKS // 2
    enA = np.zeros(TICKS, dtype=bool)
    for nombre, ini, fin in sol.estaciones:
        if nombre == "A":
            enA[ini:min(fin, TICKS)] = True
    res = {}
    for i, a in enumerate(ARMS):
        sl = slice(i * ns, (i + 1) * ns)
        viv = ser["vivas"][m:, sl]
        vm_ = viv.mean(axis=0)
        res[a] = dict(
            w=np.nanmean(ser["w"][m:, sl], axis=0),
            wA=np.nanmean(ser["w"][m:, sl][enA[m:]], axis=0),
            w1=np.nanmean(ser["w"][:m, sl], axis=0),
            mu=ser["muertes"][m:, sl].sum(axis=0) / np.where(vm_ > 0, vm_, np.nan) / (TICKS - m),
            vivas=vm_, fin=ser["vivas"][-1, sl], partos=ser["partos"][m:, sl].sum(axis=0) / np.where(vm_ > 0, vm_, np.nan) / (TICKS - m) * 100)
    out("-" * 80)
    out("ESTADO por brazo (medianas; segunda mitad de la corrida)")
    out(f"  {'brazo':<10} {'vivas':>6} {'vivas fin':>9} {'cosecha w':>10} {'w en A':>7} {'w 1a mitad':>10} {'muerte/celda/tick':>18} {'partos/100t':>11}")
    for a, r in res.items():
        f = lambda k: float(np.nanmedian(r[k]))   # noqa: E731
        out(f"  {a:<10} {f('vivas'):>6.0f} {f('fin'):>9.0f} {f('w'):>10.3f} {f('wA'):>7.3f} {f('w1'):>10.3f} {f('mu'):>18.5f} {f('partos'):>11.3f}")
    out("")
    out("-" * 80)
    out("ULTRA contra cada control (pareado por semilla)")
    supera = {}
    for c in ("siempre", "invertido", "nunca"):
        u, x = res["ultra"], res[c]
        ok_par = [i for i in range(ns) if u["fin"][i] > 0 and x["fin"][i] > 0 and not np.isnan(u["w"][i]) and not np.isnan(x["w"][i])]
        kw = sum(1 for i in ok_par if u["w"][i] > x["w"][i])
        km = sum(1 for i in ok_par if u["mu"][i] < x["mu"][i])
        n = len(ok_par)
        dens = float(np.nanmedian(u["vivas"]) / max(np.nanmedian(x["vivas"]), 1e-9))
        supera[c] = (n >= 8 and kw / n >= 0.75 and signo_p(kw, n) < 0.05 and km / n >= 0.75 and signo_p(km, n) < 0.05 and dens >= 0.9)
        out(f"  vs {c:<10} cosecha mayor en {kw}/{n} (p {signo_p(kw, n):.3f}); muerte menor en {km}/{n} (p {signo_p(km, n):.3f}); "
            f"vivas ultra/control {dens:.2f} -> {'SUPERA' if supera[c] else 'no'}")
    out("")
    out("=" * 80)
    out("VEREDICTO (regla escrita antes de correr)")
    if all(supera.values()):
        out("=> APRENDE EN VIDA: el tejido que reescribe su regla solo cuando le va mal cosecha mas y muere menos que el que reescribe siempre, "
            "que el que reescribe al reves y que el que no reescribe. ANTES DE CREERLO: replicar con otro sol.")
    elif supera["siempre"] and supera["invertido"]:
        out("=> COMPUERTA: la compuerta limita el dano de reescribir, pero no encuentra nada mejor que lo que deja la criba de la sopa.")
    else:
        out("=> NADA: reescribir segun la propia situacion no mejora al tejido con esta vara.")
    (RESULTS / f"{NAME}_run.txt").write_text(chr(10).join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
