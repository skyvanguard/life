"""
§K3 -- a REPERTOIRE of the world: can the kernel's world model come to know WHICH
regime it is in (context inference), not only the average of what it lived?
(docs/MUNDO_PROPIO.md; pre-registered 2026-10-26, after the calibration below and
before any run on the test seeds)

WHY. §K2 (exp_mundo_propio_sueno.py) gave APRENDE Y RECUERDA, replicated, but BY
AVERAGING: sleep turns the world model into the exact average of the known regimes
(beyond-average 0/12 in both runs). The recommendation was ONE change, COIN-style:
the world model sees its own prediction error, ConsciousKernel(wm_error_input=True)
(GRU input = [action, observation - prediction of the last observed tick]; zero
error in imagination and at the start of each sleep window; off = byte-identical,
tests/test_error_input.py; the §K2 secuencia life of seed 0 reproduces, max diff 0).

WHAT THE CALIBRATION SHOWED (declared; seeds 100-102 and an offline pilot, never
the test seeds). (1) Offline pilot (the same architecture, BPTT on babbled
sequences of the 3 known regimes, 30000 steps, 3 seeds): even WITHOUT the error
input the architecture leaves the averaging plateau, after 5000-7500 steps
(known-regime probe 0.018 vs the exact average 0.103); the error input shortens
the plateau (0.019 at 7500 steps vs 0.067 without). The averaging of §K2 was a
training plateau, not a capacity limit. (2) Calibration in life (`calibracion`,
results/mundo_propio_contexto_calibracion.txt, babbled life): mean probe over the
known regimes at cycles 7-8, ratio to the exact average: secuencia (§K2) 1.07,
error (§K2 dose + error input) 1.03, secuencia_x4 (4 x the sleep dose, 200 steps
per sleep) 0.89 (2/3 below 0.9, late, cycle 8), error_x4 (both) 0.44 (3/3, from
cycle 6). Both are needed: the error input does nothing at the §K2 dose, the dose
alone barely gets there in one life.

THE CHANGE TESTED. error_x4 = the §K2 sleep (windows of 16, batch 8) with 4 x the
dose (wm_sleep_replay 200 per sleep, every 50 ticks) + wm_error_input. Controls
of attribution: secuencia_x4 (dose only) and error (error input only, §K2 dose).
The world, the calendar, the test ticks, the probe, the readouts and the §K1
rule are unchanged. The kernel / secuencia / congelado / reactivo lives (and
sin_sueno / secuencia of part 1) are READ from §K2's saved lives
(data/mundo_propio_sueno/*.npz): the code path is byte-identical (verified on
seed 0); re-run §K2 first if data/ is empty.

PART 1 -- POSITIVE CONTROL ON A BABBLED LIFE (`control`; seeds 0-11, as §K2 part 1).
Run arms error / secuencia_x4 / error_x4; read sin_sueno / secuencia.
  CONTEXTO_CTRL  error_x4's mean probe error over the 3 known regimes at the end
                 of the cycle 7-8 visits (median over those visits) < 0.9 x the
                 exact-average model's error (the §K2 BEYOND AVERAGING reading),
                 >= 10/12 (one-sided p 0.019).
  STOP RULE: if CONTEXTO_CTRL fails, part 2 is NOT run with this design.
  Attribution (reported): CONTEXTO_CTRL of secuencia_x4 and of error, and the
  burn-in gain (error during the first 8 ticks of a probe minus after them, > 0 =
  the latent carries the context).
  `error` runs in part 2 (flag --con-error) only if it passes CONTEXTO_CTRL in part 1.

PART 2 -- THE §K1 TEST (default; seeds 0-11). Run error_x4 and secuencia_x4; read
kernel / secuencia / congelado / reactivo.
  CONTEXTO (primary)  the CONTEXTO_CTRL reading on error_x4 in the acting life.
  BEHAVIOUR           the §K1 rule exactly on error_x4 (CONTROLA, APRENDE,
                      RECUERDA -> NO CONTROLA / APRENDE Y RECUERDA / APRENDE SIN
                      RECORDAR / RECUERDA SIN APRENDER / NADA).
  VERDICT   CONTEXTO and APRENDE Y RECUERDA      -> REPERTORIO
            CONTEXTO and another behaviour       -> REPERTORIO SIN CONDUCTA (+ it)
            no CONTEXTO                          -> SIN REPERTORIO (+ behaviour)
  ESPECIFICIDAD (secondary)  per seed, the RECUERDA difference (e_early NOVEL -
            mean e_early of the known visits of cycles 6-7) of error_x4 > that of
            secuencia (the §K2 generalist), >= 10/12: a repertoire's savings are
            more specific to what was lived. Reported with the paired entry costs
            (known visits of cycles 7-8, and NOVEL) of error_x4 vs secuencia.
  ATTRIBUTION (reported): CONTEXTO and verdict of secuencia_x4. If secuencia_x4
            also has CONTEXTO -> "the dose suffices; the error input accelerates".
  Reported, not verdicts: DISTINGUE (the §K1 Psi reading), stuck visits
  (e_late > 0.3), the probe on the current regime and on the NOVEL one.
PREDICTIONS written before running: part 1 error_x4 passes (calibration 3/3 at
0.44), secuencia_x4 borderline, error fails. Part 2: CONTEXTO at risk -- the
acting kernel lives near C, so its data is narrow and the escape from the plateau
(cycle 6 in the babbled calibration) may come later or not at all; ESPECIFICIDAD
positive if CONTEXTO holds; CONTROLA open (each 200-step sleep moves the world
model a lot).

REPLICATION (pre-registered 2026-10-26 after part 2 landed, before running):
seeds 12-23 (each regime still the NOVEL one in 3 seeds); run error_x4 only, read
kernel / secuencia / congelado / reactivo from the §K2 replication's saved lives;
the same rule. REPLICADO if error_x4 is again REPERTORIO. Pre-registered here as
secondary (in part 2 DISTINGUE was only reported, 12/12, and its paired contrast
was post hoc): DISTINGUE >= 10/12 AND DISTINGUE PAREADO -- per seed, the gap
frac(Psi<0.85 | EXO) - frac(Psi<0.85 | EFERENCIA) of error_x4 > that of the
kernel without sleep, >= 10/12 -- both needed to call it "distinguishes, and by
the mechanism" (the §K2 objection: a separation the kernel already has without
the mechanism is not the mechanism's). ESPECIFICIDAD reported again.

3 CPU processes, one torch thread each (declared exception to the GPU rule: the
kernel is tiny). Part 1 ~30 min, part 2 ~30 min, replication ~16 min.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py calibracion
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py control
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_contexto.py replica   # seeds 12-23
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("mundo_propio_sueno", HERE / "exp_mundo_propio_sueno.py")
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)
mp = ms.mp

RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio_contexto"
SEEDS = mp.SEEDS
SEEDS_CAL = (100, 101, 102)
N_OK = mp.N_OK
WORKERS = 3
D = mp.D
K2 = ms.SUENO["secuencia"]
BRAZOS = {
    "kernel": {},
    "secuencia": dict(K2),
    "error": {**K2, "wm_error_input": True},
    "secuencia_x4": {**K2, "wm_sleep_replay": 4 * K2["wm_sleep_replay"]},
    "error_x4": {**K2, "wm_sleep_replay": 4 * K2["wm_sleep_replay"], "wm_error_input": True},
    "congelado": {},
    "reactivo": {},
}
ARMS_CAL = ("secuencia", "error", "secuencia_x4", "error_x4")


def error_sonda(wm, obs, a) -> tuple[float, float]:
    """The §K2 probe; with the error input the recurrence also feeds the GRU its own
    error (zero at the start, as in a sleep window). Read-only."""
    import torch
    if not wm.error_input:
        return ms.error_sonda(wm, obs, a)
    b = wm.posterior_blend
    errs = []
    with torch.no_grad():
        z = wm.encoder(obs[:, 0])
        err = torch.zeros_like(obs[:, 0])
        for j in range(a.shape[1]):
            prior = wm.transition(wm._transition_input(a[:, j], None, err), z)
            pred = wm.predictor(prior)
            errs.append(torch.linalg.vector_norm(pred - obs[:, j + 1], dim=-1).mean())
            err = obs[:, j + 1] - pred
            z = b * prior + (1.0 - b) * wm.encoder(obs[:, j + 1])
    e = torch.stack(errs)
    return float(e[ms.QUEMA:].mean()), float(e[:ms.QUEMA].mean())


def nuevo_kernel(brazo: str, control: bool):
    import torch

    from zeta_life.kernel import ConsciousKernel
    kw = BRAZOS[brazo]
    if control or brazo == "reactivo":
        return ConsciousKernel(obs_dim=4, action_mode="reactive", **kw)
    return ConsciousKernel(obs_dim=4, action_mode="efe", preference=torch.tensor(mp.C),
                           efe_n_samples=48, efe_obs_norm="l1", **kw)


def vivir(args: tuple[str, int, bool]) -> dict:
    """One life: the §K2 loop (byte-identical for the §K2 arms) with the arm's kernel."""
    import torch
    brazo, seed, control = args
    t0 = time.time()
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    vis = mp.calendario(seed)
    tipo, a_test, a_babble = mp.pruebas(seed, vis)
    if control:
        tipo = np.zeros_like(tipo)
    n = len(vis) * D
    pref = torch.tensor(mp.C)
    k = nuevo_kernel(brazo, control)
    probes = ms.sondas()
    s = torch.full((4,), 0.25)
    dist, psi, fe = np.empty(n), np.empty(n), np.empty(n)
    sonda = np.empty((len(vis), 4))
    sonda0 = np.empty((len(vis), 4))
    for t in range(n):
        v = t // D
        fase, reg, _ = vis[v]
        if brazo == "congelado" and t == 3 * D:
            for g in k.world_model.optimizer.param_groups:
                g["lr"] = 0.0
        r = k.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        psi[t], fe[t] = r.psi, r.free_energy
        if control or fase == "babble":
            a = torch.tensor(a_babble[t], dtype=torch.float32)
            k.last_action = a
        elif tipo[t]:
            a = torch.tensor(a_test[t], dtype=torch.float32)
            if tipo[t] == 1:
                k.last_action = a
        else:
            a = r.action.detach()
        s = ((1 - mp.R) * s + mp.R * torch.roll(a, reg)).clamp(min=1e-6)
        s = s / s.sum()
        if t % D == D - 1:
            for kk in range(4):
                sonda[v, kk], sonda0[v, kk] = error_sonda(k.world_model, *probes[kk])
    DATA.mkdir(parents=True, exist_ok=True)
    tag = "control_" if control else ""
    np.savez_compressed(DATA / f"{tag}{brazo}_{seed}.npz", dist=dist, psi=psi, fe=fe, tipo=tipo,
                        sonda=sonda, sonda0=sonda0)
    return {"brazo": brazo, "seed": seed, "dist": dist, "psi": psi, "fe": fe, "tipo": tipo,
            "sonda": sonda, "sonda0": sonda0, "min": (time.time() - t0) / 60}


