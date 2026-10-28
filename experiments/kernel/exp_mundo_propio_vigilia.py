"""
§K11 -- THE WAKE THAT DOES NOT ERASE: does a smaller online (awake) learning rate keep
what the sleep consolidates, and what does it cost?
(docs/MUNDO_PROPIO.md; written 2026-10-27, before any test pair; no calibration)

WHY. §K10's measurement: the slept home expert is precise only right after each sleep --
over the last 150 childhood ticks of one coin life, 0.004-0.006 right after a sleep,
median 0.012, above 0.05 in 44/151 ticks, up to 0.215 -- and every block-end probe of the
programme falls right after a sleep. A post hoc look at that life: the test ticks raise
the probe on average (+0.007 vs -0.0001), but 15 of the 21 jumps above +0.01 come at
ordinary ticks, in runs (0.037 -> 0.069 -> 0.110 -> 0.152): online learning between two
sleeps, not only the surprises. Most of the time the world model the kernel plans with
is much worse than the block-end probes say.

DESIGN. ContextualWorldModel(wake_lr_scale=s) (tests/test_contextual_world_model.py): the
awake steps of the learning expert use the optimizer's rate times s; sleep keeps the
full rate. One new arm under §K7's "una", with §K4's life, roles, exile and assays:
coin_vigilia = coin + wake_lr_scale 0.1. coin itself is RE-RUN as the control, because
the loop now also probes one tick before the block's last step (49 online steps after
a sleep, before the next; the block-end probe comes right after that sleep): every coin
re-run must reproduce its stored §K7 life exactly on the stored keys (max diff 0, the
probe only reads; checked on the §K8 smoke life). Both arms keep §K6's snapshot (no
snapshot_lag): one variable at a time.

Readouts per pair (mean of the twins): the home oracle right after a sleep (block end)
and 49 online steps after it ("awake"), median over the last 5 childhood blocks; H; the
first exile block's e_early (entering a never-lived world).

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019):
  VERIFICATION every coin re-run equals its §K7 life (diff 0) -- else stop: a bug.
  EROSIONA (control) coin: awake home oracle > right-after-sleep home oracle.
  PRECISA  (primary) awake home oracle coin_vigilia < coin.
  PERSISTE_V (primary) H(T2) coin_vigilia > 0.
  LENTO    (primary, the price) first exile block e_early coin_vigilia > coin.
  VERDICT  no EROSIONA -> NO HAY EROSION; no PRECISA -> LA TASA NO LA EVITA; PRECISA and
           PERSISTE_V without LENTO -> VIGILIA QUE NO BORRA; PRECISA and PERSISTE_V and
           LENTO -> PRECISA PERO LENTA; PRECISA without PERSISTE_V -> PRECISA SIN
           IDENTIDAD.
  Secondary: PAREADO H(T2) coin_vigilia > coin and the reverse; CONTROLA (the childhood's
  mean e_late, coin_vigilia < coin); stuck blocks; ELIGE.
  Reported: H at T1/Tm/T2; home/abroad costs; the oracle table (right after sleep /
  awake) for the home at the end of the childhood and for the exile expert at the end of
  the exile; contexts.

PREDICTIONS (written before any test pair). VERIFICATION 24/24. EROSIONA passes. PRECISA
passes: a step ten times smaller erodes less. PERSISTE_V passes. LENTO passes: learning
the never-lived exile awake goes ten times slower, and sleep alone (every 50 ticks) does
not make up for the first block. VERDICT PRECISA PERO LENTA. CONTROLA uncertain (a more
precise model to plan with, but slower to follow the own stream).

NOTE AFTER THE SMOKE TEST, BEFORE THE TEST (pair 0, short life: not evidence). The coin
re-run equals its §K7 life (diff 0). The awake home oracle: coin 0.004 right after a
sleep -> 0.061 awake; coin_vigilia 0.005 -> 0.025 (erosion halved, not gone). The price
looks large: the first exile block 0.982 vs coin's 0.334 (one twin stuck), the sibling's
home at T1 0.906 vs 0.362. The predictions above stand as written.

REPLICATION, pre-registered with the test: pairs 12-23, the same rule, launched right
after the test unless a bug is found (any change recorded). REPLICADO if the verdict
repeats.

RESULT (pairs 0-11, results/mundo_propio_vigilia_run.txt, 121.8 min on a shared machine;
every coin re-run equals its §K7 life, max diff 0.0 over 24). Pre-registered verdict:
PRECISA PERO LENTA, as predicted -- EROSIONA 12/12 (coin's home oracle 0.005 right after a
sleep -> 0.042 awake), PRECISA 12/12 (coin_vigilia 0.004 -> 0.009), PERSISTE_V 12/12
(H(T2) +1.70; coin +0.69), LENTO 12/12 (first exile block 0.970 vs 0.497). Secondary:
PAREADO 12/12 (reverse 0/12), CONTROLA 12/12 (childhood e_late 0.034 vs 0.038), ELIGE
12/12. The exile expert does not erode either (end of exile 0.023 -> 0.022; coin 0.031 ->
0.062). The price is the entry into a never-lived world: post hoc, all 31 stuck blocks
fall in the exile (23 in its first block, 8 in the second; none in the childhood; coin 2),
and from the third exile block on e_late is coin's (0.033-0.036); the sibling's home in
the assays costs 0.94-0.97 (coin 0.49-0.51). Much of the larger H is that price (home at
T2 0.109 vs 0.146, abroad 0.969 vs 0.489).

48 lives per run (24 coin re-runs + 24 new); 3 CPU processes, one torch thread each.
`reanudar` after any mode loads the lives already on disk.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_vigilia.py replica   # pairs 12-23
"""

