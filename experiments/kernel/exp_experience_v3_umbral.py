"""
How big must a within-tick difference be for Psi to see it? (calibration curve
of the instrument; docs/PHASE_B_DESIGN.md, "v3")

WHY. The offline replay (exp_experience_v3_replay.py) gave 913 distinct v3 axis
vectors over Yvyra's real life against 15 before, and Psi did not notice: it
stayed ALTA in 100% of the introspection ticks that do not follow a mode switch.
Psi (Hill n=4, K=0.1 over free energy relative to its own running mean) only
registers surprises of some size. Before designing events for her life we need
that size.

WHAT. Her real v3 life (journals -> v3 axes, as in the replay), plus synthetic
EVENTS: in a fraction P_EV of introspection ticks (drawn once, fixed seed) the
axes are shifted by DELTA along a fixed direction d = (+1, 0, -1, -1)/sqrt(3)
(more lexical novelty, less uptake, shorter: what an intrusion or an empty
prompt would plausibly do), clipped to [0, 1]. Sweep DELTA. Reference scale: the
distance between her mean introspection and mean research axes (a mode switch).
Each arm is one faithful deployment simulation (load/save per tick).

AMENDMENT (2026-10-26, after the first sweep): the first direction moved
introspection ticks TOWARD the world model's blurred average prediction, so
event ticks were predicted BETTER (an artefact of the direction, not a lag of
Psi; checked tick by tick). The sweep now also runs on the OLD low-noise axes
and with a direction orthogonal to the introspection->research axis:
  --base v3|old   --dir hacia_b|ortogonal
Hypothesis under test: Psi (relative surprise) sees rare large breaks in a
predictable stream better than the same breaks in a noisy stream.

READOUT (a curve, no verdict): after the first 200 ticks, among introspection
ticks that do not follow a mode switch, frac(not ALTA) on event ticks, on the
tick right after an event, and on the rest; first vs second half (does the
kernel habituate to iid events?). Declared reading: DELTA* = the smallest DELTA
with frac(not ALTA | event) >= 0.5 and frac(not ALTA | rest) <= 0.2.

    PYTHONPATH=src python experiments/kernel/exp_experience_v3_umbral.py
"""

from __future__ import annotations

import importlib.util
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

_spec = importlib.util.spec_from_file_location("v3replay", HERE / "exp_experience_v3_replay.py")
rp = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(rp)

P_EV = 0.30
DELTAS = (0.0, 0.1, 0.2, 0.3, 0.5, 0.8)
DIR_HACIA_B = np.array([1.0, 0.0, -1.0, -1.0]) / np.sqrt(3.0)
SEED = 7
SKIP = rp.SKIP
HI = rp.HI


def direccion(base: np.ndarray, kinds: list[str], cual: str) -> np.ndarray:
    """Unit event direction: toward research, or orthogonal to the A->B axis."""
    if cual == "hacia_b":
        return DIR_HACIA_B
    k = np.array(kinds)
    ab = base[k == "B"].mean(0) - base[k == "A"].mean(0)
    ab = ab / np.linalg.norm(ab)
    v = np.array([0.0, 0.0, 1.0, -1.0])           # more uptake, shorter
    v = v - (v @ ab) * ab
    return v / np.linalg.norm(v)


def con_eventos(base: np.ndarray, kinds: list[str], delta: float,
                d: np.ndarray = DIR_HACIA_B) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    ev = np.array([k == "A" and rng.random() < P_EV for k in kinds])
    x = base.copy()
    x[ev] = np.clip(x[ev] + delta * d, 0.0, 1.0)
    return x, ev


def _brazo(args: tuple) -> np.ndarray:
    import torch
    torch.set_num_threads(1)
    scores = args
    return rp.simular([list(map(float, r)) for r in scores])


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", choices=("v3", "old"), default="v3")
    ap.add_argument("--dir", choices=("hacia_b", "ortogonal"), default="hacia_b")
    args = ap.parse_args()
    if args.base == "old":
        sc, kinds = rp.leer_old()
        base = np.array(sc)
    else:
        vida = rp.leer_vida()
        kinds = [k for _, k, _ in vida]
        base = np.array(rp.ejes_v3_vida(vida))
    k = np.array(kinds)
    d_ev = direccion(base, kinds, args.dir)
    ref = float(np.linalg.norm(base[k == "B"].mean(0) - base[k == "A"].mean(0)))
    out("=" * 78)
    out("HOW BIG MUST A WITHIN-TICK DIFFERENCE BE FOR PSI TO SEE IT?")
    out("=" * 78)
    out(f"base {args.base} ({len(k)} ticks); events in {P_EV:.0%} of introspection ticks along {args.dir} d={d_ev.round(3).tolist()}")
    out(f"reference: mode-switch distance |mean B - mean A| = {ref:.3f}; within-introspection axis std "
        f"{base[k == 'A'].std(0).round(3).tolist()} (norm {np.linalg.norm(base[k == 'A'].std(0)):.3f})")
    entradas = [con_eventos(base, kinds, d, d_ev) for d in DELTAS]
    with ProcessPoolExecutor(max_workers=len(DELTAS)) as pool:
        psis = list(pool.map(_brazo, [x for x, _ in entradas]))
    sw = np.r_[False, k[1:] != k[:-1]]
    idx = np.arange(len(k)) >= SKIP
    mitad = SKIP + (len(k) - SKIP) // 2
    out("")
    out(f"{'DELTA':>6} {'xref':>5} | not ALTA on: {'event':>7} {'after':>7} {'rest':>7} | event 1st/2nd half")
    estrella = None
    for d, (x, ev), p in zip(DELTAS, entradas, psis):
        na = p < HI
        tras = np.r_[False, ev[:-1]] & ~ev
        base_m = idx & (k == "A") & ~sw
        m_ev, m_tr, m_re = base_m & ev, base_m & tras, base_m & ~ev & ~tras
        h1, h2 = m_ev & (np.arange(len(k)) < mitad), m_ev & (np.arange(len(k)) >= mitad)
        f = [float(na[m].mean()) if m.any() else float("nan") for m in (m_ev, m_tr, m_re, h1, h2)]
        out(f"{d:>6.2f} {d / ref:>5.2f} | {'':>12} {f[0]:>7.2f} {f[1]:>7.2f} {f[2]:>7.2f} | {f[3]:.2f} / {f[4]:.2f}   (n event {int(m_ev.sum())})")
        if estrella is None and f[0] >= 0.5 and f[2] <= 0.2:
            estrella = d
    out("")
    out(f"DELTA* (event not-ALTA >= 0.5 with rest <= 0.2): {estrella if estrella is not None else 'not reached in the sweep'}"
        + (f" = {estrella / ref:.2f} x a mode switch" if estrella else ""))
    rp.RESULTS.mkdir(exist_ok=True)
    (rp.RESULTS / "experience_v3_umbral_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