def correr(arms: tuple, seeds: tuple, control: bool) -> dict:
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        vidas = list(pool.map(vivir, itertools.product(arms, seeds, (control,))))
    return {(x["brazo"], x["seed"]): x for x in vidas}


def ganancia(vida: dict, seed: int, ciclos: tuple) -> float:
    """Median over the visits of `ciclos` of (error during the burn-in - after it) on the
    known regimes: > 0 = the context of the first ticks helps (the latent carries it)."""
    vis, nuevo = mp.calendario(seed), seed % 4
    conocidos = [k for k in range(4) if k != nuevo]
    return float(np.median([vida["sonda0"][v, conocidos].mean() - vida["sonda"][v, conocidos].mean()
                            for v, (_, _, c) in enumerate(vis) if c in ciclos]))


def main_calibracion() -> None:
    """Calibration on seeds 100-102 (never test seeds), babbled life: which sleep
    dose and whether the error input are needed to leave the averaging plateau."""
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    V = correr(ARMS_CAL, SEEDS_CAL, True)
    out("§K3 CALIBRATION (seeds 100-102, whole calendar babbled; not test seeds)")
    out(f"arms {ARMS_CAL}; run {(time.time() - t0) / 60:.1f} min")
    out("mean probe over the 3 known regimes, end of visit (median over seeds); "
        "exact-average reference per seed: " + str([round(ms.ref_promedio(s), 3) for s in SEEDS_CAL]))
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>12}" for a in ARMS_CAL))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(
            f"{np.median([ms.conocidos_medio(V[(a, s)], s, (ciclo,)) for s in SEEDS_CAL]):>12.3f}"
            for a in ARMS_CAL))
    out("")
    out(f"{'arm':>12} | known 7-8 | / avg | beyond | burn gain | novel 7-8 | current 7-8 | min/life")
    for a in ARMS_CAL:
        kn = [ms.conocidos_medio(V[(a, s)], s, (7, 8)) for s in SEEDS_CAL]
        ra = [kn[i] / ms.ref_promedio(s) for i, s in enumerate(SEEDS_CAL)]
        nv = [float(np.median([V[(a, s)]["sonda"][v, s % 4] for v, (_, _, c) in
                               enumerate(mp.calendario(s)) if c in (7, 8)])) for s in SEEDS_CAL]
        cur = [ms.otros(V[(a, s)], s, (7, 8))[1] for s in SEEDS_CAL]
        out(f"{a:>12} | {np.median(kn):>9.3f} | {np.median(ra):>5.2f} | {sum(r < 0.9 for r in ra):>4}/3 | "
            f"{np.median([ganancia(V[(a, s)], s, (7, 8)) for s in SEEDS_CAL]):>+9.3f} | "
            f"{np.median(nv):>9.3f} | {np.median(cur):>11.3f} | "
            f"{np.median([V[(a, s)]['min'] for s in SEEDS_CAL]):>8.1f}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "mundo_propio_contexto_calibracion.txt").write_text("\n".join(lines), encoding="utf-8")


def cargar_k2(brazo: str, seed: int, control: bool) -> dict:
    """A §K2 life from its saved npz (the §K2 arms are byte-identical here)."""
    f = ms.DATA / f"{'control_' if control else ''}{brazo}_{seed}.npz"
    if not f.exists():
        raise SystemExit(f"missing {f}: run exp_mundo_propio_sueno.py first")
    return {"brazo": brazo, "seed": seed, **dict(np.load(f))}


def vidas(correr_arms: tuple, leer_arms: tuple, seeds: tuple, control: bool) -> dict:
    V = correr(correr_arms, seeds, control) if correr_arms else {}
    for a in leer_arms:
        for s in seeds:
            V[(a, s)] = cargar_k2(a, s, control)
    return V


def contexto(V: dict, brazo: str, seeds: tuple) -> dict:
    """The BEYOND AVERAGING reading: known-regime probe at cycles 7-8 vs 0.9 x average."""
    kn = [ms.conocidos_medio(V[(brazo, s)], s, (7, 8)) for s in seeds]
    ra = [kn[i] / ms.ref_promedio(s) for i, s in enumerate(seeds)]
    nv = [float(np.median([V[(brazo, s)]["sonda"][v, s % 4] for v, (_, _, c)
                           in enumerate(mp.calendario(s)) if c in (7, 8)])) for s in seeds]
    return {"kn": kn, "ratio": ra, "n": sum(r < 0.9 for r in ra),
            "gan": [ganancia(V[(brazo, s)], s, (7, 8)) for s in seeds],
            "nuevo": nv, "actual": [ms.otros(V[(brazo, s)], s, (7, 8))[1] for s in seeds]}


def tabla_contexto(V: dict, arms: tuple, seeds: tuple, out) -> dict:
    out("mean probe over the 3 known regimes, end of visit (median over seeds); exact average "
        f"{np.median([ms.ref_promedio(s) for s in seeds]):.3f}")
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>12}" for a in arms))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(
            f"{np.median([ms.conocidos_medio(V[(a, s)], s, (ciclo,)) for s in seeds]):>12.3f}"
            for a in arms))
    out("")
    out(f"{'arm':>12} | known 7-8 | / avg | below 0.9 | burn gain | NOVEL 7-8 | current 7-8")
    res = {}
    for a in arms:
        x = contexto(V, a, seeds)
        res[a] = x
        out(f"{a:>12} | {np.median(x['kn']):>9.3f} | {np.median(x['ratio']):>5.2f} | "
            f"{x['n']:>6}/{len(seeds)} | {np.median(x['gan']):>+9.3f} | {np.median(x['nuevo']):>9.3f} | "
            f"{np.median(x['actual']):>11.3f}")
    return res


