"""
§K8 -- SLEEP OR SEPARATION: where does the repertoire's identity come from?
(docs/MUNDO_PROPIO.md; written 2026-10-27, before the calibration below; pre-registered
after it, before the test)

WHY. §K4: the identity of twins raised in different worlds is BY SLEEP -- the
kernel without sleep keeps it at chance (15/24), the paired contrast 23/24. §K7: a
kernel with a repertoire (coin = error_x4 + wm_contexts=6) keeps it too (PERSISTE
24/24) and the identity becomes WHICH EXPERT IT GOES BACK TO (ELIGE 22/24); but
there was no coin without sleep, so §K7 cannot say whether that identity is still
the sleep's, or whether separating the exile into its own expert is enough: the home
expert is restored and stops learning while inactive, with or without sleep.

DESIGN. A 2 x 2 over sleep x separation, all under §K7's "una" (home only):
  coin            sleep, experts        READ from §K7 (data/mundo_propio_casas)
  error_x4        sleep, one model      READ from §K4 (data/mundo_propio_gemelos)
  coin_sin_sueno  no sleep, experts     NEW: coin with wm_sleep_replay = 0
  error_sin_sueno no sleep, one model   NEW: error_x4 with wm_sleep_replay = 0
plus kernel (§K4's arm: no sleep, no error input) read as a reference. The two new
arms differ from the read ones ONLY in the world model's sleep replay (the kernel's
DreamEngine sleep, which never touches the world model, runs in every arm). The
life, the roles, the exile and the assays are §K4's; the loop is §K7's vivir
(exp_mundo_propio_casas.vivir: the active expert per tick and per assay tick, the
context events, the context probe), re-run on coin (first pair, twin A) and required
to reproduce the stored §K7 life exactly (max diff 0). Declared: "dos" is not run;
error_sin_sueno has one world model, so its "expert" readouts are trivial (h = e = 0).

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019):
  SE DIFERENCIA (positive control) H(T1) coin_sin_sueno > 0.
  PERSISTE_SS (primary) H(T2) coin_sin_sueno > 0.
  SEPARA      (primary) H(T2) coin_sin_sueno > error_sin_sueno (separation, paired).
  SUENO       (primary) H(T2) coin > coin_sin_sueno (sleep, paired).
  VERDICT  SE DIFERENCIA fails -> NO SE DIFERENCIA; else
           PERSISTE_SS and SEPARA, not SUENO -> POR LA SEPARACION;
           PERSISTE_SS and SEPARA and SUENO   -> SEPARACION Y SUENO;
           PERSISTE_SS without SEPARA         -> PERSISTE SIN SUENO, SIN ATRIBUIR;
           no PERSISTE_SS, SUENO              -> POR EL SUENO;
           otherwise                          -> INDETERMINADO.
  Secondary: ELIGE_SS (§K7's ELIGE on coin_sin_sueno at T2); EXILIO_SS (the first
  exile block's e_early, coin_sin_sueno < error_sin_sueno); the §K4 readout on the
  new single arm (PERSISTE of error_sin_sueno); ERROR_SS (added after the calibration,
  before the test): H(T2) error_sin_sueno > kernel, paired -- without sleep, does
  seeing its own error give the single model an identity?
  Reported: H at T1/Tm/T2 for every arm; home and abroad costs at T1 and T2; stuck
  blocks; contexts in use, (h, e), settled expert, NO CONFUNDE and latency for both
  coin arms; the probe of coin_sin_sueno by role.

PREDICTIONS (written before the calibration). SE DIFERENCIA 12/12 (§K4's kernel
without sleep differed at T1 12/12). PERSISTE_SS and SEPARA pass, SUENO fails:
VERDICT POR LA SEPARACION. The reason: in the contextual model only the ACTIVE
expert learns, and at the exile's spawn the home expert is restored to its weights
before the streak, so the childhood is protected without any replay; the single
sleepless model overwrites it in the exile (§K4: 15/24). ELIGE_SS passes. Risk: the
sleepless online learner's running error may hover near the absolute threshold
(0.08) and open spurious contexts, which would break ELIGE_SS (§K7's two misses had a
third expert). PERSISTE of error_sin_sueno at chance, like §K4's kernel.

CALIBRATION (`calibracion`, pairs 100-102, never test pairs;
results/mundo_propio_separacion_calibracion_run.txt; 9.3 min). Nothing was tuned.
Verification max diff 0. coin_sin_sueno: H(T1) +0.88, H(T2) +0.51 (3/3 both), ELIGE
3/3 (latency 29 ticks at T2; coin 10), 2 contexts in 5/6 twins and 3 in 1/6; its home
probe 0.077-0.091 vs coin's 0.005 (without sleep the home expert stays coarse). Home
cost at T2: coin 0.143, coin_sin_sueno 0.279, error_sin_sueno 0.475, kernel 0.507.
SUENO 3/3 (+1.09 vs +0.51), SEPARA 2/3. Surprise: error_sin_sueno persists 3/3 (+0.33)
where kernel gives -0.51 on the same pairs; the only difference is the error input.
PREDICTIONS added after the calibration, before the test pairs: SE DIFERENCIA and
PERSISTE_SS pass; SUENO passes (the written prediction, fails, stands); SEPARA
uncertain (the single sleepless model persists too); so SEPARACION Y SUENO if SEPARA
passes, else PERSISTE SIN SUENO, SIN ATRIBUIR; ELIGE_SS and EXILIO_SS pass; PERSISTE of
error_sin_sueno uncertain (the written 'at chance' stands); ERROR_SS uncertain
(3/3 on the calibration, read after adding it by reloading the lives).

REPLICATION, pre-registered with the test: pairs 12-23 (the replication lives of
§K4 and §K7 are read), the same rule, launched right after the test unless a bug is
found (any change recorded). REPLICADO if the verdict repeats.

48 new lives + 1 verification life per run; 3 CPU processes, one torch thread each
(the declared kernel exception). `reanudar` after any mode loads the lives already
on disk instead of re-running them.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py calibracion
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion.py replica   # pairs 12-23
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


def _cargar_modulo(nombre: str, archivo: str):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


k7 = _cargar_modulo("mundo_propio_casas", "exp_mundo_propio_casas.py")
cr, co, g = k7.cr, k7.co, k7.g
NUEVOS = ("coin_sin_sueno", "error_sin_sueno")
co.BRAZOS["coin_sin_sueno"] = {**co.BRAZOS["coin"], "wm_sleep_replay": 0}
co.BRAZOS["error_sin_sueno"] = {**co.BRAZOS["error_x4"], "wm_sleep_replay": 0}
DATA_K7 = k7.DATA
k7.DATA = DATA = ROOT / "data" / "mundo_propio_separacion"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
EXPERTOS = ("coin", "coin_sin_sueno")
TODOS = ("coin", "coin_sin_sueno", "error_x4", "error_sin_sueno", "kernel")


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def tareas(pares: tuple, escala: dict, reanudar: bool) -> list[tuple]:
    h = cr.humo(escala)
    t = [("coin", pares[0], "A", escala, "una", f"verif_coin_{pares[0]}_A{h}", reanudar)]
    return t + [(a, p, gm, escala, "una", f"una_{a}_{p}_{gm}{h}", reanudar)
                for a in NUEVOS for p in pares for gm in GEMELOS]


def cargar_k7(par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K7 coin life ('una'), in the shape vivir() returns."""
    x = dict(np.load(DATA_K7 / f"una_coin_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida(("coin", par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> tuple[dict, dict]:
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas(pares, escala, reanudar)))
    V = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas[1:]}
    for p in pares:
        for gm in GEMELOS:
            V[("coin", p, gm)] = cargar_k7(p, gm, escala)
            for a in ("error_x4", "kernel"):
                V[(a, p, gm)] = k7.cargar(a, p, gm, "una", escala)
    return V, vidas[0]


