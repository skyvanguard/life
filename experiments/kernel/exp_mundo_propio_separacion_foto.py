"""
§K8 mechanism (post hoc, after the test and the replication; docs/MUNDO_PROPIO.md):
why the sleepless repertoire (coin_sin_sueno) does not keep the identity.

The test's hypothesis was a STALE SNAPSHOT: the home expert hovers just above the
absolute threshold, so the pre-streak snapshot would be taken in the childhood and the
exile's spawn would restore it. Two readings:

1. Re-run 6 coin_sin_sueno lives (pairs 0-2) and 2 coin lives (pair 0) with the
   contextual model's _decide instrumented (snapshot taken / dropped, switch / spawn and
   whether a snapshot was restored), on the main world model only (the assay clones are
   filtered out by object id: the main model is the first that decides). The
   instrumentation only reads: each re-run must reproduce its stored life (diff 0).
2. On the stored lives (48 sleepless twins, pairs 0-23): the oracle probe of the home
   world per block -- end of the childhood (block 17), first exile block (18), last (32).

RESULT (2026-10-27): the hypothesis is REFUTED -- the restored snapshot is taken 4-24
ticks into the exile and the running error at the end of the childhood is below the
threshold. The home expert is frozen through the exile but gets worse at its start (the
running error crosses the threshold a few ticks late, so the snapshot holds the first
exile updates) and stays coarse without sleep.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_separacion_foto.py
"""

from __future__ import annotations

import importlib.util
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("mundo_propio_separacion", HERE / "exp_mundo_propio_separacion.py")
k8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k8)
g, k7, cr = k8.g, k8.k7, k8.cr

from zeta_life.kernel import contextual_world_model as cwm  # noqa: E402

LOG: list = []
MAIN: list = []
_orig = cwm.ContextualWorldModel._decide


def _decide(self, obs) -> None:
    if not MAIN:
        MAIN.append(id(self))
    if id(self) != MAIN[0]:
        return _orig(self, obs)
    before, n_ev = self._snapshot, len(self.events)
    _orig(self, obs)
    if len(self.events) > n_ev:
        LOG.append((self.events[-1][0], self._t, before is not None))
    elif before is None and self._snapshot is not None:
        LOG.append(("take", self._t, float(self.running[self.active])))
    elif before is not None and self._snapshot is None:
        LOG.append(("drop", self._t, float(self.running[self.active])))
    if self._t % g.D == 0 and self.running[self.active] is not None:
        LOG.append(("r", self._t, float(self.running[self.active]), self.active))


cwm.ContextualWorldModel._decide = _decide


def una(args: tuple) -> tuple:
    a, p, gm = args
    LOG.clear()
    MAIN.clear()
    archivo = f"foto_{a}_{p}_{gm}"
    x = k7.vivir((a, p, gm, g.ESCALA, "una", archivo, False))
    (k8.DATA / f"{archivo}.npz").unlink()
    ref = (k8.cargar_k7(p, gm, g.ESCALA) if a == "coin"
           else k7.salida((a, p, gm, g.ESCALA, "una"), dict(np.load(k8.DATA / f"una_{a}_{p}_{gm}.npz")), 0.0))
    return a, p, gm, cr.diferencia(x, ref), list(LOG)


def main() -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    nb, nn, ne = g.ESCALA["vida"]
    ex0 = (nb + nn) * g.D
    out("=" * 80)
    out("§K8 MECHANISM -- the snapshot and the home expert without sleep")
    out("=" * 80)
    out(f"1. instrumented re-runs (the childhood ends at tick {ex0})")
    tareas = [("coin_sin_sueno", p, gm) for p in (0, 1, 2) for gm in g.GEMELOS]
    tareas += [("coin", 0, gm) for gm in g.GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        for a, p, gm, dif, log in pool.map(una, tareas):
            takes = [e for e in log if e[0] == "take"]
            r_fin = [e[2] for e in log if e[0] == "r" and e[1] == ex0]
            out(f"{a} pair {p} twin {gm}: re-run diff {dif}; running error of the active expert at the "
                f"end of the childhood {r_fin[0] if r_fin else float('nan'):.3f}; snapshots taken "
                f"{len(takes)}, dropped {sum(e[0] == 'drop' for e in log)}")
            for s in (e for e in log if e[0] == "spawn"):
                previas = [t for t in takes if t[1] <= s[1]]
                u = previas[-1] if previas else None
                out(f"   spawn at tick {s[1]} ({'exile' if s[1] >= ex0 else 'childhood'}), restored a "
                    f"snapshot: {s[2]}; taken at tick {u[1] if u else None} "
                    f"({s[1] - u[1] if u else None} ticks before; r {u[2] if u else float('nan'):.3f})")
    out("")
    out("2. the home oracle of the 48 sleepless twins (pairs 0-23), by block")
    o = np.array([np.load(k8.DATA / f"una_coin_sin_sueno_{p}_{gm}.npz")["oraculo"][:, g.papeles(p)[gm]]
                  for p in range(24) for gm in g.GEMELOS])
    b17, b18, b32 = o[:, nb + nn - 1], o[:, nb + nn], o[:, -1]
    out(f"  end of the childhood (block {nb + nn - 1}) median {np.median(b17):.3f}; first exile block "
        f"{np.median(b18):.3f}; last {np.median(b32):.3f}")
    out(f"  first exile block > end of the childhood in {(b18 > b17).sum()}/48 twins; median jump "
        f"{np.median(b18 - b17):+.3f}")
    out(f"  childhood block-to-block |change| (blocks 10-17), median "
        f"{np.median(np.median(np.abs(np.diff(o[:, 10:nb + nn], axis=1)), axis=1)):.3f}")
    out(f"  frozen through the exile (last == first exile block within 0.002): "
        f"{(np.abs(b32 - b18) < 0.002).sum()}/48")
    (ROOT / "results" / "mundo_propio_separacion_foto_run.txt").write_text("\n".join(lines) + "\n",
                                                                       encoding="utf-8")


if __name__ == "__main__":
    main()
