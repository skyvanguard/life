"""
Does Psi see rare large breaks in a PREDICTABLE stream, and does noise bury
them? (the hypothesis left open by exp_experience_v3_umbral.py; the kernel ALONE)

WHY. Over Yvyra's life Psi stayed ALTA in 100% of the introspection ticks off a
mode switch, with the old binary axes and with the noisy v3 content axes alike.
Reading of _compute_psi: with psi_fe_adaptive the free energy is divided by its
own running mean (EMA 0.99), so Psi is a detector of RELATIVE surprise. Hypothesis
H: it registers rare large breaks in a predictable stream, and the same breaks
are buried when the stream is noisy (noise raises the reference). Decision
2026-10-26 (Fran): no Hermes, no other agent -- the kernel is the agent. So this
test feeds the kernel directly, no bridge, no load/save.

THE KERNEL. ConsciousKernel with the configuration that saturated in Yvyra
(obs_dim 4, reactive, preference (0.3,0.4,0.1,0.2), l1, precision hyper-model,
psi_fe_adaptive with psi_fe_scale 1.0), dreaming on its own default cadence
(dream_interval 50; the bridge dreamt every 20 ticks by hand). One kernel per run.

THE STREAM (4000 ticks). A learnable base x_t = 0.5 + 0.1 sin(2 pi t / 12 + i)
on axis i; iid Gaussian noise of std SIGMA per axis; BREAKS: on a fraction P of
ticks (drawn once per seed) the tick is displaced by DELTA along a random unit
direction (a fresh direction per break, so no fixed direction can move breaks
toward the model's average prediction -- the artefact of the first v3 curve);
everything clipped to [0, 1], and the effective (post-clip) displacement norm is
reported. Grid: SIGMA {0, 0.02, 0.05, 0.10} x DELTA {0, 0.1, 0.2, 0.35, 0.5} x
P {0.03, 0.30} x 3 seeds = 120 runs.

READOUT (declared before running), ticks >= 800 only:
  H  = frac(Psi < 0.85 | break tick)                    hit rate
  F  = frac(Psi < 0.85 | not a break, not right after)  false alarms
  AUC of -Psi and of free energy, break vs rest (is the information in the
  free energy before Psi compresses it?)
  frac(not ALTA) over all measured ticks (the Phase B target needed ALTA <= 0.75)
  mechanism: r_t = free_energy_t / fe_ref_t; best threshold r* for "Psi < 0.85"
  and its agreement.
RULE (means over the 3 seeds, P = 0.03 = "rare"):
  P1  at SIGMA = 0 some DELTA > 0 has H >= 0.5 and F <= 0.05. DELTA1 = the
      smallest such DELTA.
  P2  at DELTA1, H falls with noise: H(SIGMA 0.10) <= 0.5 * H(SIGMA 0).
  CONFIRMADA = P1 and P2; NO LO ENTIERRA = P1 without P2; NO DETECTA = not P1.
  Secondary: P3 rarity, H(P 0.30) < H(P 0.03) at SIGMA 0, DELTA1; and the
  ceiling: frac(not ALTA) <= 1/r* in every run (Markov, if Psi is a ratio rule).

Runs on 3 CPU processes (one torch thread each; the kernel is too small for the
GPU to help; ~3.4 ms/tick), ~15 min.

    PYTHONPATH=src python experiments/kernel/exp_psi_quiebres.py
"""

from __future__ import annotations

import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
RESULTS = ROOT / "results"

TICKS = 4000
SKIP = 800
HI = 0.85
PERIODO = 12
AMP = 0.1
SIGMAS = (0.0, 0.02, 0.05, 0.10)
DELTAS = (0.0, 0.1, 0.2, 0.35, 0.5)
PS = (0.03, 0.30)
SEEDS = (0, 1, 2)
PREFERENCE = (0.30, 0.40, 0.10, 0.20)
WORKERS = 3