def casa(V: dict, brazo: str, par: int, T: str) -> float:
    """Home cost: e_early of each twin in its own world, mean of the twins."""
    m = g.leer(V, brazo, par, T, "early")
    return float((m[0, 0] + m[1, 1]) / 2)


def veredicto(sd: int, persiste: int, separa: int, sueno: int) -> str:
    """The pre-registered §K8 rule."""
    if sd < N_OK:
        return "NO SE DIFERENCIA"
    p, s, z = persiste >= N_OK, separa >= N_OK, sueno >= N_OK
    if p and s:
        return "SEPARACION Y SUENO" if z else "POR LA SEPARACION"
    if p:
        return "PERSISTE SIN SUENO, SIN ATRIBUIR"
    return "POR EL SUENO" if z else "INDETERMINADO"


def expertos(V: dict, a: str, pares: tuple, escala: dict, out) -> None:
    n = len(pares)
    usos = [1 + int((V[(a, p, gm)]["eventos"][:, 0] == co.EVENTO["spawn"]).sum())
            for p in pares for gm in GEMELOS]
    he = [k7.casa_exilio(V[(a, p, gm)], p) for p in pares for gm in GEMELOS]
    out(f"  {a}: in use {usos}")
    out(f"  {a}: (h, e) {he}; e != h in {sum(e != h for h, e in he)}/{2 * n} twins")
    for j, (t, b) in enumerate(escala["ensayos"]):
        if b == 0:
            continue
        en_h = sum(k7.asentado(V[(a, p, gm)], j, i) == k7.casa_exilio(V[(a, p, gm)], p)[0]
                   for p in pares for i, gm in enumerate(GEMELOS))
        lat = [k7.latencia(V[(a, p, gm)], p, j, i) for p in pares for i, gm in enumerate(GEMELOS)]
        out(f"  {a} {t:>3}: settled at home on h {en_h}/{2 * n} twins; ELIGE pairs "
            f"{sum(k7.elige(V, p, j, a) for p in pares)}/{n}; NO CONFUNDE pairs "
            f"{sum(not k7.confunde(V, p, j, a) for p in pares)}/{n}; latency to h at home "
            f"median {np.median(lat):.0f} ticks")


