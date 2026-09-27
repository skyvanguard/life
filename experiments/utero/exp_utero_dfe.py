"""
§16b — ESPECTRO DE EFECTOS DE LA VARIACIÓN (DFE): ¿qué produce cada parto,
cerrado (v14) contra abierto (v16), en la ecología de la escala?
(docs/PLAN_INTELIGENCIA.md §16; ledger 2026-09-27)

La evolución experimental mide primero su operador de variación: qué fracción
de las variantes es letal, neutra o viable-distinta (distribution of fitness
effects). Aquí se sigue a cada cría nacida por colonización en la ventana
[6000, 12000) hasta 500 ticks, en la ecología de §16 (hambruna dura, parto
costoso, luz finita L0 = 9, registros lentos), con la variación CERRADA
(germinal: sólo el opcode) y ABIERTA (escritura total: la fila entera).

MEDIDAS por brazo (10 semillas, sol seed 0, orden cíclico):
  - partos por 1000 ticks; fracción de crías IDÉNTICAS a la madre al nacer
    (la variación no cambió nada) y, entre las distintas, campos cambiados en
    la fila escrita (1 = sólo opcode; 2–4 = operandos también);
  - destino: muere en su 1ª ejecución / muere después (vida mediana) /
    sobrevive 100 / sobrevive 500 ticks — para crías idénticas y distintas por
    separado;
  - crías distintas de la madre que sobreviven 500 ticks por 1000 ticks: la
    OFERTA MUTACIONAL VIABLE, la cantidad que la selección tiene para trabajar;
  - genomas distintos entre las crías / partos.

LECTURA (escrita antes de correr, descriptiva; no hay veredicto de vestigio):
  si la oferta viable abierta es < 1 por 1000 ticks por mundo, la escala de
  §16 (120000 ticks) da < 120 variantes viables por mundo: la ausencia de
  adaptación sería falta de oferta, y lo siguiente es la tasa de variación,
  no la ecología. Si es ≥ 10 por 1000 ticks y aun así §16 da NADA, la oferta
  existe y lo que falta es que alguna variante tenga efecto sobre la
  mortalidad en la hambruna: se mide entonces el efecto, no la oferta.

    PYTHONPATH=src python experiments/utero/exp_utero_dfe.py
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
from zeta_life.utero.sol import REGIMENES, Sol  # noqa: E402

N0, MAX_N = 16, 512
TICKS = 12500
WIN = (6000, 12000)
FOLLOW = 500
SEEDS = list(range(10))
SOL_SEED = 0
REGS = (("A", 0.08, 0.02, 40),) + REGIMENES[1:]
BASE = dict(memoria=True, invasion="asentada", eq_window=100, energia=True, luz_finita=9.0,
            e0=2.0, e_mant=0.01, e_dif=0.25, e_parto=0.5, percepcion=False, lentos=0.02, e_costo=1.0)
ARMS = {"cerrado": dict(escritura_total=False), "abierto": dict(escritura_total=True)}
WORKERS = max(1, min(6, (os.cpu_count() or 4) // 4))
RESULTS = HERE.parents[1] / "results"
NAME = "utero_dfe"


def correr(seed: int, arm: str) -> dict:
    sol = Sol(seed=SOL_SEED, ticks=TICKS, regimenes=REGS)
    u = UteroCreciente(n0=N0, seed=seed, max_n=MAX_N, germinal=True, toroidal=True, sol=sol,
                       log_events=True, **BASE, **ARMS[arm])
    children: dict = {}
    done: list[dict] = []
    for t in range(TICKS):
        u.step()
        alive = np.flatnonzero(u.alive)
        cg = {int(i) - u.left_grown: u.code[i].tobytes() for i in alive}
        born = {c: m for m, c in u.spawns}
        for coord in list(children):
            rec = children[coord]
            if coord not in cg or coord in born:
                rec["life"] = t - rec["t0"]
                done.append(children.pop(coord))
                continue
            if t - rec["t0"] >= FOLLOW:
                rec["life"] = FOLLOW
                done.append(children.pop(coord))
        if WIN[0] <= t < WIN[1]:
            for coord, mother in born.items():
                if coord not in cg:
                    rec = dict(t0=t, life=0, same=None, fields=None, genome=None)
                    done.append(rec)        # nació y murió en el mismo tick
                    continue
                i = coord + u.left_grown
                mi = mother + u.left_grown
                child = u.code[i]
                if 0 <= mi < u.n and u.alive[mi]:
                    mom = u.code[mi]
                    diff = child != mom
                    same = not diff.any()
                    fields = int(diff.sum()) if not same else 0
                else:
                    same, fields = None, None
                children[coord] = dict(t0=t, life=None, same=same, fields=fields, genome=cg[coord])
    for rec in children.values():
        rec["life"] = TICKS - rec["t0"]
        rec["censurada"] = True
    ticks_win = WIN[1] - WIN[0]
    recs = [d for d in done if not d.get("censurada")]
    vivas = int(u.alive.sum())
    return dict(seed=seed, arm=arm, recs=recs, ticks_win=ticks_win, vivas=vivas,
                genomas=len(u.seen))


def job(a):
    return correr(*a)


def resumen(recs: list[dict], sel) -> dict:
    r = [d for d in recs if sel(d)]
    n = len(r)
    if n == 0:
        return dict(n=0)
    return dict(n=n,
                muere_1a=sum(1 for d in r if d["life"] <= 1) / n,
                vive100=sum(1 for d in r if d["life"] >= 100) / n,
                vive500=sum(1 for d in r if d["life"] >= FOLLOW) / n,
                vida_med=float(np.median([d["life"] for d in r])),
                distintos=len({d["genome"] for d in r if d["genome"] is not None}) / n)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out("=" * 80)
    out("DFE -- espectro de efectos de la variacion: cerrado (solo opcode) vs abierto (fila entera)")
    out("=" * 80)
    out(f"ecologia {BASE}; ventana {WIN}; seguimiento {FOLLOW}; {len(SEEDS)} semillas; sol seed {SOL_SEED}; workers={WORKERS}")
    out("")
    res: dict = {a: {} for a in ARMS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, [(s, a) for a in ARMS for s in SEEDS]):
            res[r["arm"]][r["seed"]] = r
    out(f"  {'brazo':<8} {'vivas':>5} {'genomas':>8} {'partos/1000t':>12} {'identicas':>9} {'campos=1':>8} {'campos>=2':>9} "
        f"{'oferta viable/1000t':>19}")
    tabla = {}
    for arm in ARMS:
        R = list(res[arm].values())
        allrecs = [d for r in R for d in r["recs"]]
        n = len(allrecs)
        ticks = sum(r["ticks_win"] for r in R)
        same = [d for d in allrecs if d["same"] is True]
        dist = [d for d in allrecs if d["same"] is False]
        f1 = sum(1 for d in dist if d["fields"] == 1)
        f2 = sum(1 for d in dist if d["fields"] is not None and d["fields"] >= 2)
        oferta = sum(1 for d in dist if d["life"] >= FOLLOW) / ticks * 1000 * len(R)   # por mundo
        tabla[arm] = dict(n=n, same=len(same), dist=len(dist), oferta=oferta / len(R))
        out(f"  {arm:<8} {np.median([r['vivas'] for r in R]):>5.0f} {np.median([r['genomas'] for r in R]):>8.0f} "
            f"{n / ticks * 1000:>12.2f} {len(same) / max(n, 1):>9.2f} {f1 / max(len(dist), 1):>8.2f} {f2 / max(len(dist), 1):>9.2f} "
            f"{oferta / len(R):>19.2f}")
    out("")
    out("  destino de las crias (idénticas a la madre | distintas):")
    out(f"  {'brazo':<8} {'tipo':<10} {'n':>6} {'muere 1a':>9} {'vive100':>8} {'vive500':>8} {'vida med':>9} {'distintos/n':>11}")
    for arm in ARMS:
        allrecs = [d for r in res[arm].values() for d in r["recs"]]
        for tipo, sel in (("identica", lambda d: d["same"] is True), ("distinta", lambda d: d["same"] is False),
                          ("murio_ya", lambda d: d["same"] is None)):
            s = resumen(allrecs, sel)
            if s["n"] == 0:
                out(f"  {arm:<8} {tipo:<10} {0:>6}")
                continue
            out(f"  {arm:<8} {tipo:<10} {s['n']:>6} {s['muere_1a']:>9.2f} {s['vive100']:>8.2f} {s['vive500']:>8.2f} "
                f"{s['vida_med']:>9.0f} {s['distintos']:>11.2f}")
    out("")
    out("=" * 80)
    out("LECTURA (descriptiva, regla en el docstring)")
    o = tabla["abierto"]["oferta"]
    if o < 1:
        out(f"=> OFERTA ESCASA: {o:.2f} variantes viables por 1000 ticks por mundo -> <{o * 120:.0f} en la escala de §16; "
            "la falta de adaptacion seria falta de oferta (tasa de variacion).")
    elif o >= 10:
        out(f"=> OFERTA SUFICIENTE: {o:.1f} variantes viables por 1000 ticks por mundo; si §16 da NADA, medir el EFECTO de las variantes, no la oferta.")
    else:
        out(f"=> OFERTA INTERMEDIA: {o:.1f} variantes viables por 1000 ticks por mundo (~{o * 120:.0f} en §16).")
    (RESULTS / f"{NAME}_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