def flujo(sigma: float, delta: float, p: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(stream, break mask, effective displacement norm per tick)."""
    rng = np.random.default_rng(1000 + seed)
    t = np.arange(TICKS)[:, None]
    base = 0.5 + AMP * np.sin(2 * np.pi * t / PERIODO + np.arange(4)[None, :])
    ruido = sigma * rng.standard_normal((TICKS, 4))
    quiebre = rng.random(TICKS) < p
    d = rng.standard_normal((TICKS, 4))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    limpio = np.clip(base + ruido, 0.0, 1.0)
    x = np.clip(base + ruido + delta * d * quiebre[:, None], 0.0, 1.0)
    return x, quiebre, np.linalg.norm(x - limpio, axis=1)


def vivir(x: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The kernel alone: one step per tick. Returns (psi, free_energy, fe_ref)."""
    import torch

    from zeta_life.kernel.conscious_kernel import ConsciousKernel
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    c = torch.tensor(PREFERENCE)
    k = ConsciousKernel(obs_dim=4, action_mode="reactive", preference=c / c.sum(),
                        efe_obs_norm="l1", precision_hypermodel=True,
                        psi_fe_scale=1.0, psi_fe_adaptive=True)
    psi, fe, ref = np.empty(TICKS), np.empty(TICKS), np.empty(TICKS)
    for i in range(TICKS):
        r = k.step(torch.tensor(x[i], dtype=torch.float32))
        psi[i], fe[i], ref[i] = r.psi, r.free_energy, k._fe_ref
    return psi, fe, ref


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(score of a positive > score of a negative), ties count half."""
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    from scipy.stats import rankdata
    r = rankdata(np.r_[pos, neg])
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def regla_razon(ratio: np.ndarray, bajo: np.ndarray) -> tuple[float, float]:
    """Best threshold r* such that (ratio > r*) reproduces (Psi < HI); (r*, agreement)."""
    cand = np.quantile(ratio, np.linspace(0.5, 0.999, 200))
    acc = [float(np.mean((ratio > c) == bajo)) for c in cand]
    j = int(np.argmax(acc))
    return float(cand[j]), acc[j]


def correr(args: tuple[float, float, float, int]) -> dict:
    sigma, delta, p, seed = args
    x, q, desp = flujo(sigma, delta, p, seed)
    psi, fe, ref = vivir(x, seed)
    m = np.arange(TICKS) >= SKIP
    tras = np.r_[False, q[:-1]] & ~q
    bajo = psi < HI
    ev, resto = m & q, m & ~q & ~tras
    r_star, acuerdo = regla_razon(fe[m] / np.maximum(ref[m], 1e-9), bajo[m])
    return {
        "sigma": sigma, "delta": delta, "p": p, "seed": seed,
        "H": float(bajo[ev].mean()) if ev.any() else float("nan"),
        "F": float(bajo[resto].mean()),
        "auc_psi": auc(-psi[ev], -psi[resto]), "auc_fe": auc(fe[ev], fe[resto]),
        "no_alta": float(bajo[m].mean()), "r_star": r_star, "acuerdo": acuerdo,
        "desp_ef": float(desp[ev].mean()) if ev.any() else 0.0, "n_ev": int(ev.sum()),
    }


def media(rs: list[dict], **f) -> dict:
    sel = [r for r in rs if all(r[k] == v for k, v in f.items())]
    return {k: float(np.nanmean([r[k] for r in sel])) for k in
            ("H", "F", "auc_psi", "auc_fe", "no_alta", "r_star", "acuerdo", "desp_ef")}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    grid = list(itertools.product(SIGMAS, DELTAS, PS, SEEDS))
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        rs = list(pool.map(correr, grid))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "psi_quiebres_runs.json").write_text(json.dumps(rs, indent=1), encoding="utf-8")

    out("=" * 78)
    out("DOES PSI SEE RARE LARGE BREAKS IN A PREDICTABLE STREAM? (the kernel alone)")
    out("=" * 78)
    out(f"{TICKS} ticks, readout from tick {SKIP}; base 0.5 + {AMP} sin(2 pi t/{PERIODO} + i); "
        f"{len(SEEDS)} seeds per cell; Psi < {HI} = 'not ALTA'")
    for p in PS:
        out("")
        out(f"--- breaks in {p:.0%} of ticks ---")
        out(f"{'SIGMA':>6} {'DELTA':>6} {'ef':>5} | {'H':>5} {'F':>5} | {'AUCpsi':>6} {'AUCfe':>6} | "
            f"{'notALTA':>7} {'r*':>5} {'agree':>5}")
        for s in SIGMAS:
            for d in DELTAS:
                a = media(rs, sigma=s, delta=d, p=p)
                out(f"{s:>6.2f} {d:>6.2f} {a['desp_ef']:>5.2f} | {a['H']:>5.2f} {a['F']:>5.2f} | "
                    f"{a['auc_psi']:>6.2f} {a['auc_fe']:>6.2f} | {a['no_alta']:>7.3f} {a['r_star']:>5.2f} "
                    f"{a['acuerdo']:>5.3f}")

    rara = PS[0]
    out("")
    out("-" * 78)
    d1 = None
    for d in DELTAS[1:]:
        a = media(rs, sigma=0.0, delta=d, p=rara)
        if a["H"] >= 0.5 and a["F"] <= 0.05:
            d1 = d
            break
    p1 = d1 is not None
    out(f"P1 (sigma 0, rare breaks: some DELTA with H >= 0.5 and F <= 0.05): "
        f"{'yes, DELTA1 = ' + str(d1) if p1 else 'no'}")
    p2 = False
    if p1:
        h = [media(rs, sigma=s, delta=d1, p=rara)["H"] for s in SIGMAS]
        p2 = h[-1] <= 0.5 * h[0]
        out(f"P2 (H at DELTA1 by SIGMA {list(SIGMAS)}): {[round(v, 2) for v in h]} -> "
            f"H(0.10) <= 0.5 H(0): {'yes' if p2 else 'no'}")
        h_frec = media(rs, sigma=0.0, delta=d1, p=PS[1])["H"]
        out(f"P3 (rarity, sigma 0, DELTA1): H(P {PS[1]}) = {h_frec:.2f} vs H(P {rara}) = {h[0]:.2f} -> "
            f"{'lower' if h_frec < h[0] else 'not lower'}")
    techo = [r for r in rs if r["no_alta"] > 1.0 / max(r["r_star"], 1e-9) + 1e-9]
    out(f"ceiling frac(not ALTA) <= 1/r*: violated in {len(techo)}/{len(rs)} runs; "
        f"max frac(not ALTA) over all runs {max(r['no_alta'] for r in rs):.3f}; "
        f"median r* {np.median([r['r_star'] for r in rs]):.2f}, median agreement "
        f"{np.median([r['acuerdo'] for r in rs]):.3f}")
    veredicto = "CONFIRMADA" if p1 and p2 else ("NO LO ENTIERRA" if p1 else "NO DETECTA")
    out("")
    out(f"VERDICT (pre-registered rule): {veredicto}")
    (RESULTS / "psi_quiebres_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