def veredicto(pv: dict, brazo: str, seeds: tuple) -> dict:
    """The §K1 rule with `brazo` in the place of the kernel (= ms.veredicto_brazo, seeds explicit)."""
    def visitas(a: str, s: int, ciclos: tuple) -> list[dict]:
        return [x for x in pv[(a, s)] if x["ciclo"] in ciclos]

    controla = [np.mean([x["late"] for x in visitas(brazo, s, (7, 8))])
                < 0.5 * np.mean([x["late"] for x in visitas("reactivo", s, (7, 8))]) for s in seeds]
    aprende = [visitas(brazo, s, (0,))[0]["late"] < visitas("congelado", s, (0,))[0]["late"]
               for s in seeds]
    dif = [visitas(brazo, s, (0,))[0]["early"]
           - np.mean([x["early"] for x in visitas(brazo, s, (6, 7))]) for s in seeds]
    c_ok, a_ok = sum(controla) >= N_OK, sum(aprende) >= N_OK
    r_ok = sum(d > 0 for d in dif) >= N_OK
    if not c_ok:
        v = "NO CONTROLA"
    elif a_ok and r_ok:
        v = "APRENDE Y RECUERDA"
    elif a_ok:
        v = "APRENDE SIN RECORDAR"
    elif r_ok:
        v = "RECUERDA SIN APRENDER"
    else:
        v = "NADA"
    return {"controla": sum(controla), "aprende": sum(aprende), "recuerda": sum(d > 0 for d in dif),
            "dif": dif, "veredicto": v,
            "atascadas": sum(x["late"] > 0.3 for s in seeds for x in pv[(brazo, s)] if x["fase"] == "act"),
            "early_conocido": [np.mean([x["early"] for x in visitas(brazo, s, (7, 8))]) for s in seeds],
            "early_nuevo": [visitas(brazo, s, (0,))[0]["early"] for s in seeds],
            "late_nuevo": float(np.median([visitas(brazo, s, (0,))[0]["late"] for s in seeds]))}


