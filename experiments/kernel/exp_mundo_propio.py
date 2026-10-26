"""
The kernel in its OWN world: does it learn in life, does it remember what it
lived, and does Psi tell what it did from what happened to it?
(docs/MUNDO_PROPIO.md; pre-registered 2026-10-26, before any run)

WHY. Decision 2026-10-26 (Fran): the kernel is the agent; no Hermes, no LLM.
exp_psi_quiebres.py showed Psi is a relative-surprise detector. Here the kernel
lives in a world where its own actions cause what it perceives, the world has
regimes that RECUR (what the utero cells never saw: they lived two seasons), and
one regime it has never seen appears late in life. Two classic paradigms of
motor learning, done on the kernel: savings on re-adaptation to a known
visuomotor-like remapping, and attenuation of self-produced sensations
(efference copy).

THE WORLD. State s on the 4-simplex, s' = normalize((1 - 0.3) s + 0.3 roll(a, k)):
the action a moves the state, but regime k (0..3) remaps WHICH coordinate each
action component pushes. The kernel's preference is C = (0.7, 0.1, 0.1, 0.1),
fixed for life (its own). To hold the state at C under regime k it must act
roll(C, -k). Visits of 300 ticks. Of the 4 regimes, 3 RECUR in a fixed cycle;
the 4th (NOVEL = seed mod 4, so every regime is the novel one in 3 of the 12
seeds) appears once, late:
  cycle 1        3 visits, motor babbling (random Dirichlet(1) actions WITH
                 efference copy: the kernel registers them as its own)
  cycles 2-6     15 visits, the kernel acts
  NOVEL          1 visit
  cycles 7-8     6 visits
  = 25 visits, 7500 ticks.
TEST TICKS (from cycle 2 on, only in ticks 150-299 of a visit, ~3% each type,
never within 6 ticks of another): the environment executes a random
Dirichlet(0.5) action a_r instead of the kernel's. EFERENCIA: the kernel's
last_action is set to a_r (it "knows" what moved). EXO: its last_action stays
its own (something else moved it). Same physics, same distribution of
displacement; only the efference copy differs.

ARMS (12 seeds; world, babbling and test ticks shared across arms by seed):
  kernel    ConsciousKernel, action_mode efe, 48 continuous samples, l1 (the
            exp_control configuration), learning all its life.
  congelado same kernel, world-model optimizer frozen (lr 0) after the babbling
            cycle: learns only in infancy.
  reactivo  action = softmax(obs), no goal: the no-control reference.

READOUT (declared before running). Per visit: e_early = mean ||s - C|| over its
ticks 0-99 (re-adaptation cost); e_late = mean over ticks 150-299 excluding the
test ticks and the 5 after each.
RULE (sign tests over the 12 seeds; 10/12 = one-sided p 0.019):
  CONTROLA   kernel e_late on cycles 7-8 < 0.5 x reactivo e_late on the same
             visits, in >= 10/12 seeds.
  APRENDE    on the NOVEL visit, kernel e_late < congelado e_late, >= 10/12:
             it learns a regime it never saw, which infancy alone does not give.
  RECUERDA   (primary) kernel e_early(NOVEL) > mean kernel e_early of the 6
             known visits around it (cycle 6 and cycle 7), >= 10/12: at the
             same age, a known regime is re-entered faster than a new one.
  VERDICT    not CONTROLA -> NO CONTROLA; else APRENDE Y RECUERDA / APRENDE SIN
             RECORDAR / RECUERDA SIN APRENDER / NADA.
  Secondary, Psi (kernel arm, cycles 3+): DISTINGUE if frac(Psi < 0.85) on the
  tick that perceives an EXO test > on the tick that perceives an EFERENCIA
  test, >= 10/12. Reported with the free-energy AUC (EXO vs EFERENCIA), the
  false-alarm rate on ordinary late ticks, and Psi on the first 5 ticks of
  known vs NOVEL visits.
  Descriptive, not a verdict: kernel e_early on cycles 7-8 vs cycle 2 (does
  re-entry improve over life?).
NOT MEASURED HERE: identity. It needs its own design (e.g. twins raised in
different worlds); declared as next.

3 CPU processes, one torch thread each (~6.7 ms/tick with EFE), ~10 min.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio.py
"""

