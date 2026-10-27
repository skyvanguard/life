"""
§K9 -- THE SLEEP OF THE CHILDHOOD: is a precise home expert, frozen through the exile,
enough to keep the identity, or must the kernel keep sleeping?
(docs/MUNDO_PROPIO.md; written 2026-10-27, before any test pair; no calibration)

WHY. §K8: the repertoire's identity is the sleep's (POR EL SUENO, replicated: without
sleep PERSISTE 14/24, with sleep 24/24). Its mechanism readout: without sleep the home
expert is kept FROZEN through the exile (39/48) but it is coarse (0.087 vs 0.005) and it
is hit at the exile's start (the running error crosses the threshold a few ticks late,
so the restored snapshot already holds the first exile updates); back home the clone
does not tell it from the exile expert. Sleep does two things there: it makes the home
expert precise in the childhood, and it keeps every expert (the inactive ones too)
replayed through the exile. §K9 separates them.

DESIGN. One new arm, coin_ninez: coin (error_x4 + wm_contexts=6) whose world model stops
sleeping when the exile begins (k.wm_sleep_replay = 0 right after the T1 assay; the
clones of the Tm and T2 assays inherit it). Under §K7's "una", with §K4's life, roles,
exile and assays. Read: coin (§K7, sleeps all its life, assays included) and
coin_sin_sueno (§K8, never sleeps). Its life up to the exile is coin's, so EVERY life is
verified: the childhood (per-tick series and probes up to the exile, the assays before
it, the self_embedding and the context events there) must equal the stored §K7 life
exactly (max diff 0). Declared: EXILIO below measures all the sleep after the
childhood -- the exile's and the Tm/T2 assays' -- not the exile's alone. No calibration
this time: in §K7 and §K8 the 3-pair calibration misled and nothing was tuned; the smoke
test checks the mechanism.

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019):
  PERSISTE_N (primary) H(T2) coin_ninez > 0.
  NINEZ      (primary) H(T2) coin_ninez > coin_sin_sueno (the childhood's sleep, paired).
  EXILIO     (primary) H(T2) coin > coin_ninez (the sleep after the childhood, paired).
  VERDICT  PERSISTE_N and NINEZ, not EXILIO -> BASTA LA NINEZ (a precise frozen expert
           keeps the identity); PERSISTE_N and NINEZ and EXILIO -> LA NINEZ SOSTIENE, EL
           RESTO SUMA; PERSISTE_N without NINEZ -> PERSISTE SIN ATRIBUIR; no PERSISTE_N,
           EXILIO -> HACE FALTA SEGUIR DURMIENDO; otherwise -> INDETERMINADO.
  Secondary: ELIGE_N (§K7's ELIGE on coin_ninez at T2).
  Reported: H at T1/Tm/T2; home and abroad costs; stuck blocks; contexts, (h, e), the
  settled expert, NO CONFUNDE and latency; the probe of coin_ninez by role; the home
  oracle at the end of the childhood, at the first and at the last exile block (DANO =
  first exile block > end of the childhood; CONGELADO = last == first exile block within
  0.002), for the three arms.

PREDICTIONS (written before any test pair). Every childhood equals coin's (diff 0).
PERSISTE_N and NINEZ pass: the childhood's sleep makes the home expert precise (~0.005)
and without sleep it stays frozen through the exile. EXILIO passes too: the first exile
steps (before the snapshot) hit the home expert and nothing repairs them later, and the
T2 clone does not sleep. VERDICT: LA NINEZ SOSTIENE, EL RESTO SUMA. ELIGE_N passes (a
precise home expert is easy to tell from the exile's). DANO in most twins; CONGELADO in
most, as in §K8.

NOTE AFTER THE SMOKE TEST, BEFORE THE TEST (one short life, one pair: not evidence). The
childhoods equal §K7's (diff 0) and the whole lives differ (the sleep stops). At the
exile's start coin_ninez's home oracle jumps 0.003 -> 0.184 (coin_sin_sueno 0.087 ->
0.169, coin 0.003 -> 0.009): the precise expert looks MORE fragile to the first exile
steps. A possible reason, untested: Adam (the world model's optimizer) divides the step
by the recent gradient magnitude, small for a precise expert, so the first large errors
give large steps. If it repeats,
PERSISTE_N and ELIGE_N are at risk; the predictions above stand as written.

REPLICATION, pre-registered with the test: pairs 12-23 (reading the replication lives
of §K7 and §K8), the same rule, launched right after the test unless a bug is found
(any change recorded). REPLICADO if the verdict repeats.

RESULT (pairs 0-11, results/mundo_propio_ninez_run.txt, 31.1 min; every childhood equals
§K7's, max diff 0 over 24 lives). Pre-registered verdict: INDETERMINADO -- PERSISTE_N
9/12 (H(T2) +0.35, between coin +0.69 and coin_sin_sueno +0.06), NINEZ 8/12, EXILIO 8/12;
ELIGE_N 4/12. The smoke note held: DANO 23/24 -- the childhood's sleep leaves the home
expert precise (oracle 0.005, as coin's) and the first exile block takes it to 0.121
(coin_sin_sueno's coarse expert: 0.131), frozen afterwards (21/24); with sleep the damage
is repaired within the block (coin 0.005 -> 0.006). The first exile steps, before the
snapshot, take ANY home expert to ~0.12-0.13, precise or not: the question could not be
asked clean, because the expert that gets frozen is no longer the childhood's.

24 new lives per run; 3 CPU processes, one torch thread each (the declared kernel
exception). `reanudar` after any mode loads the lives already on disk.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_ninez.py replica   # pairs 12-23
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

spec = importlib.util.spec_from_file_location("mundo_propio_separacion", HERE / "exp_mundo_propio_separacion.py")
k8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k8)
k7, cr, co, g = k8.k7, k8.cr, k8.co, k8.g
NUEVO = "coin_ninez"
co.BRAZOS[NUEVO] = dict(co.BRAZOS["coin"])
k7.SUENO_SOLO_NINEZ.add(NUEVO)
k7.DATA = DATA = ROOT / "data" / "mundo_propio_ninez"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
BRAZOS = ("coin", NUEVO, "coin_sin_sueno")


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def cargar_k8(par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K8 coin_sin_sueno life, in the shape vivir() returns."""
    x = dict(np.load(k8.DATA / f"una_coin_sin_sueno_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida(("coin_sin_sueno", par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> dict:
    h = cr.humo(escala)
    tareas = [(NUEVO, p, gm, escala, "una", f"una_{NUEVO}_{p}_{gm}{h}", reanudar)
              for p in pares for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    V = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas}
    for p in pares:
        for gm in GEMELOS:
            V[("coin", p, gm)] = k8.cargar_k7(p, gm, escala)
            V[("coin_sin_sueno", p, gm)] = cargar_k8(p, gm, escala)
    return V


def ninez(x: dict, escala: dict) -> dict:
    """The part of a life before the exile: per-tick series, probes, the assays before
    it, the self_embedding there and the context events."""
    nb, nn, _ = escala["vida"]
    t0, j = (nb + nn) * D, [i for i, (_, b) in enumerate(escala["ensayos"]) if b <= nb + nn]
    out = {k: np.asarray(x[k])[:t0] for k in ("dist", "psi", "fe", "ctx")}
    out.update({k: np.asarray(x[k])[: nb + nn] for k in ("sonda", "oraculo")})
    out.update({k: np.asarray(x[k])[j] for k in ("ens_dist", "ens_fe", "ens_psi", "ens_ctx", "yo")})
    ev = np.asarray(x["eventos"]).reshape(-1, 3)
    out["eventos"] = ev[ev[:, 1] <= t0]
    return out


def veredicto(persiste: int, n_ninez: int, exilio: int) -> str:
    """The pre-registered §K9 rule."""
    p, n, e = (v >= N_OK for v in (persiste, n_ninez, exilio))
    if p and n:
        return "LA NINEZ SOSTIENE, EL RESTO SUMA" if e else "BASTA LA NINEZ"
    if p:
        return "PERSISTE SIN ATRIBUIR"
    return "HACE FALTA SEGUIR DURMIENDO" if e else "INDETERMINADO"


def oraculo_casa(V: dict, a: str, pares: tuple, escala: dict) -> np.ndarray:
    """(twins, blocks) home oracle."""
    return np.array([V[(a, p, gm)]["oraculo"][:, g.papeles(p)[gm]] for p in pares for gm in GEMELOS])


def informe(V: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2 = T[-1], len(T) - 1
    nb, nn, _ = escala["vida"]
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; new: {NUEVO} (coin, world-model sleep off from the exile on); "
        f"read: coin (§K7), coin_sin_sueno (§K8); run {minutos:.1f} min")
    dif = [cr.diferencia(ninez(V[(NUEVO, p, gm)], escala), ninez(V[("coin", p, gm)], escala))
           for p in pares for gm in GEMELOS]
    out(f"verification: every {NUEVO} childhood vs the stored §K7 coin life, max diff {max(dif)} "
        f"over {len(dif)} lives")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>14} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                        for t in T))
    out("costs (medians): home T1 | abroad T1 | home T2 | abroad T2 | first exile block | stuck blocks (twins)")
    for a in BRAZOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares]) for t in ("T1", t2) for f in (k8.casa, g.afuera)]
        out(f"  {a:>14} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
    out("experts")
    for a in BRAZOS:
        k8.expertos(V, a, pares, escala, out)
    k8.sonda(V, NUEVO, pares, escala, out)
    out("home oracle (median over twins): end of the childhood | first exile block | last | DANO | CONGELADO")
    for a in BRAZOS:
        o = oraculo_casa(V, a, pares, escala)
        b17, b18, bf = o[:, nb + nn - 1], o[:, nb + nn], o[:, -1]
        out(f"  {a:>14} | {np.median(b17):.3f} | {np.median(b18):.3f} | {np.median(bf):.3f} | "
            f"{(b18 > b17).sum()}/{2 * n} | {(np.abs(bf - b18) < 0.002).sum()}/{2 * n}")
    out("")
    out("-" * 80)
    mayor = lambda a, b: sum(x > y for x, y in zip(H[(a, t2)], H[(b, t2)]))  # noqa: E731
    persiste = sum(v > 0 for v in H[(NUEVO, t2)])
    n_ninez = mayor(NUEVO, "coin_sin_sueno")
    exilio = mayor("coin", NUEVO)
    out(f"PERSISTE_N H({t2}) {NUEVO} > 0: {persiste}/{n}")
    out(f"NINEZ H({t2}) {NUEVO} > coin_sin_sueno: {n_ninez}/{n}")
    out(f"EXILIO H({t2}) coin > {NUEVO}: {exilio}/{n}")
    out(f"(secondary) ELIGE_N at {t2}: {sum(k7.elige(V, p, j2, NUEVO) for p in pares)}/{n}")
    if n == len(g.PAIRS):
        out(f"VERDICT (pre-registered rule): {veredicto(persiste, n_ninez, exilio)}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    V = correr(pares, escala, reanudar)
    if escala == g.HUMO:
        d = cr.diferencia(V[(NUEVO, pares[0], "A")], V[("coin", pares[0], "A")])
        print(f"whole life {NUEVO} vs coin, twin A: max diff {d} (must be > 0: the sleep stops)")
    informe(V, pares, escala, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_ninez_humo", "§K9 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_ninez_replica",
             "§K9 REPLICATION (pairs 12-23) -- the sleep of the childhood", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_ninez", "§K9 -- the sleep of the childhood", reanudar)