def main_control(seeds: tuple = SEEDS, nombre: str = "mundo_propio_contexto_control") -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    V = vidas(("error", "secuencia_x4", "error_x4"), ("sin_sueno", "secuencia"), seeds, True)
    arms = ("sin_sueno", "secuencia", "error", "secuencia_x4", "error_x4")
    out("=" * 80)
    out("§K3 PART 1 -- POSITIVE CONTROL: does the world model infer the regime in a babbled life?")
    out("=" * 80)
    out(f"seeds {seeds[0]}-{seeds[-1]} x {arms} (sin_sueno, secuencia read from §K2); "
        f"run {(time.time() - t0) / 60:.1f} min")
    out("")
    res = tabla_contexto(V, arms, seeds, out)
    ok = res["error_x4"]["n"] >= N_OK
    out("")
    out("-" * 80)
    out(f"CONTEXTO_CTRL  error_x4 below 0.9 x average: {res['error_x4']['n']}/{len(seeds)} -> "
        f"{'yes' if ok else 'NO'}")
    for a in ("secuencia_x4", "error"):
        out(f"  attribution: {a:>12} {res[a]['n']}/{len(seeds)} -> "
            f"{'yes' if res[a]['n'] >= N_OK else 'no'}")
    out("  error " + ("PASSES: it runs in part 2 (--con-error)" if res["error"]["n"] >= N_OK
                      else "fails: it does not run in part 2"))
    out("")
    out("STOP RULE: " + ("passed, part 2 may run" if ok
                         else "CONTEXTO_CTRL failed -> part 2 is NOT run with this design"))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines), encoding="utf-8")