from __future__ import annotations

import importlib.util
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("mundo_propio_foto", HERE / "exp_mundo_propio_foto.py")
k10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k10)
k9, k8, k7, cr, co, g = k10.k9, k10.k8, k10.k7, k10.cr, k10.co, k10.g
ESCALA_VIGILIA = 0.1
co.BRAZOS["coin_vigilia"] = {**co.BRAZOS["coin"], "wm_context_kwargs": {"wake_lr_scale": ESCALA_VIGILIA}}
k7.DATA = DATA = ROOT / "data" / "mundo_propio_vigilia"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
BRAZOS = ("coin", "coin_vigilia")
ULTIMOS = 5


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def correr(pares: tuple, escala: dict, reanudar: bool) -> dict:
    h = cr.humo(escala)
    tareas = [(a, p, gm, escala, "una", f"una_{a}_{p}_{gm}{h}", reanudar)
              for a in BRAZOS for p in pares for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    return {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas}


def veredicto(erosiona: int, precisa: int, persiste: int, lento: int) -> str:
    """The pre-registered §K11 rule."""
    if erosiona < N_OK:
        return "NO HAY EROSION"
    if precisa < N_OK:
        return "LA TASA NO LA EVITA"
    if persiste < N_OK:
        return "PRECISA SIN IDENTIDAD"
    return "PRECISA PERO LENTA" if lento >= N_OK else "VIGILIA QUE NO BORRA"


def oraculo(x: dict, campo: str, mundo: int, bloques: range) -> float:
    return float(np.median(np.asarray(x[campo])[list(bloques), mundo]))


def por_par(V: dict, a: str, p: int, f) -> float:
    return float(np.mean([f(V[(a, p, gm)], gm) for gm in GEMELOS]))


def informe(V: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2 = T[-1], len(T) - 1
    nb, nn, ne = escala["vida"]
    ninez = range(nb + nn - min(ULTIMOS, nn), nb + nn)
    exilio = range(nb + nn + ne - min(ULTIMOS, ne), nb + nn + ne)
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; coin re-run (control) and coin_vigilia (wake_lr_scale "
        f"{ESCALA_VIGILIA}); run {minutos:.1f} min")
    difs = [cr.diferencia(V[("coin", p, gm)], k8.cargar_k7(p, gm, escala)) for p in pares for gm in GEMELOS]
    out(f"verification: every coin re-run vs its stored §K7 life (stored keys), max diff {max(difs)} over "
        f"{len(difs)} lives")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>12} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                       for t in T))
    out("costs (medians): home T1 | abroad T1 | home T2 | abroad T2 | first exile block | childhood e_late | "
        "stuck blocks (twins)")
    late = {a: [por_par(V, a, p, lambda x, gm: np.mean([b["late"] for b in g.por_bloque(x, p)[nb:nb + nn]]))
                for p in pares] for a in BRAZOS}
    for a in BRAZOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares]) for t in ("T1", t2) for f in (k8.casa, g.afuera)]
        out(f"  {a:>12} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | {np.median(late[a]):.3f} | "
            f"stuck {b} ({tw}/{2 * n})")
    out("experts")
    for a in BRAZOS:
        k8.expertos(V, a, pares, escala, out)
    out(f"oracle (median over pairs of the twins' mean; median over the last {ULTIMOS} blocks): "
        "right after a sleep | awake (49 online steps later)")
    O = {}
    for a in BRAZOS:
        for donde, bloques in (("home, childhood", ninez), ("exile, end", exilio)):
            def f(x, gm, campo, _b=bloques, _d=donde):
                p = x["par"]
                mundo = g.papeles(p)[gm] if _d.startswith("home") else g.papeles(p)["X"]
                return oraculo(x, campo, mundo, _b)
            for campo in ("oraculo", "oraculo_vigilia"):
                O[(a, donde, campo)] = [por_par(V, a, p, lambda x, gm, c=campo: f(x, gm, c)) for p in pares]
            out(f"  {a:>12} {donde:>15} | {np.median(O[(a, donde, 'oraculo')]):.3f} | "
                f"{np.median(O[(a, donde, 'oraculo_vigilia')]):.3f}")
    out("")
    out("-" * 80)
    mayor = lambda xs, ys: sum(x > y for x, y in zip(xs, ys))  # noqa: E731
    casa = "home, childhood"
    erosiona = mayor(O[("coin", casa, "oraculo_vigilia")], O[("coin", casa, "oraculo")])
    precisa = mayor(O[("coin", casa, "oraculo_vigilia")], O[("coin_vigilia", casa, "oraculo_vigilia")])
    persiste = sum(v > 0 for v in H[("coin_vigilia", t2)])
    ex = {a: [cr.exilio(V, a, p) for p in pares] for a in BRAZOS}
    lento = mayor(ex["coin_vigilia"], ex["coin"])
    out(f"EROSIONA coin awake > right after sleep (home, childhood): {erosiona}/{n}")
    out(f"PRECISA awake home oracle coin_vigilia < coin: {precisa}/{n}")
    out(f"PERSISTE_V H({t2}) coin_vigilia > 0: {persiste}/{n}")
    out(f"LENTO first exile block coin_vigilia > coin: {lento}/{n}")
    out(f"(secondary) PAREADO H({t2}) coin_vigilia > coin: {mayor(H[('coin_vigilia', t2)], H[('coin', t2)])}/{n}, "
        f"coin > coin_vigilia: {mayor(H[('coin', t2)], H[('coin_vigilia', t2)])}/{n} | CONTROLA childhood "
        f"e_late coin_vigilia < coin: {mayor(late['coin'], late['coin_vigilia'])}/{n} | ELIGE coin_vigilia: "
        f"{sum(k7.elige(V, p, j2, 'coin_vigilia') for p in pares)}/{n}")
    if n == len(g.PAIRS):
        v = "STOP: VERIFICATION FAILED" if max(difs) != 0.0 else veredicto(erosiona, precisa, persiste, lento)
        out(f"VERDICT (pre-registered rule): {v}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    V = correr(pares, escala, reanudar)
    informe(V, pares, escala, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_vigilia_humo", "§K11 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_vigilia_replica",
             "§K11 REPLICATION (pairs 12-23) -- the wake that does not erase", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_vigilia", "§K11 -- the wake that does not erase", reanudar)
