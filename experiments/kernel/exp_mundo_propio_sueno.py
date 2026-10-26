"""
§K2 -- a memory of the WORLD: the kernel's world model replays lived sequences in
sleep. Does it then remember the regimes it has lived (savings)?
(docs/MUNDO_PROPIO.md; pre-registered 2026-10-26, before any run)

WHY. §K1 (exp_mundo_propio.py): the kernel learns a never-seen regime in life
(12/12) but re-learns every known regime on every visit (RECUERDA 6/12). Verified
in the code: the dream and the complementary memory consolidate the SELF; nothing
consolidates the world model, a single online SGD learner. §K2 adds ONE thing,
ConsciousKernel(wm_sleep_replay=...): every lived transition is kept, and on each
dream tick (every 50) the world model takes gradient steps on windows sampled
from the whole lived past.

WHY SEQUENCES (a design point found reading the code, before running). The regime
is HIDDEN: one transition (s, a, s') does not say which regime produced it. A
one-step replay (the dreamer replay_wm update) interleaves all regimes into a
model that cannot tell them apart, so it can only average them. Sequence replay
runs the world model's own recurrence (prior -> posterior blend, exactly as in
waking life) through windows of 16 consecutive ticks with backprop through time,
so the latent can learn to carry the regime as a context inferred from the last
few ticks (the in-context inference COIN uses to explain savings). The waking
learner never backpropagates more than one tick, so it cannot learn that.

THE WORLD, the calendar, the test ticks, the readouts and the §K1 rule: unchanged
(imported from exp_mundo_propio.py).

SLEEP (declared, not tuned): wm_sleep_replay = 50 gradient steps per sleep, one
per lived tick (sleep doubles the training of the predictive transition: half
from the present, half from the whole lived past, buffer capacity 10000 > 7500
ticks). Each step = 128 replayed transitions:
  secuencia  8 windows x 16 consecutive ticks, BPTT through each window.
  paso       128 single transitions (seq_len 1 = the context-free one-step replay).

THE PROBE (mechanism readout, no effect on the life: no_grad, local latent, no
RNG). Per regime k, a fixed set (same for every seed and arm, numpy seed 7000+k)
of 32 sequences of 24 babbled transitions (s0 and actions Dirichlet(1)). The world
model runs its recurrence from encode(s0); error = mean ||predicted - actual s||
over steps 8-23 (after an 8-tick context burn-in), measured at the end of every
visit for the 4 regimes. "Others" = the 3 recurring regimes minus the current one.

PART 1 -- POSITIVE CONTROL OF THE MECHANISM (`control`). The whole calendar is
babbled (Dirichlet(1) actions with efference copy every tick, no test ticks,
reactive kernel: the action is always overridden), arms sin_sueno / secuencia /
paso, 12 seeds. Per seed: median probe error on the others at the end of the
visits of cycles 3-8 and NOVEL.
  RETIENE_CTRL   secuencia < sin_sueno, >= 10/12 (one-sided p 0.019).
  CONTEXTO_CTRL  secuencia < paso, >= 10/12.
  STOP RULE: if RETIENE_CTRL fails, part 2 is NOT run with this design; the
  failure is reported and the mechanism redesigned.

PART 2 -- THE §K1 TEST WITH SLEEP (default). Arms (12 seeds, world shared by seed):
  kernel     the §K1 kernel, no sleep replay (must reproduce §K1: 9/12, 12/12, 6/12)
  secuencia  kernel + sleep replay of sequences        <- the arm of the verdict
  paso       kernel + one-step sleep replay            <- context-free control
  congelado  as §K1 (world-model lr 0 after the babbling cycle)
  reactivo   as §K1 (no goal)
RULE: the §K1 rule exactly, with secuencia in the place of the kernel:
  CONTROLA   secuencia e_late on cycles 7-8 < 0.5 x reactivo, >= 10/12.
  APRENDE    NOVEL visit: secuencia e_late < congelado, >= 10/12.
  RECUERDA   (primary) secuencia e_early(NOVEL) > mean secuencia e_early of the 6
             known visits around it (cycles 6 and 7), >= 10/12.
  VERDICT    not CONTROLA -> NO CONTROLA; else APRENDE Y RECUERDA / APRENDE SIN
             RECORDAR / RECUERDA SIN APRENDER / NADA.
  ATTRIBUTION (adversarial): the same RECUERDA reading on paso. If secuencia
  RECUERDA and paso does not -> "by context". If both do -> "by interleaving,
  not context" (the sequence is not what matters).
  Secondary, pre-registered:
  RETIENE    probe error on the others at the end of the cycle 7-8 visits
             (median per seed): secuencia < kernel, >= 10/12. CAVEAT declared
             before running (seen in the smoke test at 40-tick visits): the acting
             kernel lives near C, so its own data is narrow; replaying the babbled
             infancy alone lowers the probe in ANY sleeping arm. The probe contrast
             that isolates context is secuencia vs paso, reported alongside.
  DISTINGUE  the §K1 Psi reading on secuencia (EXO > EFERENCIA, >= 10/12).
  Reported, not verdicts: the three arms' verdicts by the same rule; the probe on
  the current regime (does sleep cost the present?); stuck visits (e_late > 0.3).
  REPRODUCTION check: the kernel arm's per-visit e_early/e_late are compared with
  §K1's results/mundo_propio_visitas.json (max abs difference reported).
PREDICTIONS written before running: kernel reproduces §K1 exactly (same seeds,
the probe touches nothing); paso averages the regimes and controls worse than
kernel; secuencia: open.

3 CPU processes, one torch thread each (the kernel is tiny; declared exception to
the GPU rule). Part 1 ~10 min, part 2 ~25 min.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_sueno.py control
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_sueno.py
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
_spec = importlib.util.spec_from_file_location("mundo_propio", HERE / "exp_mundo_propio.py")
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)

RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio_sueno"
SEEDS = mp.SEEDS
N_OK = mp.N_OK
WORKERS = 3
D = mp.D
SUENO = {"secuencia": {"wm_sleep_replay": 50, "wm_sleep_seq_len": 16, "wm_sleep_batch": 8},
         "paso": {"wm_sleep_replay": 50, "wm_sleep_seq_len": 1, "wm_sleep_batch": 128}}
ARMS_CTRL = ("sin_sueno", "secuencia", "paso")
ARMS = ("kernel", "secuencia", "paso", "congelado", "reactivo")
M_SONDA = 32
L_SONDA = 24
QUEMA = 8


def mover(s, a, k: int):
    """The §K1 physics, batched over the last axis."""
    import torch
    s = ((1 - mp.R) * s + mp.R * torch.roll(a, k, dims=-1)).clamp(min=1e-6)
    return s / s.sum(dim=-1, keepdim=True)


def sondas() -> dict:
    """Fixed probe per regime: obs (M, L+1, 4) and actions (M, L, 4)."""
    import torch
    out = {}
    for k in range(4):
        rng = np.random.default_rng(7000 + k)
        s = torch.tensor(rng.dirichlet(np.ones(4), size=M_SONDA), dtype=torch.float32)
        a = torch.tensor(rng.dirichlet(np.ones(4), size=(M_SONDA, L_SONDA)), dtype=torch.float32)
        obs = [s]
        for j in range(L_SONDA):
            obs.append(mover(obs[-1], a[:, j], k))
        out[k] = (torch.stack(obs, dim=1), a)
    return out


def error_sonda(wm, obs, a) -> tuple[float, float]:
    """(error after the context burn-in, error during it): the world model's own
    recurrence from encode(s0), read-only."""
    import torch
    b = wm.posterior_blend
    errs = []
    with torch.no_grad():
        z = wm.encoder(obs[:, 0])
        for j in range(a.shape[1]):
            prior = wm.transition(a[:, j], z)
            errs.append(torch.linalg.vector_norm(wm.predictor(prior) - obs[:, j + 1], dim=-1).mean())
            z = b * prior + (1.0 - b) * wm.encoder(obs[:, j + 1])
    e = torch.stack(errs)
    return float(e[QUEMA:].mean()), float(e[:QUEMA].mean())


def nuevo_kernel(brazo: str, control: bool):
    import torch

    from zeta_life.kernel import ConsciousKernel
    sueno = SUENO.get(brazo, {})
    if control or brazo == "reactivo":
        return ConsciousKernel(obs_dim=4, action_mode="reactive", **sueno)
    return ConsciousKernel(obs_dim=4, action_mode="efe", preference=torch.tensor(mp.C),
                           efe_n_samples=48, efe_obs_norm="l1", **sueno)


def vivir(args: tuple[str, int, bool]) -> dict:
    """One life: the §K1 loop (byte-identical for kernel/congelado/reactivo) plus the
    probe at the end of every visit. control = every tick babbled, no tests."""
    import torch
    brazo, seed, control = args
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    vis = mp.calendario(seed)
    tipo, a_test, a_babble = mp.pruebas(seed, vis)
    if control:
        tipo = np.zeros_like(tipo)
    n = len(vis) * D
    pref = torch.tensor(mp.C)
    k = nuevo_kernel(brazo, control)
    probes = sondas()
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
            "sonda": sonda, "sonda0": sonda0}


def otros(vida: dict, seed: int, ciclos: tuple) -> tuple[float, float]:
    """Median over the visits of `ciclos` of (probe on the others, probe on the current)."""
    vis = mp.calendario(seed)
    nuevo = seed % 4
    conocidos = [k for k in range(4) if k != nuevo]
    o, c = [], []
    for v, (_, reg, ciclo) in enumerate(vis):
        if ciclo not in ciclos:
            continue
        o.append(np.mean([vida["sonda"][v, k] for k in conocidos if k != reg]))
        c.append(vida["sonda"][v, reg])
    return float(np.median(o)), float(np.median(c))


def correr(arms: tuple, control: bool) -> dict:
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        vidas = list(pool.map(vivir, itertools.product(arms, SEEDS, (control,))))
    return {(x["brazo"], x["seed"]): x for x in vidas}


def escribir(lines: list[str], nombre: str) -> None:
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / nombre).write_text("\n".join(lines), encoding="utf-8")


def tabla_sonda(V: dict, arms: tuple, out) -> None:
    out("probe error after the burn-in, end of visit (median over seeds): others | current | burn-in on others")
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>22}" for a in arms))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        cel = []
        for a in arms:
            o = [otros(V[(a, s)], s, (ciclo,)) for s in SEEDS]
            q = []
            for s in SEEDS:
                vis, nuevo = mp.calendario(s), s % 4
                q += [np.mean([V[(a, s)]["sonda0"][v, k] for k in range(4) if k not in (nuevo, reg)])
                      for v, (_, reg, c) in enumerate(vis) if c == ciclo]
            cel.append(f"{np.median([x[0] for x in o]):.3f} {np.median([x[1] for x in o]):.3f} "
                       f"{np.median(q):.3f}")
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(f"{c:>22}" for c in cel))


def main_control() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    V = correr(ARMS_CTRL, True)
    out("=" * 80)
    out("§K2 PART 1 -- POSITIVE CONTROL: does sleep replay make the world model RETAIN the regimes?")
    out("=" * 80)
    out(f"{len(SEEDS)} seeds x {ARMS_CTRL}; whole calendar babbled; sleep {SUENO}; run "
        f"{(time.time() - t0) / 60:.1f} min")
    out("")
    tabla_sonda(V, ARMS_CTRL, out)
    ciclos = (3, 4, 5, 6, 0, 7, 8)
    m = {a: [otros(V[(a, s)], s, ciclos)[0] for s in SEEDS] for a in ARMS_CTRL}
    retiene = [m["secuencia"][i] < m["sin_sueno"][i] for i in range(len(SEEDS))]
    contexto = [m["secuencia"][i] < m["paso"][i] for i in range(len(SEEDS))]
    out("")
    out("-" * 80)
    out("probe on the others, visits of cycles 3-8 + NOVEL, median per seed:")
    for a in ARMS_CTRL:
        out(f"  {a:>10}: median {np.median(m[a]):.3f}   per seed {[round(x, 3) for x in m[a]]}")
    out(f"RETIENE_CTRL   secuencia < sin_sueno: {sum(retiene)}/{len(SEEDS)} -> "
        f"{'yes' if sum(retiene) >= N_OK else 'NO'}")
    out(f"CONTEXTO_CTRL  secuencia < paso:      {sum(contexto)}/{len(SEEDS)} -> "
        f"{'yes' if sum(contexto) >= N_OK else 'no'}")
    out("")
    out("STOP RULE: " + ("passed, part 2 may run" if sum(retiene) >= N_OK
                         else "RETIENE_CTRL failed -> part 2 is NOT run with this design"))
    escribir(lines, "mundo_propio_sueno_control_run.txt")


def veredicto_brazo(pv: dict, brazo: str) -> dict:
    """The §K1 rule with `brazo` in the place of the kernel."""
    def visitas(a: str, s: int, ciclos: tuple) -> list[dict]:
        return [x for x in pv[(a, s)] if x["ciclo"] in ciclos]

    controla = [np.mean([x["late"] for x in visitas(brazo, s, (7, 8))])
                < 0.5 * np.mean([x["late"] for x in visitas("reactivo", s, (7, 8))]) for s in SEEDS]
    aprende = [visitas(brazo, s, (0,))[0]["late"] < visitas("congelado", s, (0,))[0]["late"]
               for s in SEEDS]
    dif = [visitas(brazo, s, (0,))[0]["early"]
           - np.mean([x["early"] for x in visitas(brazo, s, (6, 7))]) for s in SEEDS]
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
    atascadas = sum(x["late"] > 0.3 for s in SEEDS for x in pv[(brazo, s)]
                    if x["fase"] == "act")
    return {"controla": sum(controla), "aprende": sum(aprende), "recuerda": sum(d > 0 for d in dif),
            "r_ok": r_ok, "dif": dif, "veredicto": v, "atascadas": atascadas,
            "late_nuevo": float(np.median([visitas(brazo, s, (0,))[0]["late"] for s in SEEDS]))}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    V = correr(ARMS, False)
    pv = {key: mp.por_visita(x, mp.calendario(key[1])) for key, x in V.items()}
    out("=" * 80)
    out("§K2 PART 2 -- THE KERNEL IN ITS OWN WORLD, WITH A SLEEP THAT REPLAYS THE WORLD")
    out("=" * 80)
    out(f"{len(SEEDS)} seeds x {ARMS}; sleep {SUENO}; run {(time.time() - t0) / 60:.1f} min")
    out("")
    out(f"mean ||s - C|| per cycle (median over seeds)    early = ticks 0-{mp.EARLY - 1}, "
        f"late = {mp.LATE0}-{D - 1}")
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>13}" for a in ARMS))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        cel = []
        for a in ARMS:
            e = [np.mean([x["early"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in SEEDS]
            la = [np.mean([x["late"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in SEEDS]
            cel.append(f"{np.median(e):.3f}/{np.median(la):.3f}")
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(f"{c:>13}" for c in cel))
    out("")
    tabla_sonda(V, ("kernel", "secuencia", "paso"), out)
    out("")
    out("-" * 80)
    out(f"{'arm':>10} | CONTROLA APRENDE RECUERDA | NOVEL late | stuck | median RECUERDA dif | verdict")
    ver = {}
    for a in ("kernel", "secuencia", "paso"):
        x = veredicto_brazo(pv, a)
        ver[a] = x
        out(f"{a:>10} | {x['controla']:>5}/12 {x['aprende']:>5}/12 {x['recuerda']:>5}/12 | "
            f"{x['late_nuevo']:>10.3f} | {x['atascadas']:>5} | {np.median(x['dif']):>+19.3f} | "
            f"{x['veredicto']}")
    out("RECUERDA dif per seed (secuencia): " + str([round(float(d), 3) for d in ver["secuencia"]["dif"]]))
    if ver["secuencia"]["r_ok"]:
        atrib = "by interleaving, not context" if ver["paso"]["r_ok"] else "by context"
    else:
        atrib = "-- (secuencia does not RECUERDA)"
    out(f"ATTRIBUTION: {atrib}")
    r_sec = [otros(V[("secuencia", s)], s, (7, 8))[0] for s in SEEDS]
    r_ker = [otros(V[("kernel", s)], s, (7, 8))[0] for s in SEEDS]
    retiene = [r_sec[i] < r_ker[i] for i in range(len(SEEDS))]
    out(f"RETIENE  probe on the others, cycles 7-8: secuencia < kernel {sum(retiene)}/{len(SEEDS)} "
        f"(medians {np.median(r_sec):.3f} vs {np.median(r_ker):.3f}) -> "
        f"{'yes' if sum(retiene) >= N_OK else 'no'}")
    r_paso = [otros(V[("paso", s)], s, (7, 8))[0] for s in SEEDS]
    out(f"         (context contrast) secuencia < paso {sum(r_sec[i] < r_paso[i] for i in range(len(SEEDS)))}"
        f"/{len(SEEDS)} (paso median {np.median(r_paso):.3f})")
    k1 = RESULTS / "mundo_propio_visitas.json"
    if k1.exists():
        ref = json.loads(k1.read_text(encoding="utf-8"))
        dmax = max(abs(a[c] - b[c]) for s in SEEDS for a, b in zip(pv[("kernel", s)], ref[f"kernel_{s}"])
                   for c in ("early", "late"))
        out(f"REPRODUCTION  kernel arm vs §K1 per visit: max |diff| = {dmax:.2e} -> "
            f"{'reproduces' if dmax < 1e-9 else 'DOES NOT reproduce'}")
    else:
        out("REPRODUCTION  §K1 per-visit file not found; not checked")
    out("")
    out("Psi (cycles 3+ and NOVEL; frac Psi < 0.85 on the tick that perceives the test)")
    out(f"{'arm':>10} | {'EXO':>5} {'EFER':>5} {'false':>5} | {'AUC fe EXO>EFER':>15} | n EXO/EFER")
    lect = {}
    for a in ("kernel", "secuencia", "paso"):
        ls = [mp.lectura_psi(V[(a, s)], mp.calendario(s)) for s in SEEDS]
        lect[a] = ls
        m = {k2: float(np.nanmedian([x[k2] for x in ls])) for k2 in ls[0]}
        out(f"{a:>10} | {m['exo']:>5.2f} {m['efer']:>5.2f} {m['fa']:>5.2f} | {m['auc_fe']:>15.2f} | "
            f"{m['n_exo']:.0f}/{m['n_efer']:.0f}")
    distingue = [x["exo"] > x["efer"] for x in lect["secuencia"]]
    out(f"DISTINGUE (secuencia, EXO > EFERENCIA): {sum(distingue)}/{len(SEEDS)} -> "
        f"{'yes' if sum(distingue) >= N_OK else 'no'}")
    out("")
    out(f"VERDICT (pre-registered rule, secuencia): {ver['secuencia']['veredicto']}")
    escribir(lines, "mundo_propio_sueno_run.txt")
    (RESULTS / "mundo_propio_sueno_visitas.json").write_text(
        json.dumps({f"{a}_{s}": v for (a, s), v in pv.items()}), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "control":
        main_control()
    else:
        main()
