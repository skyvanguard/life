"""
§K10 measurement (docs/MUNDO_PROPIO.md): is the slept home expert precise only right
after each sleep? Re-runs one coin life (§K7's loop; pair 0, twin A) and probes the
home world with the ACTIVE expert at every tick of the last 150 childhood ticks --
inside the model's tick, after its online step and before that tick's sleep -- and
compares it with the block-end oracle the experiments record (taken right after a
sleep: block ends fall on dream ticks). The life itself is unchanged (the probe only
reads); its file is not kept.

RESULT (2026-10-27, run first from the scratchpad with the same code): right after a
sleep 0.004-0.006; over the 151 ticks median 0.012, mean 0.046, above 0.05 in 43, up to
0.215 -- online learning between two sleeps erodes what the sleep consolidated.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_entre_suenos.py          # ~8 min, 1 process
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_entre_suenos.py humo     # short life
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("mundo_propio_foto", HERE / "exp_mundo_propio_foto.py")
k10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k10)
g, k7, co = k10.g, k10.k7, k10.co
ms = g.ms

from zeta_life.kernel import contextual_world_model as cwm  # noqa: E402

VENTANA = 150
LOG: dict = {}
_orig = cwm.ContextualWorldModel._decide


def main(escala: dict, nombre: str) -> None:
    par, gm = 0, "A"
    nb, nn, _ = escala["vida"]
    t0 = (nb + nn) * g.D
    casa = g.papeles(par)[gm]
    probes = ms.sondas()

    def _decide(self, obs) -> None:
        _orig(self, obs)
        if t0 - VENTANA <= self._t <= t0:
            e = co.errores_sonda(self.experts[self.active], *probes[casa])
            LOG.setdefault(id(self), []).append((self._t, float(e[ms.QUEMA:].mean())))

    cwm.ContextualWorldModel._decide = _decide
    k7.DATA = ROOT / "data" / "mundo_propio_foto" / "entre_suenos"
    k7.DATA.mkdir(parents=True, exist_ok=True)
    x = k7.vivir(("coin", par, gm, escala, "una", "entre_suenos", False))
    (k7.DATA / "entre_suenos.npz").unlink()
    k7.DATA.rmdir()
    principal = max(LOG.values(), key=len)  # the main model; assay clones log only a tick or two
    v = np.array([e for _, e in principal])
    lines = [
        "=" * 80,
        "§K10 MEASUREMENT -- the slept home expert between two sleeps (coin, pair 0, twin A)",
        "=" * 80,
        f"exile starts at model tick {t0}; the kernel dreams every 50 steps",
        "model tick: home probe of the active expert (after its online step, before that tick's sleep)",
        " ".join(f"{t}:{e:.3f}" for t, e in principal),
        f"over {len(v)} ticks: median {np.median(v):.3f}, mean {v.mean():.3f}, max {v.max():.3f}, "
        f"> 0.05 in {(v > 0.05).sum()}, > 0.1 in {(v > 0.1).sum()}",
        f"block-end oracle (as the experiments record it, right after a sleep), last childhood block: "
        f"{x['oraculo'][nb + nn - 1, casa]:.3f}",
    ]
    print("\n".join(lines))
    (ROOT / "results" / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "humo" in sys.argv[1:]:
        main(g.HUMO, "mundo_propio_entre_suenos_humo")
    else:
        main(g.ESCALA, "mundo_propio_entre_suenos")
