"""
§K12 mechanism (post hoc, after the test and the replication; docs/MUNDO_PROPIO.md):
why the return home after the exile costs coin_madurez more than coin (VUELVE 7/24).

From the stored lives: at the T2 home assay coin_madurez switches back to its home expert
h sooner than coin (median 9 vs 12 ticks) and pays less before the switch (0.054 vs
0.082), but more AFTER it (0.114 vs 0.064; ticks 20-40 0.180 vs 0.070; 21/24 pairs);
coin_vigilia pays 0.034 there. The best home expert is intact at the end of the exile in
all three arms (home oracle 0.006-0.007).

Hypothesis (written before running): every expert in use predicts every tick, so h's
running error comes home carrying the exile, and the switch is relative (margin), not by
the threshold. The re-activated h therefore does not yet "explain" its stream and learns
awake at the full rate during the recovery. That alone does not say why coin, which
always learns at the full rate, pays less.

Re-run 16 lives (coin and coin_madurez, pairs 0-3, both twins); each must reproduce its
stored life (diff 0). At the Tm and T2 home assays, extra clones start from the same state
with the same seed (torch, numpy and random states saved and restored: the life is not
touched):
- instr: the assay loop with per-tick reads (active expert, running errors, whether h
  explains). It must reproduce the stored assay (diff 0).
- sonda: instr plus h's own error on the home probe at fixed ticks (read-only, checked
  against instr).
- lento_h: h learns awake at lr x 0.1 through the assay; every other expert keeps its rule.
- congelado_h: h does not learn awake (lr x 0); it still sleeps.
Both also read h's home-probe error (read-only, as in sonda).
Predictions: at the T2 switch r_h > threshold in most twins of both arms; lento_h and
congelado_h lower coin_madurez's cost after the switch toward coin_vigilia's.

Amended after the smoke, before the run: the first lento_h / congelado_h overrode
`_explica` for every expert, which also put coin_madurez's exile expert at the full rate
from the first tick home (the smoke caught it: the Tm switch moved from 33 to 15 ticks).
Now only h's awake rate changes (`fijar_h`); every other expert keeps its arm's rule.

RESULT (2026-10-28, results/mundo_propio_madurez_vuelta_run.txt, 47.7 min; every re-run
life diff 0.0, instr vs the stored assay 0.0, sonda vs instr 0.0). Both predictions held.
At the T2 switch r_h > threshold in 6/8 (coin) and 7/8 (coin_madurez) twins. The home
expert comes back intact and is DAMAGED by its own awake relearning: its home-probe
error goes 0.007 -> 0.157 (tick 20) -> 0.230 (tick 40) in coin_madurez and 0.008 ->
0.090 in coin, until the sleep at tick 50 repairs it (0.010). lento_h keeps it at
0.017, congelado_h at 0.007, and both remove the excess: coin_madurez's cost after the
switch 0.083 -> 0.055 (7/8 and 6/8 twins), below coin's 0.058. Freezing h also helps
coin (7/8). The excess concentrates in half the coin_madurez twins (after-switch
0.10-0.35); in three of them h spends 43-92 straight ticks not explaining (coin <= 12).
Only the first stretch was measured, not relapses. Why the damage is larger than coin's
at the same full rate was not tested.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez_vuelta.py humo   # pair 0, short life
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_madurez_vuelta.py
"""

from __future__ import annotations