def main(seeds: tuple = SEEDS, nombre: str = "mundo_propio_contexto", con_error: bool = False,
         correr_arms: tuple = ("error_x4", "secuencia_x4")) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    correr_arms = correr_arms + (("error",) if con_error else ())
    V = vidas(correr_arms, ("kernel", "secuencia", "congelado", "reactivo"), seeds, False)
    pv = {key: mp.por_visita(x, mp.calendario(key[1])) for key, x in V.items()}
    vivos = ("kernel", "secuencia") + correr_arms
    out("=" * 80)
    out("§K3 PART 2 -- THE KERNEL IN ITS OWN WORLD: does it build a REPERTOIRE of the world?")
    out("=" * 80)
    out(f"seeds {seeds[0]}-{seeds[-1]}; run {correr_arms}, read from §K2 kernel / secuencia / "
        f"congelado / reactivo; run {(time.time() - t0) / 60:.1f} min")
    out("")
    out(f"mean ||s - C|| per cycle (median over seeds)    early = ticks 0-{mp.EARLY - 1}, "
        f"late = {mp.LATE0}-{D - 1}")
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>13}" for a in vivos))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        cel = []
        for a in vivos:
            e = [np.mean([x["early"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in seeds]
            la = [np.mean([x["late"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in seeds]
            cel.append(f"{np.median(e):.3f}/{np.median(la):.3f}")
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(f"{c:>13}" for c in cel))
    out("")
    ctx = tabla_contexto(V, vivos, seeds, out)
    out("")
    out("-" * 80)
    out(f"{'arm':>12} | CONTROLA APRENDE RECUERDA | NOVEL late | stuck | median RECUERDA dif | verdict")
    ver = {}
    for a in vivos:
        x = veredicto(pv, a, seeds)
        ver[a] = x
        out(f"{a:>12} | {x['controla']:>5}/{len(seeds)} {x['aprende']:>5}/{len(seeds)} "
            f"{x['recuerda']:>5}/{len(seeds)} | {x['late_nuevo']:>10.3f} | {x['atascadas']:>5} | "
            f"{np.median(x['dif']):>+19.3f} | {x['veredicto']}")
    out("RECUERDA dif per seed (error_x4): " + str([round(float(d), 3) for d in ver["error_x4"]["dif"]]))
    c_ok = ctx["error_x4"]["n"] >= N_OK
    out(f"CONTEXTO (primary)  error_x4 below 0.9 x average: {ctx['error_x4']['n']}/{len(seeds)} -> "
        f"{'yes' if c_ok else 'no'}")
    esp = [ver["error_x4"]["dif"][i] > ver["secuencia"]["dif"][i] for i in range(len(seeds))]
    out(f"ESPECIFICIDAD  RECUERDA dif error_x4 > secuencia: {sum(esp)}/{len(seeds)} -> "
        f"{'yes' if sum(esp) >= N_OK else 'no'}")
    for etiqueta, clave in (("known entry (cycles 7-8)", "early_conocido"), ("NOVEL entry", "early_nuevo")):
        a, b = ver["error_x4"][clave], ver["secuencia"][clave]
        out(f"  paired {etiqueta:>24}: error_x4 < secuencia {sum(a[i] < b[i] for i in range(len(seeds)))}"
            f"/{len(seeds)} (medians {np.median(a):.3f} vs {np.median(b):.3f})")
    for a in correr_arms[1:]:
        out(f"ATTRIBUTION  {a}: CONTEXTO {ctx[a]['n']}/{len(seeds)}, verdict {ver[a]['veredicto']}"
            + ("  -> the dose suffices; the error input accelerates"
               if a == "secuencia_x4" and ctx[a]["n"] >= N_OK else ""))
    out("")
    out("Psi (cycles 3+ and NOVEL; frac Psi < 0.85 on the tick that perceives the test)")
    out(f"{'arm':>12} | {'EXO':>5} {'EFER':>5} {'false':>5} | {'AUC fe EXO>EFER':>15}")
    lect = {}
    for a in vivos:
        ls = [mp.lectura_psi(V[(a, s)], mp.calendario(s)) for s in seeds]
        lect[a] = ls
        m = {k2: float(np.nanmedian([x[k2] for x in ls])) for k2 in ls[0]}
        out(f"{a:>12} | {m['exo']:>5.2f} {m['efer']:>5.2f} {m['fa']:>5.2f} | {m['auc_fe']:>15.2f}")
    dist = sum(x["exo"] > x["efer"] for x in lect["error_x4"])
    out(f"DISTINGUE (error_x4, EXO > EFERENCIA): {dist}/{len(seeds)} -> {'yes' if dist >= N_OK else 'no'}")
    gap = {a: [x["exo"] - x["efer"] for x in lect[a]] for a in ("kernel", "error_x4")}
    par = sum(gap["error_x4"][i] > gap["kernel"][i] for i in range(len(seeds)))
    out(f"DISTINGUE PAREADO  gap EXO-EFER error_x4 > kernel: {par}/{len(seeds)} (medians "
        f"{np.median(gap['error_x4']):+.3f} vs {np.median(gap['kernel']):+.3f}) -> "
        f"{'yes' if par >= N_OK else 'no'}")
    conducta = ver["error_x4"]["veredicto"]
    if c_ok and conducta == "APRENDE Y RECUERDA":
        final = "REPERTORIO"
    elif c_ok:
        final = f"REPERTORIO SIN CONDUCTA ({conducta})"
    else:
        final = f"SIN REPERTORIO ({conducta})"
    out("")
    out(f"VERDICT (pre-registered rule, error_x4): {final}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines), encoding="utf-8")
    (RESULTS / f"{nombre}_visitas.json").write_text(
        json.dumps({f"{a}_{s}": v for (a, s), v in pv.items()}), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calibracion":
        main_calibracion()
    elif len(sys.argv) > 1 and sys.argv[1] == "control":
        main_control()
    elif len(sys.argv) > 1 and sys.argv[1] == "replica":
        main(tuple(range(12, 24)), "mundo_propio_contexto_replica", correr_arms=("error_x4",))
    else:
        main(con_error="--con-error" in sys.argv)