from __future__ import annotations

import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio"

R = 0.3
C = (0.7, 0.1, 0.1, 0.1)
D = 300
EARLY = 100
LATE0 = 150
P_TEST = 0.03
GAP = 6
HI = 0.85
SEEDS = tuple(range(12))
ARMS = ("kernel", "congelado", "reactivo")
WORKERS = 3
N_OK = 10


def calendario(seed: int) -> list[tuple[str, int, int]]:
    """[(phase, regime, cycle)] per visit; phase babble | act; cycle 0 = NOVEL."""
    nuevo = seed % 4
    conocidos = [k for k in range(4) if k != nuevo]
    vis = [("babble", k, 1) for k in conocidos]
    for c in range(2, 7):
        vis += [("act", k, c) for k in conocidos]
    vis.append(("act", nuevo, 0))
    for c in (7, 8):
        vis += [("act", k, c) for k in conocidos]
    return vis


def pruebas(seed: int, vis: list[tuple[str, int, int]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per tick: test type (0 none, 1 EFERENCIA, 2 EXO), random test actions, babble actions."""
    rng = np.random.default_rng(5000 + seed)
    n = len(vis) * D
    tipo = np.zeros(n, dtype=int)
    ultimo = -GAP
    for v, (fase, _, _) in enumerate(vis):
        if fase == "babble":
            continue
        for t in range(v * D + LATE0, (v + 1) * D - 1):
            if t - ultimo >= GAP and rng.random() < 2 * P_TEST:
                tipo[t] = 1 + int(rng.random() < 0.5)
                ultimo = t
    a_test = rng.dirichlet(np.full(4, 0.5), size=n)
    a_babble = rng.dirichlet(np.ones(4), size=n)
    return tipo, a_test, a_babble


def vivir(args: tuple[str, int]) -> dict:
    """One life. Per kernel step t: dist ||s_t - C||, psi_t, fe_t. The action
    returned at step t moves the world into s_{t+1} under the regime of tick t."""
    import torch

    from zeta_life.kernel import ConsciousKernel
    brazo, seed = args
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    vis = calendario(seed)
    tipo, a_test, a_babble = pruebas(seed, vis)
    n = len(vis) * D
    pref = torch.tensor(C)
    if brazo == "reactivo":
        k = ConsciousKernel(obs_dim=4, action_mode="reactive")
    else:
        k = ConsciousKernel(obs_dim=4, action_mode="efe", preference=pref, efe_n_samples=48,
                            efe_obs_norm="l1")
    s = torch.full((4,), 0.25)
    dist, psi, fe = np.empty(n), np.empty(n), np.empty(n)
    for t in range(n):
        v = t // D
        fase, reg, _ = vis[v]
        if brazo == "congelado" and t == 3 * D:
            for g in k.world_model.optimizer.param_groups:
                g["lr"] = 0.0
        r = k.step(s)
        dist[t] = float(torch.linalg.vector_norm(s - pref))
        psi[t], fe[t] = r.psi, r.free_energy
        if fase == "babble":
            a = torch.tensor(a_babble[t], dtype=torch.float32)
            k.last_action = a
        elif tipo[t]:
            a = torch.tensor(a_test[t], dtype=torch.float32)
            if tipo[t] == 1:
                k.last_action = a
        else:
            a = r.action.detach()
        s = ((1 - R) * s + R * torch.roll(a, reg)).clamp(min=1e-6)
        s = s / s.sum()
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA / f"{brazo}_{seed}.npz", dist=dist, psi=psi, fe=fe, tipo=tipo)
    return {"brazo": brazo, "seed": seed, "dist": dist, "psi": psi, "fe": fe, "tipo": tipo}


def por_visita(vida: dict, vis: list) -> list[dict]:
    """e_early / e_late per visit; tests and the 5 ticks after each excluded from e_late."""
    tipo = vida["tipo"]
    sucio = np.zeros(len(tipo), dtype=bool)
    for t in np.flatnonzero(tipo):
        sucio[t: t + 6] = True
    out = []
    for v, (fase, reg, ciclo) in enumerate(vis):
        a = v * D
        late = np.arange(a + LATE0, a + D)
        late = late[~sucio[late]]
        out.append({"fase": fase, "reg": reg, "ciclo": ciclo,
                    "early": float(vida["dist"][a: a + EARLY].mean()),
                    "late": float(vida["dist"][late].mean())})
    return out


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    from scipy.stats import rankdata
    r = rankdata(np.r_[pos, neg])
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def lectura_psi(vida: dict, vis: list) -> dict:
    """Psi on the tick that PERCEIVES each test (t + 1), cycles 3+ only."""
    tipo, psi, fe = vida["tipo"], vida["psi"], vida["fe"]
    n = len(tipo)
    ciclo = np.repeat([c for _, _, c in vis], D)
    madura = (ciclo >= 3) | (ciclo == 0)
    efer = np.array([t + 1 for t in np.flatnonzero(tipo == 1) if madura[t] and t + 1 < n])
    exo = np.array([t + 1 for t in np.flatnonzero(tipo == 2) if madura[t] and t + 1 < n])
    pos = np.arange(n) % D
    sucio = np.zeros(n, dtype=bool)
    for t in np.flatnonzero(tipo):
        sucio[t: t + 6] = True
    normal = madura & (pos >= LATE0) & ~sucio
    ini = pos < 5
    nuevo = ini & (ciclo == 0)
    conocido = ini & madura & (ciclo != 0)
    bajo = psi < HI
    return {"exo": float(bajo[exo].mean()), "efer": float(bajo[efer].mean()),
            "fa": float(bajo[normal].mean()), "auc_fe": auc(fe[exo], fe[efer]),
            "ini_nuevo": float(bajo[nuevo].mean()), "ini_conocido": float(bajo[conocido].mean()),
            "n_exo": len(exo), "n_efer": len(efer)}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        vidas = list(pool.map(vivir, itertools.product(ARMS, SEEDS)))
    V = {(x["brazo"], x["seed"]): x for x in vidas}
    pv = {key: por_visita(x, calendario(key[1])) for key, x in V.items()}

    out("=" * 80)
    out("THE KERNEL IN ITS OWN WORLD: learns in life? remembers? tells what it did?")
    out("=" * 80)
    out(f"{len(SEEDS)} seeds x {ARMS}; 25 visits of {D} ticks (babble cycle, cycles 2-6, NOVEL, cycles 7-8); "
        f"C = {C}; run {(time.time() - t0) / 60:.1f} min")
    out("")
    out(f"mean ||s - C|| per cycle (median over seeds)    early = ticks 0-{EARLY - 1}, late = {LATE0}-{D - 1}")
    out(f"{'cycle':>8} | " + " | ".join(f"{a:>17}" for a in ARMS))
    for ciclo in (1, 2, 3, 4, 5, 6, 0, 7, 8):
        cel = []
        for a in ARMS:
            e = [np.mean([x["early"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in SEEDS]
            la = [np.mean([x["late"] for x in pv[(a, s)] if x["ciclo"] == ciclo]) for s in SEEDS]
            cel.append(f"{np.median(e):.3f} / {np.median(la):.3f}")
        out(f"{'NOVEL' if ciclo == 0 else ciclo:>8} | " + " | ".join(f"{c:>17}" for c in cel))

    def visitas(a: str, s: int, ciclos: tuple) -> list[dict]:
        return [x for x in pv[(a, s)] if x["ciclo"] in ciclos]

    controla = [np.mean([x["late"] for x in visitas("kernel", s, (7, 8))])
                < 0.5 * np.mean([x["late"] for x in visitas("reactivo", s, (7, 8))]) for s in SEEDS]
    aprende = [visitas("kernel", s, (0,))[0]["late"] < visitas("congelado", s, (0,))[0]["late"] for s in SEEDS]
    dif = [visitas("kernel", s, (0,))[0]["early"]
           - np.mean([x["early"] for x in pv[("kernel", s)] if x["ciclo"] in (6, 7)]) for s in SEEDS]
    recuerda = [d > 0 for d in dif]
    mejora = [np.mean([x["early"] for x in visitas("kernel", s, (7, 8))])
              < np.mean([x["early"] for x in visitas("kernel", s, (2,))]) for s in SEEDS]
    out("")
    out("-" * 80)
    out(f"CONTROLA  kernel late (cycles 7-8) < 0.5 x reactivo: {sum(controla)}/{len(SEEDS)}")
    out(f"APRENDE   NOVEL late: kernel < congelado: {sum(aprende)}/{len(SEEDS)}   "
        f"(medians kernel {np.median([visitas('kernel', s, (0,))[0]['late'] for s in SEEDS]):.3f}, "
        f"congelado {np.median([visitas('congelado', s, (0,))[0]['late'] for s in SEEDS]):.3f})")
    out(f"RECUERDA  NOVEL early > known early around it (cycles 6-7): {sum(recuerda)}/{len(SEEDS)}   "
        f"(median difference {np.median(dif):+.3f}; per seed {[round(float(d), 3) for d in dif]})")
    out(f"(descriptive) kernel early cycles 7-8 < cycle 2: {sum(mejora)}/{len(SEEDS)}")
    c_ok, a_ok, r_ok = sum(controla) >= N_OK, sum(aprende) >= N_OK, sum(recuerda) >= N_OK
    if not c_ok:
        veredicto = "NO CONTROLA"
    elif a_ok and r_ok:
        veredicto = "APRENDE Y RECUERDA"
    elif a_ok:
        veredicto = "APRENDE SIN RECORDAR"
    elif r_ok:
        veredicto = "RECUERDA SIN APRENDER"
    else:
        veredicto = "NADA"

    out("")
    out("Psi (cycles 3+ and NOVEL; frac Psi < 0.85 on the tick that perceives the test)")
    out(f"{'arm':>10} | {'EXO':>5} {'EFER':>5} {'false':>5} | {'AUC fe EXO>EFER':>15} | "
        f"{'1st 5 ticks known':>17} {'NOVEL':>6} | n EXO/EFER")
    lect = {}
    for a in ARMS:
        ls = [lectura_psi(V[(a, s)], calendario(s)) for s in SEEDS]
        lect[a] = ls
        m = {k2: float(np.nanmedian([x[k2] for x in ls])) for k2 in ls[0]}
        out(f"{a:>10} | {m['exo']:>5.2f} {m['efer']:>5.2f} {m['fa']:>5.2f} | {m['auc_fe']:>15.2f} | "
            f"{m['ini_conocido']:>17.2f} {m['ini_nuevo']:>6.2f} | {m['n_exo']:.0f}/{m['n_efer']:.0f}")
    distingue = [x["exo"] > x["efer"] for x in lect["kernel"]]
    out(f"DISTINGUE (kernel, EXO > EFERENCIA): {sum(distingue)}/{len(SEEDS)} -> "
        f"{'yes' if sum(distingue) >= N_OK else 'no'}")
    out("")
    out(f"VERDICT (pre-registered rule): {veredicto}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "mundo_propio_run.txt").write_text("\n".join(lines), encoding="utf-8")
    (RESULTS / "mundo_propio_visitas.json").write_text(
        json.dumps({f"{a}_{s}": v for (a, s), v in pv.items()}), encoding="utf-8")


if __name__ == "__main__":
    main()
