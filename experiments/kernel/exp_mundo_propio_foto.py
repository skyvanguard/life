"""
§K10 -- THE SNAPSHOT IN TIME: with the home expert restored to weights from BEFORE the
exile, is a precise frozen expert enough to keep the identity?
(docs/MUNDO_PROPIO.md; written 2026-10-27, before any test pair; no calibration)

WHY. §K9 could not ask its question clean: the childhood's sleep leaves the home expert
precise (oracle 0.005), but the contextual model's running error is an EMA that crosses
the threshold 4-24 ticks after the exile begins, so the "pre-streak" snapshot already
holds the first exile steps; restored at the spawn, the home expert lands at the
never-slept level (0.110-0.121; 46/48 twins) and freezes there. In coin the exile's
sleep repairs that damage within the block. Pooled, sleeping only in the childhood did
not hold the identity (EXILIO 19/24) -- but the expert that got frozen was not the
childhood's.

DESIGN. ContextualWorldModel(snapshot_lag=L) (tested in tests/test_contextual_world_model.py):
the active expert is checkpointed at the end of every sleep and every L ticks without
one, and the snapshot is the latest checkpoint at least L ticks old at the crossing.
L = 50, above the largest crossing lag measured in §K8 (24 ticks); in a sleeping kernel
(a sleep every 50 ticks) it restores the expert as it was right after the last sleep
at least 50 ticks before the crossing. Two new arms, under §K7's "una" with §K4's life, roles, exile and assays:
  coin_ninez_foto      coin_ninez (§K9: world-model sleep off from the exile on) + L
  coin_sin_sueno_foto  coin_sin_sueno (§K8: never sleeps) + L
Read: coin (§K7), coin_ninez (§K9), coin_sin_sueno (§K8). The lag only acts at a
restore, so a life with no restore before the exile must have the childhood of its
reference arm (coin for coin_ninez_foto, coin_sin_sueno for coin_sin_sueno_foto): its
per-tick series, probes, self_embedding at T1 and context events up to the exile are
compared (max diff 0). The assays are not: an assay clone restores too (a clone that
spawns in its sibling's home), so T1 may differ. The loop now also logs every restore
(tick, tick of the snapshot); it is only a log.

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019):
  FOTO A TIEMPO (manipulation check) in coin_ninez_foto, the restore at the exile's
           spawn uses weights from before the exile in >= 20/24 twins; if not -> NO SE
           PUDO HACER (the experiment did not test what it meant to).
  PERSISTE_F (primary) H(T2) coin_ninez_foto > 0.
  NINEZ_F    (primary) H(T2) coin_ninez_foto > coin_sin_sueno_foto (the childhood's
           sleep, both with the snapshot in time).
  RESTO_F    (primary) H(T2) coin > coin_ninez_foto (the sleep after the childhood:
           the exile's and the Tm/T2 assays').
  VERDICT  PERSISTE_F and NINEZ_F, not RESTO_F -> BASTA LA NINEZ; PERSISTE_F and NINEZ_F
           and RESTO_F -> LA NINEZ SOSTIENE, EL RESTO SUMA; PERSISTE_F without NINEZ_F ->
           PERSISTE SIN ATRIBUIR; no PERSISTE_F, RESTO_F -> HACE FALTA SEGUIR DURMIENDO;
           otherwise -> INDETERMINADO.
  Secondary: REPARA_F (H(T2) coin_ninez_foto > coin_ninez, the snapshot helps);
  PERSISTE_SSF (H(T2) coin_sin_sueno_foto > 0); ELIGE_F (§K7's ELIGE on coin_ninez_foto
  at T2); FOTO A TIEMPO on coin_sin_sueno_foto.
  Reported: H at T1/Tm/T2; home and abroad costs; stuck blocks; contexts, (h, e), the
  settled expert, NO CONFUNDE and latency; the home oracle at the end of the childhood,
  the first and the last exile block (DANO, CONGELADO) for every arm; the age of the
  restored snapshot at the exile's spawn.

AMENDED AFTER THE FIRST SMOKE TEST, BEFORE ANY TEST PAIR. The first version checkpointed
every L ticks inside the model's tick, i.e. BEFORE that tick's sleep; in the smoke test
coin_ninez_foto's restored home expert came back at 0.086, the never-slept level. The
reason, measured (exp_mundo_propio_entre_suenos.py, re-running coin pair 0 twin A and
probing the home world with the active expert at every tick, after its online step and
before its sleep): the slept expert is precise only right after each sleep. Over the
last 150 childhood ticks it reads 0.004-0.006 right after a sleep, median 0.012, mean
0.046, above 0.05 in 44/151 ticks, up to 0.215 (online learning between two sleeps
erodes what the sleep consolidated, sometimes from 0.004 to 0.2 in ~25 ticks). The
block-end probes of every experiment so far are taken right after a sleep (block ends
fall on dream ticks), so the "0.005" of §K7-§K9 is the just-slept state. The rule was
changed to checkpoint after each sleep; in the second smoke test the restored home
expert stays at 0.003-0.004 through the exile.

PREDICTIONS (written before any test pair; they stand after the amendment). FOTO A TIEMPO 24/24 in both arms. DANO
disappears in coin_ninez_foto: its home oracle at the first exile block stays near the
end of the childhood (0.005-0.01) and freezes there. PERSISTE_F and NINEZ_F pass,
RESTO_F fails: VERDICT BASTA LA NINEZ. REPARA_F and ELIGE_F pass. coin_sin_sueno_foto
keeps its coarse home expert intact (~0.087); PERSISTE_SSF uncertain.

REPLICATION, pre-registered with the test: pairs 12-23 (reading the replication lives
of §K7, §K8 and §K9), the same rule, launched right after the test unless a bug is
found (any change recorded). REPLICADO if the verdict repeats.

RESULT (pairs 0-11, results/mundo_propio_foto_run.txt, 42.4 min; childhoods without a
restore before the exile equal their reference, diff 0, 21/24 and 20/24 lives). The
manipulation works: FOTO A TIEMPO 22/24 (coin_sin_sueno_foto 24/24); coin_ninez_foto's
home oracle stays at 0.005 through the exile (CONGELADO 22/24), the §K9 damage is gone.
Pre-registered verdict: BASTA LA NINEZ -- PERSISTE_F 12/12 (H(T2) +1.02; coin +0.69),
NINEZ_F 10/12 (at the threshold), RESTO_F 5/12; REPARA_F 12/12, ELIGE_F 8/12. Surprise:
coin_sin_sueno_foto (never sleeps) PERSISTS 10/12 (+0.43) and CHOOSES 12/12 (24/24 twins
settle on h at T2) -- §K8's POR EL SUENO was obtained with the lagged snapshot. Part of
coin_ninez_foto's larger H is a worse abroad cost (0.707 vs coin 0.489: its Tm/T2
clones do not sleep); home at T2 it is as good as coin (0.138 vs 0.146).

REPLICATION RESULT (pairs 12-23, results/mundo_propio_foto_replica_run.txt, 52.8 min;
childhoods without a restore equal their reference, diff 0). REPLICADO: BASTA LA NINEZ
again -- FOTO A TIEMPO 21/24, PERSISTE_F 11/12, NINEZ_F 10/12, RESTO_F 7/12; ELIGE_F
10/12, PERSISTE_SSF 9/12. Pooled 24: PERSISTE_F 23/24, NINEZ_F 20/24, RESTO_F 12/24,
ELIGE_F 18/24; the never-sleeping coin_sin_sueno_foto PERSISTS 19/24 and CHOOSES 22/24
(§K8 with the lagged snapshot: 14/24 and 12/24). A precise frozen childhood expert
holds the identity; with the snapshot in time the separation alone holds it too,
weaker, and the childhood's sleep adds; sleeping after the childhood is not needed.
The test's "worse abroad" did not repeat (abroad at T2 0.522 vs coin 0.611).

48 new lives per run; 3 CPU processes, one torch thread each (the declared kernel
exception; the GPU is slower for this batch-1 loop, measured 2026-10-27). `reanudar`
after any mode loads the lives already on disk.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_foto.py replica   # pairs 12-23
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

spec = importlib.util.spec_from_file_location("mundo_propio_ninez", HERE / "exp_mundo_propio_ninez.py")
k9 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k9)
k8, k7, cr, co, g = k9.k8, k9.k7, k9.cr, k9.co, k9.g
LAG = 50
NUEVOS = {"coin_ninez_foto": "coin_ninez", "coin_sin_sueno_foto": "coin_sin_sueno"}
for nuevo, base in NUEVOS.items():
    co.BRAZOS[nuevo] = {**co.BRAZOS[base], "wm_context_kwargs": {"snapshot_lag": LAG}}
k7.SUENO_SOLO_NINEZ.add("coin_ninez_foto")
k7.DATA = DATA = ROOT / "data" / "mundo_propio_foto"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
BRAZOS = ("coin", "coin_ninez", "coin_ninez_foto", "coin_sin_sueno", "coin_sin_sueno_foto")


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def guardada(a: str, par: int, gemelo: str, escala: dict) -> dict:
    """A stored life of a read arm: coin (§K7), coin_ninez (§K9), coin_sin_sueno (§K8)."""
    if a == "coin":
        return k8.cargar_k7(par, gemelo, escala)
    if a == "coin_sin_sueno":
        return k9.cargar_k8(par, gemelo, escala)
    x = dict(np.load(k9.DATA / f"una_{a}_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida((a, par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> dict:
    h = cr.humo(escala)
    tareas = [(a, p, gm, escala, "una", f"una_{a}_{p}_{gm}{h}", reanudar)
              for a in NUEVOS for p in pares for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    V = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas}
    for p in pares:
        for gm in GEMELOS:
            for a in ("coin", "coin_ninez", "coin_sin_sueno"):
                V[(a, p, gm)] = guardada(a, p, gm, escala)
    return V


def ninez(x: dict, escala: dict) -> dict:
    """The main life before the exile, without the assays: per-tick series, probes, the
    self_embedding at the assays before the exile and the context events."""
    nb, nn, _ = escala["vida"]
    t0, j = (nb + nn) * D, [i for i, (_, b) in enumerate(escala["ensayos"]) if b <= nb + nn]
    out = {k: np.asarray(x[k])[:t0] for k in ("dist", "psi", "fe", "ctx")}
    out.update({k: np.asarray(x[k])[: nb + nn] for k in ("sonda", "oraculo")})
    out["yo"] = np.asarray(x["yo"])[j]
    ev = np.asarray(x["eventos"]).reshape(-1, 3)
    out["eventos"] = ev[ev[:, 1] <= t0]
    return out


def foto_exilio(x: dict, escala: dict) -> tuple[int | None, int | None]:
    """(tick of the first restore at or after the exile's start, tick of its snapshot)."""
    nb, nn, _ = escala["vida"]
    t0 = (nb + nn) * D
    r = np.asarray(x["restauraciones"]).reshape(-1, 2)
    r = r[r[:, 0] >= t0]
    return (int(r[0, 0]), int(r[0, 1])) if len(r) else (None, None)


def informe(V: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2 = T[-1], len(T) - 1
    nb, nn, _ = escala["vida"]
    t0 = (nb + nn) * D
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; new: {list(NUEVOS)} (snapshot_lag {LAG}); read: coin (§K7), "
        f"coin_ninez (§K9), coin_sin_sueno (§K8); run {minutos:.1f} min")
    for nuevo, base in NUEVOS.items():
        sin, difs = 0, []
        for p in pares:
            for gm in GEMELOS:
                x = V[(nuevo, p, gm)]
                r = np.asarray(x["restauraciones"]).reshape(-1, 2)
                if (r[:, 0] < t0).any():
                    sin += 1
                    continue
                difs.append(cr.diferencia(ninez(x, escala), ninez(V[(base, p, gm)], escala)))
        out(f"verification: {nuevo} childhood vs {base}, max diff {max(difs) if difs else float('nan')} over "
            f"{len(difs)} lives with no restore before the exile ({sin} had one: they may differ)")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>19} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                         for t in T))
    out("costs (medians): home T1 | abroad T1 | home T2 | abroad T2 | first exile block | stuck blocks (twins)")
    for a in BRAZOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares]) for t in ("T1", t2) for f in (k8.casa, g.afuera)]
        out(f"  {a:>19} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
    out("experts")
    for a in NUEVOS:
        k8.expertos(V, a, pares, escala, out)
    out("the restore at the exile's spawn (new arms): before the exile | median age of the snapshot (ticks)")
    a_tiempo = {}
    for a in NUEVOS:
        fx = [foto_exilio(V[(a, p, gm)], escala) for p in pares for gm in GEMELOS]
        a_tiempo[a] = sum(f is not None and f < t0 for _, f in fx)
        edades = [r - f for r, f in fx if r is not None]
        out(f"  {a:>19} | {a_tiempo[a]}/{2 * n} | {np.median(edades) if edades else float('nan'):.0f} "
            f"(no exile restore in {sum(r is None for r, _ in fx)})")
    out("home oracle (median over twins): end of the childhood | first exile block | last | DANO | CONGELADO")
    for a in BRAZOS:
        o = k9.oraculo_casa(V, a, pares, escala)
        b17, b18, bf = o[:, nb + nn - 1], o[:, nb + nn], o[:, -1]
        out(f"  {a:>19} | {np.median(b17):.3f} | {np.median(b18):.3f} | {np.median(bf):.3f} | "
            f"{(b18 > b17).sum()}/{2 * n} | {(np.abs(bf - b18) < 0.002).sum()}/{2 * n}")
    out("")
    out("-" * 80)
    mayor = lambda a, b: sum(x > y for x, y in zip(H[(a, t2)], H[(b, t2)]))  # noqa: E731
    persiste = sum(v > 0 for v in H[("coin_ninez_foto", t2)])
    n_ninez = mayor("coin_ninez_foto", "coin_sin_sueno_foto")
    resto = mayor("coin", "coin_ninez_foto")
    out(f"FOTO A TIEMPO coin_ninez_foto: {a_tiempo['coin_ninez_foto']}/{2 * n} twins (needs >= 20/24)")
    out(f"PERSISTE_F H({t2}) coin_ninez_foto > 0: {persiste}/{n}")
    out(f"NINEZ_F H({t2}) coin_ninez_foto > coin_sin_sueno_foto: {n_ninez}/{n}")
    out(f"RESTO_F H({t2}) coin > coin_ninez_foto: {resto}/{n}")
    out(f"(secondary) REPARA_F H({t2}) coin_ninez_foto > coin_ninez: {mayor('coin_ninez_foto', 'coin_ninez')}/{n} | "
        f"PERSISTE_SSF: {sum(v > 0 for v in H[('coin_sin_sueno_foto', t2)])}/{n} | ELIGE_F: "
        f"{sum(k7.elige(V, p, j2, 'coin_ninez_foto') for p in pares)}/{n} | FOTO A TIEMPO coin_sin_sueno_foto: "
        f"{a_tiempo['coin_sin_sueno_foto']}/{2 * n}")
    if n == len(g.PAIRS):
        if a_tiempo["coin_ninez_foto"] < 20:
            v = "NO SE PUDO HACER"
        else:
            v = k9.veredicto(persiste, n_ninez, resto)
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
        main((0,), g.HUMO, "mundo_propio_foto_humo", "§K10 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_foto_replica",
             "§K10 REPLICATION (pairs 12-23) -- the snapshot in time", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_foto", "§K10 -- the snapshot in time", reanudar)
