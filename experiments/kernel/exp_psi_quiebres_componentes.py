"""
Which term of Psi moves its threshold? (mechanism check for exp_psi_quiebres.py)

WHY. In exp_psi_quiebres.py the free-energy ratio r* at which Psi leaves ALTA
rose from ~1.4 (clean stream) to ~3 (noise SIGMA 0.10) and ~3.5 (breaks on 30%
of ticks), and with it the false alarms fell and the breaks went unseen. Psi =
Hill(B), B = (Phi - Phi_c) / Phi_c, Phi = phi_base + 0.2 * len(fast_memory)/500,
phi_base = 1 / (1 + FE / EMA(FE)). Candidate: the episodic-memory bonus (the
fast memory is surprise-gated, so a surprising life fills it) rather than
Phi_c. This records, per tick, Phi and Phi_c (by wrapping compute_psi_hill) and
the fast-memory size, for four streams of the same harness (seed 0), and reads
the fast-memory size of Yvyra's saved kernel (read-only), if present.

    PYTHONPATH=src python experiments/kernel/exp_psi_quiebres_componentes.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
import zeta_life.kernel.conscious_kernel as ck  # noqa: E402

_spec = importlib.util.spec_from_file_location("quiebres", HERE / "exp_psi_quiebres.py")
q = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(q)

FLUJOS = (  # (sigma, delta, p, seed)
    (0.0, 0.0, 0.03, 0),
    (0.0, 0.35, 0.03, 0),
    (0.10, 0.35, 0.03, 0),
    (0.0, 0.35, 0.30, 0),
)
CKPT_YVYRA = Path.home() / ".hermes" / "zeta" / "state" / "yvyra.ckpt"
B_ALTA = 0.1 * (0.85 / 0.15) ** 0.25    # B at which Hill(n=4, K=0.1) = 0.85


def componentes(args: tuple[float, float, float, int]) -> dict:
    reg: list[tuple[float, float]] = []
    hill = ck.compute_psi_hill

    def grabar(phi: float, phi_c: float, n: float, K: float) -> float:
        reg.append((phi, phi_c))
        return hill(phi, phi_c, n, K)

    ck.compute_psi_hill = grabar
    try:
        x, _, _ = q.flujo(*args)
        torch.manual_seed(args[3])
        c = torch.tensor(q.PREFERENCE)
        k = ck.ConsciousKernel(obs_dim=4, action_mode="reactive", preference=c / c.sum(),
                               efe_obs_norm="l1", precision_hypermodel=True,
                               psi_fe_scale=1.0, psi_fe_adaptive=True)
        mem = np.empty(q.TICKS)
        for i in range(q.TICKS):
            k.step(torch.tensor(x[i], dtype=torch.float32))
            mem[i] = len(k.fast_memory)
    finally:
        ck.compute_psi_hill = hill
    phi, phi_c = np.array(reg).T
    bono = 0.2 * mem / 500.0
    m = slice(q.SKIP, None)
    umbral_base = (1 + B_ALTA) * phi_c[m].mean() - bono[m].mean()
    return {"mem": mem[m].mean(), "bono": bono[m].mean(), "phi_base": (phi - bono)[m].mean(),
            "phi_c": phi_c[m].mean(), "r_pred": 1.0 / max(umbral_base, 1e-9) - 1.0}


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    torch.set_num_threads(1)
    out("=" * 78)
    out(f"WHICH TERM OF PSI MOVES ITS THRESHOLD? (seed 0, ticks >= {q.SKIP})")
    out("=" * 78)
    out(f"Psi < 0.85  <=>  Phi < (1 + {B_ALTA:.3f}) Phi_c  <=>  FE/EMA(FE) > r_pred = 1/(threshold - bonus) - 1")
    out("")
    out(f"{'SIGMA':>6} {'DELTA':>6} {'P':>5} | {'fast mem':>8} {'bonus':>6} {'phi_base':>8} {'Phi_c':>6} {'r_pred':>6}")
    for args in FLUJOS:
        a = componentes(args)
        out(f"{args[0]:>6.2f} {args[1]:>6.2f} {args[2]:>5.2f} | {a['mem']:>8.0f} {a['bono']:>6.3f} "
            f"{a['phi_base']:>8.3f} {a['phi_c']:>6.3f} {a['r_pred']:>6.2f}")
    out("")
    if CKPT_YVYRA.exists():
        fm = torch.load(CKPT_YVYRA, map_location="cpu", weights_only=False).get("fast_memory", {})
        out(f"Yvyra's saved kernel: fast memory {len(fm.get('episodes', []))}/{fm.get('capacity')} episodes "
            f"(bonus {0.2 * len(fm.get('episodes', [])) / 500:.3f})")
    else:
        out("Yvyra's saved kernel: not found")
    (q.RESULTS / "psi_quiebres_componentes_run.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