import importlib.util
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("mundo_propio_madurez", HERE / "exp_mundo_propio_madurez.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
g, k7, cr, co = m.g, m.k7, m.cr, m.co
mp, ms = g.mp, g.ms
assert k7.g is g

from zeta_life.kernel.contextual_world_model import ContextualWorldModel  # noqa: E402

D = g.D
EARLY = mp.EARLY
BRAZOS = ("coin", m.NUEVO)
ENSAYOS = ("Tm", "T2")
MODOS = ("instr", "sonda", "lento_h", "congelado_h")
LARGO = 150
TICKS_SONDA = (0, 5, 10, 15, 20, 30, 40, 50, 70, 100)
CTX: dict = {}
EXTRA: dict = {}
_ensayo = g.ensayo


def fijar_h(wm, h: int, escala: float) -> None:
    """Expert h learns awake at lr x escala; every other expert keeps its arm's rule."""
    original = wm._despierto

    @contextmanager
    def despierto(c: int):
        if c != h:
            with original(c):
                yield
            return
        grupos = wm.experts[h].optimizer.param_groups
        base = [gr["lr"] for gr in grupos]
        for gr, lr in zip(grupos, base):
            gr["lr"] = lr * escala
        try:
            yield
        finally:
            for gr, lr in zip(grupos, base):
                gr["lr"] = lr

    wm._despierto = despierto


def visita(k, s, mundo: int, semilla: int, h: int, modo: str, largo: int) -> dict:
    """g.ensayo's loop on a clone, with per-tick reads; lento_h / congelado_h change only h's
    awake rate. `explica` is whether h explains by the arm's rule (ContextualWorldModel._explica)."""
    import torch
    estado = torch.get_rng_state()
    c, s = g.clonar(k), s.clone()
    wm = c.world_model
    if modo in ("lento_h", "congelado_h"):
        fijar_h(wm, h, 0.1 if modo == "lento_h" else 0.0)
    torch.manual_seed(semilla)
    pref = torch.tensor(mp.C)
    sonda = ms.sondas()[mundo]
    dist, err_h = np.empty(largo), np.full(largo, np.nan)
    activo, explica = np.zeros(largo, dtype=np.int8), np.zeros(largo, dtype=bool)
    run = np.full((largo, wm.n_contexts), np.nan)
    for t in range(largo):
        if modo != "instr" and t in TICKS_SONDA:
            err_h[t] = float(co.errores_sonda(wm.experts[h], *sonda)[ms.QUEMA:].mean())
        explica[t] = ContextualWorldModel._explica(wm, h)
        r = c.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        activo[t] = wm.active
        run[t, : wm.in_use] = [np.nan if v is None else v for v in wm.running[: wm.in_use]]
        s = ms.mover(s, r.action.detach(), mundo)
    torch.set_rng_state(estado)
    return {"dist": dist, "activo": activo, "explica": explica, "run": run, "err_h": err_h,
            "umbral": wm.threshold}


def ensayo(k, s, mundo: int, semilla: int) -> dict:
    """The life's assay, unchanged; at the Tm / T2 home assay, the extra clones."""
    x = _ensayo(k, s, mundo, semilla)
    p = CTX.get("par")
    if p is None or mundo != CTX["casa"]:
        return x
    i = (semilla - 900_000 - 100 * p - mundo) // 10
    nombre = CTX["nombres"][i]
    if nombre in ENSAYOS:
        estados = np.random.get_state(), random.getstate()
        EXTRA[nombre] = {}
        for modo in MODOS:
            EXTRA[nombre][modo] = visita(k, s, mundo, semilla, CTX["h"], modo, D if modo == "instr" else LARGO)
        np.random.set_state(estados[0])
        random.setstate(estados[1])
    return x


g.ensayo = ensayo


def referencia(a: str, p: int, gm: str, escala: dict) -> dict:
    if a == "coin":
        return m.cargar_k11("coin", p, gm, escala)
    x = dict(np.load(m.DATA / f"una_{a}_{p}_{gm}{cr.humo(escala)}.npz"))
    return k7.salida((a, p, gm, escala, "una"), x, 0.0)


def una(args: tuple) -> dict:
    a, p, gm, escala = args
    ref = referencia(a, p, gm, escala)
    h, e = k7.casa_exilio(ref, p)
    nombres = [T for T, _ in escala["ensayos"]]
    w = g.GEMELOS.index(gm)
    CTX.update(par=p, casa=g.papeles(p)[gm], h=h, nombres=nombres)
    EXTRA.clear()
    archivo = f"vuelta_{a}_{p}_{gm}{cr.humo(escala)}"
    x = k7.vivir((a, p, gm, escala, "una", archivo, False))
    (m.DATA / f"{archivo}.npz").unlink()
    dif = {T: float(np.abs(EXTRA[T]["instr"]["dist"] - ref["ens_dist"][nombres.index(T), w]).max())
           for T in ENSAYOS}
    dif_sonda = {T: float(np.abs(EXTRA[T]["sonda"]["dist"] - EXTRA[T]["instr"]["dist"][:LARGO]).max())
                 for T in ENSAYOS}
    return {"brazo": a, "par": p, "gemelo": gm, "h": h, "e": e, "vida": cr.diferencia(x, ref),
            "ensayo": dif, "sonda": dif_sonda, "extra": dict(EXTRA)}


def lectura(v: dict, h: int) -> dict:
    """One clone's assay: switch to h, h's running error there, ticks h does not explain
    after it, and the cost before / after the switch and per window (first EARLY ticks)."""
    c, d = v["activo"][:EARLY], v["dist"][:EARLY]
    sw = int(np.flatnonzero(c == h)[0]) if (c == h).any() else EARLY
    r_h = float(v["run"][sw, h]) if sw < EARLY else float("nan")
    tras = v["explica"][sw + 1:EARLY] if sw < EARLY else np.array([], dtype=bool)
    no_explica = int(np.argmax(tras)) if tras.any() else len(tras)
    return {"sw": sw, "r_h": r_h, "no_explica": no_explica, "antes": float(d[:sw].sum() / EARLY),
            "despues": float(d[sw:].sum() / EARLY), "total": float(d.mean()),
            "w20_70": float(d[20:70].mean())}



def main(pares: tuple, escala: dict, nombre: str, titulo: str) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    tareas = [(a, p, gm, escala) for a in BRAZOS for p in pares for gm in g.GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        R = list(pool.map(una, tareas))
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, arms {BRAZOS}, {len(R)} lives re-run; {(time.time() - t0) / 60:.1f} min")
    out(f"verification: life re-run vs stored, max diff {max(r['vida'] for r in R)}; instr assay vs stored "
        f"assay {max(max(r['ensayo'].values()) for r in R)}; sonda vs instr {max(max(r['sonda'].values()) for r in R)}")
    umbral = R[0]["extra"][ENSAYOS[-1]]["instr"]["umbral"]
    out(f"threshold {umbral}; tick 0 = the clone's first tick at home; costs over the first {EARLY} ticks "
        "(sum before / after the switch, divided by EARLY: they add up to the assay's e_early)")
    L = {}
    for r in R:
        for T in ENSAYOS:
            for modo in MODOS:
                L[(r["brazo"], r["par"], r["gemelo"], T, modo)] = lectura(r["extra"][T][modo], r["h"])
    for T in ENSAYOS:
        out("")
        out(f"--- {T} home assay")
        for a in BRAZOS:
            claves = [(a, p, gm, T) for p in pares for gm in g.GEMELOS]
            for modo in ("instr", "lento_h", "congelado_h"):
                xs = [L[c + (modo,)] for c in claves]
                med = {f: np.median([x[f] for x in xs]) for f in xs[0]}
                out(f"  {a:>12} {modo:>11} | switch {med['sw']:5.1f} | r_h at switch {med['r_h']:.3f} | "
                    f"h not explaining after it {med['no_explica']:5.1f} ticks | before {med['antes']:.3f} "
                    f"after {med['despues']:.3f} total {med['total']:.3f} | ticks 20-70 {med['w20_70']:.3f}")
            sw_arriba = sum(L[c + ("instr",)]["r_h"] > umbral for c in claves)
            out(f"  {a:>12} r_h > threshold at the switch: {sw_arriba}/{len(claves)} twins")
            for modo in ("sonda", "lento_h", "congelado_h"):
                e_h = np.array([[r["extra"][T][modo]["err_h"][t] for t in TICKS_SONDA]
                                for r in R if r["brazo"] == a])
                out(f"  {a:>12} {modo:>11} h's own home-probe error at ticks {TICKS_SONDA}: "
                    f"{np.round(np.median(e_h, axis=0), 3)}")
        for modo in ("lento_h", "congelado_h"):
            for a in BRAZOS:
                claves = [(a, p, gm, T) for p in pares for gm in g.GEMELOS]
                baja = sum(L[c + (modo,)]["despues"] < L[c + ("instr",)]["despues"] for c in claves)
                out(f"  {modo:>11} lowers the cost after the switch, {a}: {baja}/{len(claves)} twins")
        E = [L[(m.NUEVO, p, gm, T, "instr")]["despues"] for p in pares for gm in g.GEMELOS]
        C = [L[("coin", p, gm, T, "instr")]["despues"] for p in pares for gm in g.GEMELOS]
        out(f"  after the switch {m.NUEVO} > coin: {sum(x > y for x, y in zip(E, C))}/{len(E)} twins")
    out("")
    out("per twin, T2 (instr): arm pair twin | switch | r_h | ticks not explaining | after: instr / lento_h / "
        "congelado_h")
    for r in R:
        a, p, gm = r["brazo"], r["par"], r["gemelo"]
        x = [L[(a, p, gm, "T2", modo)] for modo in ("instr", "lento_h", "congelado_h")]
        out(f"  {a:>12} {p} {gm} | {x[0]['sw']:3d} | {x[0]['r_h']:.3f} | {x[0]['no_explica']:3d} | "
            f"{x[0]['despues']:.3f} / {x[1]['despues']:.3f} / {x[2]['despues']:.3f}")
    (ROOT / "results" / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:] == ["humo"]:
        main((0,), g.HUMO, "mundo_propio_madurez_vuelta_humo", "§K12 MECHANISM SMOKE TEST (pair 0, short life)")
    else:
        main((0, 1, 2, 3), g.ESCALA, "mundo_propio_madurez_vuelta",
             "§K12 MECHANISM -- the return home after the exile")