def sonda(V: dict, a: str, pares: tuple, escala: dict, out) -> None:
    out(f"  {a} probe (median over twins and pairs): home | sibling | X")
    for j, (t, b) in enumerate(escala["ensayos"]):
        if b == 0:
            continue
        cel = []
        for rol in ("home", "sibling", "X"):
            vals = []
            for p in pares:
                pa = g.papeles(p)
                for gm, otro in (("A", "B"), ("B", "A")):
                    x = V[(a, p, gm)]
                    vals.append(x["sonda"][x["bloque"][j] - 1, pa[{"home": gm, "sibling": otro, "X": "X"}[rol]]])
            cel.append(f"{np.median(vals):.3f}")
        out(f"   {t:>3} | " + " | ".join(cel))


def informe(V: dict, pares: tuple, escala: dict, nombre: str, titulo: str,
            minutos: float, verif: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2 = T[-1]
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, 'una'; new: {list(NUEVOS)} (wm_sleep_replay = 0); read: coin (§K7), "
        f"error_x4 and kernel (§K4); run {minutos:.1f} min")
    out(f"verification: the loop re-run on coin pair {pares[0]} twin A vs the stored §K7 life, max diff {verif}")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in TODOS for t in T}
    for a in TODOS:
        out(f"  {a:>15} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                         for t in T))
    out("costs (medians): home T1 | abroad T1 | home T2 | abroad T2 | first exile block | stuck blocks (twins)")
    for a in TODOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares]) for t in ("T1", t2) for f in (casa, g.afuera)]
        out(f"  {a:>15} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
    out("experts")
    for a in EXPERTOS:
        expertos(V, a, pares, escala, out)
    sonda(V, "coin_sin_sueno", pares, escala, out)
    rec = [g.cruce(g.leer(V, "coin_sin_sueno", p, t2, "fe")) for p in pares]
    out(f"  (reported) RECONOCE coin_sin_sueno (free-energy cross at {t2} > 0): {sum(v > 0 for v in rec)}/{n}")
    out("")
    out("-" * 80)
    mayor = lambda a, b, t: sum(x > y for x, y in zip(H[(a, t)], H[(b, t)]))  # noqa: E731
    sd = sum(v > 0 for v in H[("coin_sin_sueno", "T1")])
    persiste = sum(v > 0 for v in H[("coin_sin_sueno", t2)])
    separa = mayor("coin_sin_sueno", "error_sin_sueno", t2)
    sueno = mayor("coin", "coin_sin_sueno", t2)
    j2 = len(T) - 1
    ex = {a: [cr.exilio(V, a, p) for p in pares] for a in NUEVOS}
    out(f"SE DIFERENCIA H(T1) coin_sin_sueno > 0: {sd}/{n}")
    out(f"PERSISTE_SS H({t2}) coin_sin_sueno > 0: {persiste}/{n}")
    out(f"SEPARA H({t2}) coin_sin_sueno > error_sin_sueno: {separa}/{n}")
    out(f"SUENO H({t2}) coin > coin_sin_sueno: {sueno}/{n}")
    out(f"(secondary) ELIGE_SS at {t2}: {sum(k7.elige(V, p, j2, 'coin_sin_sueno') for p in pares)}/{n} | "
        f"EXILIO_SS first exile block coin_sin_sueno < error_sin_sueno: "
        f"{sum(x < y for x, y in zip(ex['coin_sin_sueno'], ex['error_sin_sueno']))}/{n} | "
        f"PERSISTE error_sin_sueno: {sum(v > 0 for v in H[('error_sin_sueno', t2)])}/{n}")
    out(f"(secondary, added after the calibration) ERROR_SS H({t2}) error_sin_sueno > kernel: "
        f"{mayor('error_sin_sueno', 'kernel', t2)}/{n}")
    out(f"(reported) the sleep with one model, H({t2}) error_x4 > error_sin_sueno: "
        f"{mayor('error_x4', 'error_sin_sueno', t2)}/{n}")
    if n == len(g.PAIRS):
        out(f"VERDICT (pre-registered rule): {veredicto(sd, persiste, separa, sueno)}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    V, x0 = correr(pares, escala, reanudar)
    verif = cr.diferencia(x0, cargar_k7(pares[0], "A", escala))
    if escala == g.HUMO:
        a, b = (V[("coin_sin_sueno", pares[0], gm)]["ens_dist"][0] for gm in GEMELOS)
        print(f"newborn coin_sin_sueno twins: identical T0 assays {np.array_equal(a, b)} (must be True)")
    informe(V, pares, escala, nombre, titulo, (time.time() - t0) / 60, verif)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_separacion_humo", "§K8 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "calibracion":
        main(g.PAIRS_CAL, g.ESCALA, "mundo_propio_separacion_calibracion",
             "§K8 CALIBRATION (pairs 100-102) -- sleep or separation", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_separacion_replica",
             "§K8 REPLICATION (pairs 12-23) -- sleep or separation", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_separacion", "§K8 -- sleep or separation", reanudar)
