"""
§K12 -- MATURITY: a slow awake rate only while an expert explains its stream, the full
rate while it does not (newborn, or failing). Does it give both, the stability of the slow
wake and the entry of the fast one?
(docs/MUNDO_PROPIO.md; written 2026-10-28, before any test pair; no calibration)

WHY. §K11 (replicated, 24/24 on every readout): one awake rate does not give stability
and plasticity. At lr x 0.1 the home expert keeps what sleep consolidates (awake oracle
0.009 vs coin's 0.042) and the identity holds, but the entry into a never-lived world is
late: all 59 stuck blocks fall in the first two exile blocks (coin 3), first exile block
0.956-0.970 vs 0.497-0.601. The exile's expert is spawned ~34 ticks into the exile in both
arms (post hoc, the stored §K11 lives: median 35 and 34 ticks); in coin_vigilia it is
born a copy of the home expert and learns awake at a tenth of the rate, and its share of
each sleep is tiny (the dose is split by buffer size).

DESIGN. ContextualWorldModel(wake_lr_scale_learning=s_l)
(tests/test_contextual_world_model.py): an expert learns awake at lr x wake_lr_scale only
while it EXPLAINS its stream -- established (its running error has been <= threshold
once) and its running error <= threshold now; otherwise (newborn, or failing) at
lr x s_l. Sleep keeps the full rate. Learning fast while an established expert fails is
protected by §K6's snapshot: a spawn or a switch restores it. One new arm under §K7's
"una", with §K4's life, roles, exile and assays: coin_madurez = coin + wake_lr_scale 0.1
+ wake_lr_scale_learning 1.0. coin and coin_vigilia are NOT re-run: their §K11 lives are
loaded from data/mundo_propio_vigilia (both already carry the awake probe; every §K11
coin equals its §K7 life). No snapshot_lag: one variable at a time.

AMENDED AFTER THE SMOKE TEST, BEFORE THIS PRE-REGISTRATION (pair 0, short life: not
evidence; recorded in docs/MUNDO_PROPIO.md). The first design gated the rate only on
"established" (fast for a newborn expert, slow forever after). Its smoke: the newborn
exile expert did learn fast, but the entry stayed coin_vigilia's (first exile block 0.886
vs coin 0.334 and coin_vigilia 0.982; exile ticks 35-100 at 0.92/0.88 vs coin's
0.21/0.14; the sibling's home at T1 0.895 vs 0.906 and 0.362): before the spawn (63 and
81 ticks) the learner is the established home expert, slow. The amended design (above)
also learns fast while the established expert fails. Its smoke: twin A enters like coin
(spawn at 34 ticks; first 35 / next 65 / last 200 exile ticks 0.842 / 0.305 / 0.063, coin
0.848 / 0.215 / 0.053); twin B is stuck before its spawn (81 ticks; 0.957 over the first
100, coin 0.41) -- stuck, the error stays small and the slow rate holds; first exile block
0.725; the sibling's home at T1 0.493 (T2 0.932, coin_vigilia 0.970, coin 0.623); awake
home oracle 0.019 (coin 0.061, coin_vigilia 0.025); H(T2) +1.53; home at T2 0.166 (coin
0.490). The verification passed in both smokes (diff 0).

VERIFICATION. Per run, coin_vigilia of the first pair, twin A, is re-run with this code
and must equal its stored §K11 life on every stored key (max diff 0) -- else stop: a bug.

Readouts per pair (mean of the twins), as in §K11: the home oracle right after a sleep
and awake (49 online steps later), median over the last 5 childhood blocks; H; the first
exile block's e_early.

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019). E = coin_madurez,
C = coin, V = coin_vigilia.
  PRECISA_M  (primary) awake home oracle E < C.
  ENTRA      (primary) first exile block e_early E < V.
  PERSISTE_M (primary) H(T2) E > 0.
  LENTO_M    (primary, the price) first exile block e_early E > C.
  VERDICT  no PRECISA_M -> NO CONSERVA; PRECISA_M without ENTRA -> SIGUE LENTA; both
           without PERSISTE_M -> SIN IDENTIDAD; the three without LENTO_M -> VIGILIA QUE
           NO BORRA; the three and LENTO_M -> MEJOR PERO NO GRATIS.
  Secondary: PAREADO H(T2) E > C and E > V; CONTROLA childhood e_late E < C; VUELVE home
  cost at T2 E < C (post hoc in §K11 for V, 19/24; pre-registered here); AFUERA abroad
  cost at T2 E < V; the exile expert's awake oracle at the end of the exile E < C; stuck
  blocks; ELIGE E.
  Reported: H at T1/Tm/T2; home/abroad costs; the oracle table; contexts; for E, the
  tick of the exile spawn.

PREDICTIONS (written after both smokes, before any test pair). VERIFICATION 1/1 per run.
PRECISA_M passes (the childhood's established home expert explains its stream almost
always). ENTRA passes. PERSISTE_M passes. LENTO_M leaning pass: twins stuck before the
spawn (smoke twin B) keep the slow rate. VERDICT, predicted: MEJOR PERO NO GRATIS (VIGILIA
QUE NO BORRA if the stuck twins are rare). Stuck blocks between coin's and coin_vigilia's.
VUELVE leaning pass. AFUERA uncertain (the smoke: better than coin_vigilia at T1, not at
T2).

REPLICATION, pre-registered with the test: pairs 12-23, the same rule, launched right
after the test unless a bug is found (any change recorded). REPLICADO if the verdict
repeats.

RESULT (pairs 0-11, results/mundo_propio_madurez_run.txt, 72.2 min on a shared machine;
the coin_vigilia re-run equals its §K11 life, max diff 0.0). Pre-registered verdict:
VIGILIA QUE NO BORRA -- better than predicted (MEJOR PERO NO GRATIS). PRECISA_M 12/12
(awake home oracle 0.009, coin 0.042, coin_vigilia 0.009), ENTRA 12/12 (first exile
block 0.367 vs coin_vigilia 0.970), PERSISTE_M 12/12 (H(T2) +0.375), LENTO_M 3/12 (coin
0.497). Stuck blocks 0 (coin 2, coin_vigilia 31); the exile spawn at 31-35 ticks in all
24 twins. Secondary: CONTROLA 12/12, AFUERA 12/12 (abroad T2 0.387 vs 0.969), the exile
expert's awake oracle at the end 0.028 vs coin's 0.062 (12/12), ELIGE 12/12; PAREADO
H(T2) > coin 3/12 (> coin_vigilia 0/12) and VUELVE 3/12 failed (home T2 0.168 vs 0.146).
Post hoc: the first exile block is BELOW coin's in 9/12 pairs, and the sibling's home
too (T1 11/12, Tm 10/12, T2 9/12): the smaller H is less rigidity abroad, not a weaker
home (home at Tm better 9/12, at T2 worse 9/12).

25 lives per run (24 new + 1 verification); 3 CPU processes, one torch thread each.
`reanudar` after any mode loads the lives already on disk.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez.py replica   # pairs 12-23
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

spec = importlib.util.spec_from_file_location("mundo_propio_vigilia", HERE / "exp_mundo_propio_vigilia.py")
k11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k11)
k8, k7, cr, co, g = k11.k8, k11.k7, k11.cr, k11.co, k11.g
co.BRAZOS["coin_madurez"] = {**co.BRAZOS["coin"],
                             "wm_context_kwargs": {"wake_lr_scale": k11.ESCALA_VIGILIA,
                                                   "wake_lr_scale_learning": 1.0}}
DATA_K11 = k11.DATA
k7.DATA = DATA = ROOT / "data" / "mundo_propio_madurez"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
NUEVO = "coin_madurez"
BRAZOS = ("coin", "coin_vigilia", NUEVO)


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def cargar_k11(brazo: str, par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K11 life ('una'), in the shape vivir() returns."""
    x = dict(np.load(DATA_K11 / f"una_{brazo}_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida((brazo, par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> tuple[dict, dict]:
    h = cr.humo(escala)
    verif = ("coin_vigilia", pares[0], "A", escala, "una", f"verif_coin_vigilia_{pares[0]}_A{h}", reanudar)
    tareas = [verif] + [(NUEVO, p, gm, escala, "una", f"una_{NUEVO}_{p}_{gm}{h}", reanudar)
                        for p in pares for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    V = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas[1:]}
    for a in BRAZOS[:2]:
        for p in pares:
            for gm in GEMELOS:
                V[(a, p, gm)] = cargar_k11(a, p, gm, escala)
    return V, vidas[0]


def veredicto(precisa: int, entra: int, persiste: int, lento: int) -> str:
    """The pre-registered §K12 rule."""
    if precisa < N_OK:
        return "NO CONSERVA"
    if entra < N_OK:
        return "SIGUE LENTA"
    if persiste < N_OK:
        return "SIN IDENTIDAD"
    return "MEJOR PERO NO GRATIS" if lento >= N_OK else "VIGILIA QUE NO BORRA"


def spawn_exilio(x: dict) -> int | None:
    """Ticks from the start of the exile to its first spawn."""
    nb, nn, _ = x["vida_bloques"]
    t0 = (nb + nn) * D
    ev = x["eventos"]
    ts = [int(t) - t0 for e, t, _ in ev if e == co.EVENTO["spawn"] and t >= t0]
    return min(ts) if ts else None


def informe(V: dict, x0: dict, pares: tuple, escala: dict, nombre: str, titulo: str,
            minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2 = T[-1], len(T) - 1
    nb, nn, ne = escala["vida"]
    ninez = range(nb + nn - min(k11.ULTIMOS, nn), nb + nn)
    exilio = range(nb + nn + ne - min(k11.ULTIMOS, ne), nb + nn + ne)
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; coin and coin_vigilia loaded from §K11, {NUEVO} "
        f"(wake_lr_scale {k11.ESCALA_VIGILIA}, wake_lr_scale_learning 1.0) new; run {minutos:.1f} min")
    dif = cr.diferencia(x0, cargar_k11("coin_vigilia", pares[0], "A", escala))
    out(f"verification: coin_vigilia pair {pares[0]} twin A re-run vs its stored §K11 life (every stored "
        f"key), max diff {dif}")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>12} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                       for t in T))
    out("costs (medians): home T1 | abroad T1 | home T2 | abroad T2 | first exile block | childhood e_late | "
        "stuck blocks (twins)")
    late = {a: [k11.por_par(V, a, p, lambda x, gm: np.mean([b["late"] for b in g.por_bloque(x, p)[nb:nb + nn]]))
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
    sp = [spawn_exilio(V[(NUEVO, p, gm)]) for p in pares for gm in GEMELOS]
    out(f"  {NUEVO}: ticks from the exile start to its first spawn {sp}")
    out(f"oracle (median over pairs of the twins' mean; median over the last {k11.ULTIMOS} blocks): "
        "right after a sleep | awake (49 online steps later)")
    O = {}
    for a in BRAZOS:
        for donde, bloques in (("home, childhood", ninez), ("exile, end", exilio)):
            def f(x, gm, campo, _b=bloques, _d=donde):
                p = x["par"]
                mundo = g.papeles(p)[gm] if _d.startswith("home") else g.papeles(p)["X"]
                return k11.oraculo(x, campo, mundo, _b)
            for campo in ("oraculo", "oraculo_vigilia"):
                O[(a, donde, campo)] = [k11.por_par(V, a, p, lambda x, gm, c=campo: f(x, gm, c)) for p in pares]
            out(f"  {a:>12} {donde:>15} | {np.median(O[(a, donde, 'oraculo')]):.3f} | "
                f"{np.median(O[(a, donde, 'oraculo_vigilia')]):.3f}")
    out("")
    out("-" * 80)
    mayor = lambda xs, ys: sum(x > y for x, y in zip(xs, ys))  # noqa: E731
    casa, fin = "home, childhood", "exile, end"
    precisa = mayor(O[("coin", casa, "oraculo_vigilia")], O[(NUEVO, casa, "oraculo_vigilia")])
    ex = {a: [cr.exilio(V, a, p) for p in pares] for a in BRAZOS}
    entra = mayor(ex["coin_vigilia"], ex[NUEVO])
    persiste = sum(v > 0 for v in H[(NUEVO, t2)])
    lento = mayor(ex[NUEVO], ex["coin"])
    out(f"PRECISA_M awake home oracle {NUEVO} < coin: {precisa}/{n}")
    out(f"ENTRA first exile block {NUEVO} < coin_vigilia: {entra}/{n}")
    out(f"PERSISTE_M H({t2}) {NUEVO} > 0: {persiste}/{n}")
    out(f"LENTO_M first exile block {NUEVO} > coin: {lento}/{n}")
    costo = {(a, f.__name__): [f(V, a, p, t2) for p in pares] for a in BRAZOS for f in (k8.casa, g.afuera)}
    out(f"(secondary) PAREADO H({t2}) {NUEVO} > coin: {mayor(H[(NUEVO, t2)], H[('coin', t2)])}/{n}, "
        f"> coin_vigilia: {mayor(H[(NUEVO, t2)], H[('coin_vigilia', t2)])}/{n} | CONTROLA childhood e_late "
        f"{NUEVO} < coin: {mayor(late['coin'], late[NUEVO])}/{n} | VUELVE home {t2} {NUEVO} < coin: "
        f"{mayor(costo[('coin', 'casa')], costo[(NUEVO, 'casa')])}/{n} | AFUERA abroad {t2} {NUEVO} < "
        f"coin_vigilia: {mayor(costo[('coin_vigilia', 'afuera')], costo[(NUEVO, 'afuera')])}/{n}")
    out(f"(secondary) exile expert awake oracle, end of the exile, {NUEVO} < coin: "
        f"{mayor(O[('coin', fin, 'oraculo_vigilia')], O[(NUEVO, fin, 'oraculo_vigilia')])}/{n} | ELIGE {NUEVO}: "
        f"{sum(k7.elige(V, p, j2, NUEVO) for p in pares)}/{n}")
    if n == len(g.PAIRS):
        v = "STOP: VERIFICATION FAILED" if dif != 0.0 else veredicto(precisa, entra, persiste, lento)
        out(f"VERDICT (pre-registered rule): {v}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    V, x0 = correr(pares, escala, reanudar)
    informe(V, x0, pares, escala, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_madurez_humo", "§K12 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_madurez_replica",
             "§K12 REPLICATION (pairs 12-23) -- maturity: a rate per expert", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_madurez", "§K12 -- maturity: a rate per expert", reanudar)
