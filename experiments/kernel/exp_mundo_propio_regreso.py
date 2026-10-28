"""
§K13 -- THE RETURN: an established expert that becomes active again by a switch learns
awake slowly until it explains its stream. Does the return home stop costing what §K12's
maturity made it cost, while keeping what maturity gained?
(docs/MUNDO_PROPIO.md; written 2026-10-28, before any test pair; no calibration)

WHY. §K12 (replicated, 24/24 on PRECISA_M, ENTRA and PERSISTE_M): a per-expert awake rate
-- slow while an expert explains its stream, full while it is newborn or failing --
keeps what sleep consolidates and enters a never-lived world faster than coin. What
failed is VUELVE (7/24): back home after the exile it pays more than coin (0.165 vs
0.145). The §K12 mechanism (exp_mundo_propio_madurez_vuelta.py, 16 lives re-run, diff 0)
found why. Every expert predicts every tick, so the home expert's running error comes
home carrying the exile, and the switch is by margin, not by the threshold. Under
maturity the returning home expert "does not explain" (7/8 twins above the threshold)
and relearns awake at the full rate, and that relearning multiplies its home error by
~30 (0.007 -> 0.23 by tick 40; coin 0.09) until the next sleep. Slowing or freezing its
awake rate removed the excess (after-switch cost 0.083 -> 0.055, 7/8 and 6/8 twins).

DESIGN. ContextualWorldModel(slow_return=True) (tests/test_contextual_world_model.py):
an established expert made active by a SWITCH learns awake at lr x wake_lr_scale until it
explains its stream (running error <= threshold) or for at most `persist` ticks (30, the
model's own patience before a new context), then by §K12's rule. A spawn is not a return.
False = byte-identical. One new arm under §K7's "una", with §K4's life, roles, exile and
assays: coin_regreso = coin_madurez + slow_return. coin and coin_vigilia are loaded from
§K11 (data/mundo_propio_vigilia), coin_madurez from §K12 (data/mundo_propio_madurez);
none is re-run. In the stored §K12 lives 44/48 main lives have no switch at all (one spawn,
the exile's): there coin_regreso's main life must equal coin_madurez's, and the arms
differ only in the assays' clones -- where the returns are (a switch back to the home
expert in 48/48 home assays at Tm and T2; abroad at Tm/T2 the change is a spawn in 45-46/48,
not a return).

AMENDED AFTER THE SMOKE TEST, BEFORE THIS PRE-REGISTRATION (pair 0, short life: not
evidence; recorded in docs/MUNDO_PROPIO.md). The first design had no cap: slow until the
returning expert explains. Its smoke: verification diff 0, MISMA VIDA 2/2, but twin B in
its sibling's home at T1 went back to h at tick 52 and stayed there, slow, never
explaining (a spawn waits grace_spawn = 150 ticks): 0.841 over the first 100 ticks vs
coin_madurez's 0.547 (which flaps h <-> the new expert every 20 ticks). In the stored
§K12 lives a return to h in the sibling's home at T1 happens in ~6/48 twins. The amended
design caps the slow return at `persist` ticks: the mechanism's protected home expert
explained within a median 3-4 ticks, a wrong one never does. Its smoke: verification
diff 0, MISMA VIDA 2/2, the same twin 0.792 (the price is smaller, not gone); abroad T1
0.616 vs coin_madurez 0.493; home T2 0.165 vs 0.166 -- in the short life the return does
not damage h (the mechanism's smoke: lento_h 0.064 -> 0.062), so the smoke cannot show
the protection. The price readout RIGIDO_R now covers T1 as well (either assay: the
conservative side for the verdict).

VERIFICATION. Per run, coin_madurez of the first pair, twin A, is re-run with this code
and must equal its stored §K12 life on every stored key (max diff 0) -- else stop: a bug.

Readouts per pair (mean of the twins): the §K12 ones; plus, per home assay, the cost
after the switch to the home expert h (the first EARLY ticks from the first tick on h;
the §K12 mechanism's readout) and MISMA VIDA (every main-life key of coin_regreso equals
coin_madurez's, i.e. all but the assays' ens_*).

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019). E = coin_regreso,
M = coin_madurez, C = coin, V = coin_vigilia.
  PROTEGE    (primary) home cost at T2 E < M.
  VUELVE_R   (primary) home cost at T2 E < C.
  CONSERVA_R (primary) awake home oracle E < C and first exile block E < V (each >= 10/12).
  PERSISTE_R (primary) H(T2) E > 0.
  RIGIDO_R   (primary, the price) abroad cost E > M at T1 or at T2 (>= 10/12 in either).
  VERDICT  no CONSERVA_R or no PERSISTE_R -> PIERDE LO DEL K12; else no PROTEGE -> NO
           PROTEGE; PROTEGE without VUELVE_R -> PROTEGE PERO NO ALCANZA; both without
           RIGIDO_R -> VUELVE A CASA; both and RIGIDO_R -> VUELVE, MAS RIGIDO AFUERA.
  Secondary: RECUPERA the home cost after the switch at T2 E < M; PAREADO H(T2) E > M and
  E > C; AFUERA abroad cost at T2 E < V; home cost at Tm E < M; ELIGE E; stuck blocks.
  Reported: MISMA VIDA per twin (and whether its main life had a switch); H at
  T1/Tm/T2; home/abroad costs; the oracle table; contexts; the latency to h.

PREDICTIONS (written after both smokes, before any test pair). VERIFICATION 1/1 per run.
MISMA VIDA in every twin whose coin_madurez main life has no switch (44/48 in §K12).
CONSERVA_R passes (those main lives are §K12's, 24/24 there). PERSISTE_R passes. PROTEGE
passes (the mechanism: holding h slow lowered the after-switch cost in 7/8 twins, home
T2 0.163 -> 0.105). VUELVE_R leaning pass (that counterfactual 0.105 vs coin 0.147 over 8
twins; §K12's earlier switch to h, 19/24 pooled). RIGIDO_R does not pass: abroad at T2 the
change is a spawn in 45/48 twins, and the T1 returns are ~6/48. VERDICT, predicted: VUELVE
A CASA. Secondary: RECUPERA passes; PAREADO E > M leaning pass, E > C fails (§K12 4/24:
coin's H is mostly rigidity abroad); AFUERA passes; home Tm E < M leaning pass; ELIGE
passes; stuck blocks = coin_madurez's.

REPLICATION, pre-registered with the test: pairs 12-23, the same rule, launched right
after the test unless a bug is found (any change recorded). REPLICADO if the verdict
repeats.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_regreso.py replica   # pairs 12-23

25 lives per run (24 new + 1 verification); 3 CPU processes, one torch thread each.
`reanudar` after any mode loads the lives already on disk.
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

spec = importlib.util.spec_from_file_location("mundo_propio_madurez", HERE / "exp_mundo_propio_madurez.py")
k12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k12)
k11, k8, k7, cr, co, g = k12.k11, k12.k8, k12.k7, k12.cr, k12.co, k12.g
NUEVO = "coin_regreso"
MADUREZ = k12.NUEVO
co.BRAZOS[NUEVO] = {**co.BRAZOS[MADUREZ],
                    "wm_context_kwargs": {**co.BRAZOS[MADUREZ]["wm_context_kwargs"], "slow_return": True}}
DATA_K12 = k12.DATA
k7.DATA = DATA = ROOT / "data" / "mundo_propio_regreso"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
EARLY = g.mp.EARLY
BRAZOS = ("coin", "coin_vigilia", MADUREZ, NUEVO)


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def cargar_k12(par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K12 coin_madurez life, in the shape vivir() returns."""
    x = dict(np.load(DATA_K12 / f"una_{MADUREZ}_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida((MADUREZ, par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> tuple[dict, dict]:
    h = cr.humo(escala)
    verif = (MADUREZ, pares[0], "A", escala, "una", f"verif_{MADUREZ}_{pares[0]}_A{h}", reanudar)
    tareas = [verif] + [(NUEVO, p, gm, escala, "una", f"una_{NUEVO}_{p}_{gm}{h}", reanudar)
                        for p in pares for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    V = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas[1:]}
    for p in pares:
        for gm in GEMELOS:
            for a in ("coin", "coin_vigilia"):
                V[(a, p, gm)] = k12.cargar_k11(a, p, gm, escala)
            V[(MADUREZ, p, gm)] = cargar_k12(p, gm, escala)
    return V, vidas[0]


def veredicto(protege: int, vuelve: int, conserva: bool, persiste: int, rigido: int) -> str:
    """The pre-registered §K13 rule."""
    if not conserva or persiste < N_OK:
        return "PIERDE LO DEL K12"
    if protege < N_OK:
        return "NO PROTEGE"
    if vuelve < N_OK:
        return "PROTEGE PERO NO ALCANZA"
    return "VUELVE, MAS RIGIDO AFUERA" if rigido >= N_OK else "VUELVE A CASA"


def despues(x: dict, j: int) -> tuple[float, int]:
    """Home assay j of a twin: (cost after the first tick on h, summed over the first EARLY
    ticks and divided by EARLY; that first tick, EARLY if never)."""
    h, _ = k7.casa_exilio(x, x["par"])
    i = GEMELOS.index(x["gemelo"])
    c, d = x["ens_ctx"][j, i, :EARLY], x["ens_dist"][j, i, :EARLY]
    sw = int(np.flatnonzero(c == h)[0]) if (c == h).any() else EARLY
    return float(d[sw:].sum() / EARLY), sw


def misma_vida(x: dict, ref: dict) -> bool:
    """Every main-life array equal (all but the assays' ens_*)."""
    claves = [k for k, v in ref.items() if isinstance(v, np.ndarray) and not k.startswith("ens_")]
    return cr.diferencia({k: x[k] for k in claves}, {k: ref[k] for k in claves}) == 0.0


def cambios(x: dict) -> int:
    return int((x["eventos"][:, 0] == co.EVENTO["switch"]).sum()) if len(x["eventos"]) else 0


def informe(V: dict, x0: dict, pares: tuple, escala: dict, nombre: str, titulo: str,
            minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2, jm = T[-1], len(T) - 1, T.index("Tm")
    nb, nn, ne = escala["vida"]
    ninez = range(nb + nn - min(k11.ULTIMOS, nn), nb + nn)
    exilio = range(nb + nn + ne - min(k11.ULTIMOS, ne), nb + nn + ne)
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; coin and coin_vigilia loaded from §K11, {MADUREZ} from §K12, "
        f"{NUEVO} ({MADUREZ} + slow_return) new; run {minutos:.1f} min")
    dif = cr.diferencia(x0, cargar_k12(pares[0], "A", escala))
    out(f"verification: {MADUREZ} pair {pares[0]} twin A re-run vs its stored §K12 life (every stored key), "
        f"max diff {dif}")
    mv = [(p, gm, misma_vida(V[(NUEVO, p, gm)], V[(MADUREZ, p, gm)]), cambios(V[(MADUREZ, p, gm)]))
          for p in pares for gm in GEMELOS]
    sin = [m for m in mv if m[3] == 0]
    out(f"MISMA VIDA ({NUEVO} main life == {MADUREZ}'s): {sum(m[2] for m in mv)}/{len(mv)} twins; "
        f"{sum(m[2] for m in sin)}/{len(sin)} of those whose {MADUREZ} main life has no switch; with switches: "
        f"{[(p, gm, s, c) for p, gm, s, c in mv if c]}")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>12} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                       for t in T))
    out("costs (medians): home T1 | abroad T1 | home Tm | home T2 | abroad T2 | first exile block | "
        "stuck blocks (twins)")
    for a in BRAZOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares])
               for t, f in (("T1", k8.casa), ("T1", g.afuera), ("Tm", k8.casa), (t2, k8.casa), (t2, g.afuera))]
        out(f"  {a:>12} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
    out("home assay, after the switch to h (median over pairs of the twins' mean) | first tick on h (median "
        "over twins)")
    R = {(a, j): [k11.por_par(V, a, p, lambda x, gm, _j=j: despues(x, _j)[0]) for p in pares]
         for a in BRAZOS for j in (jm, j2)}
    for a in BRAZOS:
        lat = {j: np.median([despues(V[(a, p, gm)], j)[1] for p in pares for gm in GEMELOS]) for j in (jm, j2)}
        out(f"  {a:>12} | Tm {np.median(R[(a, jm)]):.3f} (tick {lat[jm]:.0f}) | {t2} {np.median(R[(a, j2)]):.3f} "
            f"(tick {lat[j2]:.0f})")
    out("experts")
    for a in BRAZOS:
        k8.expertos(V, a, pares, escala, out)
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
    costo = {(a, f.__name__, t): [f(V, a, p, t) for p in pares]
             for a in BRAZOS for f in (k8.casa, g.afuera) for t in ("Tm", t2)}
    ex = {a: [cr.exilio(V, a, p) for p in pares] for a in BRAZOS}
    casa = "home, childhood"
    protege = mayor(costo[(MADUREZ, "casa", t2)], costo[(NUEVO, "casa", t2)])
    vuelve = mayor(costo[("coin", "casa", t2)], costo[(NUEVO, "casa", t2)])
    precisa = mayor(O[("coin", casa, "oraculo_vigilia")], O[(NUEVO, casa, "oraculo_vigilia")])
    entra = mayor(ex["coin_vigilia"], ex[NUEVO])
    persiste = sum(v > 0 for v in H[(NUEVO, t2)])
    afuera_t1 = {a: [g.afuera(V, a, p, "T1") for p in pares] for a in (MADUREZ, NUEVO)}
    rigido_t1 = mayor(afuera_t1[NUEVO], afuera_t1[MADUREZ])
    rigido_t2 = mayor(costo[(NUEVO, "afuera", t2)], costo[(MADUREZ, "afuera", t2)])
    rigido = max(rigido_t1, rigido_t2)
    out(f"PROTEGE home {t2} {NUEVO} < {MADUREZ}: {protege}/{n}")
    out(f"VUELVE_R home {t2} {NUEVO} < coin: {vuelve}/{n}")
    out(f"CONSERVA_R awake home oracle {NUEVO} < coin: {precisa}/{n}; first exile block {NUEVO} < coin_vigilia: "
        f"{entra}/{n}")
    out(f"PERSISTE_R H({t2}) {NUEVO} > 0: {persiste}/{n}")
    out(f"RIGIDO_R abroad {NUEVO} > {MADUREZ}: T1 {rigido_t1}/{n}, {t2} {rigido_t2}/{n}")
    out(f"(secondary) RECUPERA after the switch {t2} {NUEVO} < {MADUREZ}: {mayor(R[(MADUREZ, j2)], R[(NUEVO, j2)])}/{n}"
        f" | PAREADO H({t2}) {NUEVO} > {MADUREZ}: {mayor(H[(NUEVO, t2)], H[(MADUREZ, t2)])}/{n}, > coin: "
        f"{mayor(H[(NUEVO, t2)], H[('coin', t2)])}/{n} | AFUERA abroad {t2} {NUEVO} < coin_vigilia: "
        f"{mayor(costo[('coin_vigilia', 'afuera', t2)], costo[(NUEVO, 'afuera', t2)])}/{n} | home Tm {NUEVO} < "
        f"{MADUREZ}: {mayor(costo[(MADUREZ, 'casa', 'Tm')], costo[(NUEVO, 'casa', 'Tm')])}/{n} | ELIGE {NUEVO}: "
        f"{sum(k7.elige(V, p, j2, NUEVO) for p in pares)}/{n}")
    if n == len(g.PAIRS):
        conserva = precisa >= N_OK and entra >= N_OK
        v = "STOP: VERIFICATION FAILED" if dif != 0.0 else veredicto(protege, vuelve, conserva, persiste, rigido)
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
        main((0,), g.HUMO, "mundo_propio_regreso_humo", "§K13 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_regreso_replica",
             "§K13 REPLICATION (pairs 12-23) -- the return", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_regreso", "§K13 -- the return", reanudar)
