"""
Experience v3, LIVE: does the de-saturated life make Psi discriminate inside
Yvyra's introspection ticks, and for a cause? (docs/PHASE_B_DESIGN.md, "v3")

PROTOCOL (pre-registered 2026-10-26, before any v3 tick existed). Yvyra runs
with the heartbeat v3 (deploy/zeta/heartbeat/tick.sh, flag `.exp_v3`), Phase B
PAUSED (flag renamed), so she is never shown Psi: this is a silent measurement
of the experience change, continuing her mature identity (kernel checkpoint at
tick 1493, backed up before the switch). Each tick appends one record to
`experience_v3.jsonl` (mode, condition, axes, psi_real) and one to
`experience_features.jsonl` (novelty, self-reference, uptake, words).

READOUT: introspection (mode A) ticks from the 31st v3 tick on (the first 30
are the kernel's re-adaptation to a new input distribution), at least 50 of
them. Levels as in Phase B: ALTA >= 0.85, BAJA < 0.40.

VERDICT (written before the first v3 tick):
  DESATURADA  0.30 <= frac(ALTA) <= 0.75 among readout introspection ticks.
  COLAPSO     frac(BAJA) > 0.60 (pinned low is saturation too).
  SATURADA    otherwise (frac(ALTA) > 0.75).
SECONDARY READINGS (inform, do not decide):
  CAUSA     frac(not ALTA) higher under INTRUSION+VACIO than under FOCO
            (one-sided Fisher p < 0.10): the conditions of her life move Psi.
  NO RELOJ  frac(not ALTA) >= 0.20 among readout introspection ticks that do
            NOT follow a mode switch: the dips are not the schedule clock.
  CONTENIDO per condition: median novelty, uptake and words (did the condition
            change how she responded?).

    PYTHONPATH=src python experiments/kernel/exp_experience_v3_live.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

STATE = Path.home() / ".hermes" / "zeta" / "state"
WARM = 30
MIN_READ = 50
HI, LO = 0.85, 0.40
RESULTS = Path(__file__).resolve().parents[2] / "results"


def leer(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def fisher_una_cola(a: int, b: int, c: int, d: int) -> float:
    """P(X >= a) for the 2x2 table [[a, b], [c, d]] under the hypergeometric null."""
    n1, n2, k = a + b, c + d, a + c
    tot = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot if tot else 1.0


def main() -> int:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    recs = leer(STATE / "experience_v3.jsonl")
    feats = leer(STATE / "experience_features.jsonl")
    out("=" * 78)
    out("EXPERIENCE v3 LIVE: does Psi discriminate inside Yvyra's introspection, for a cause?")
    out("=" * 78)
    out(f"v3 ticks: {len(recs)} (feature records {len(feats)}); axes v3 in {sum(r.get('ejes') == 'v3' for r in recs)}; "
        f"kernel ok in {sum(bool(r.get('ok')) for r in recs)}")
    modos = [r["mode"] for r in recs]
    sw = [False] + [modos[i] != modos[i - 1] for i in range(1, len(modos))]
    lect = [(r, s) for i, (r, s) in enumerate(zip(recs, sw))
            if i >= WARM and r["mode"] == "A" and r.get("psi_real") is not None]
    out(f"readout introspection ticks (from v3 tick {WARM + 1} on): {len(lect)} (need >= {MIN_READ})")
    if not lect:
        out("no readout ticks yet")
        return 0
    psi = np.array([r["psi_real"] for r, _ in lect])
    alta, baja = float(np.mean(psi >= HI)), float(np.mean(psi < LO))
    out(f"levels: ALTA {alta:.2f}  MEDIA {np.mean((psi >= LO) & (psi < HI)):.2f}  BAJA {baja:.2f}")
    out("")
    out("-" * 78)
    out("BY CONDITION (readout introspection ticks)")
    por = {}
    for r, _ in lect:
        por.setdefault(r["condicion"], []).append(r["psi_real"])
    for c in ("foco", "memoria", "intrusion", "vacio"):
        p = np.array(por.get(c, []))
        if len(p):
            out(f"  {c:<10} n={len(p):>3}  not ALTA {np.mean(p < HI):.2f}  median psi {np.median(p):.3f}")
    duro = [x for c in ("intrusion", "vacio") for x in por.get(c, [])]
    foco = por.get("foco", [])
    a, b = sum(x < HI for x in duro), sum(x >= HI for x in duro)
    c_, d = sum(x < HI for x in foco), sum(x >= HI for x in foco)
    pf = fisher_una_cola(a, b, c_, d) if duro and foco else 1.0
    causa = bool(duro and foco and a / len(duro) > c_ / len(foco) and pf < 0.10)
    out(f"  CAUSA     not ALTA intrusion+vacio {a}/{len(duro)} vs foco {c_}/{len(foco)} (Fisher one-sided p {pf:.3f}) -> {'SI' if causa else 'no'}")
    sin = np.array([r["psi_real"] for r, s in lect if not s])
    noreloj = len(sin) > 0 and float(np.mean(sin < HI)) >= 0.20
    out(f"  NO RELOJ  not ALTA among ticks not after a switch: {np.mean(sin < HI) if len(sin) else float('nan'):.2f} (n={len(sin)}) -> {'SI' if noreloj else 'no'}")
    if len(feats) == len(recs):
        out("")
        out("CONTENT by condition (introspection ticks, all v3): median novelty / uptake / words")
        fa = [(r["condicion"], f) for r, f in zip(recs, feats) if r["mode"] == "A"]
        for c in ("foco", "memoria", "intrusion", "vacio"):
            fs = [f for cc, f in fa if cc == c]
            if fs:
                out(f"  {c:<10} n={len(fs):>3}  novelty {np.median([f['novelty'] for f in fs]):.2f}  "
                    f"uptake {np.median([f['overlap'] for f in fs]):.2f}  words {np.median([f['words'] for f in fs]):.0f}")
    out("")
    out("=" * 78)
    out(f"VERDICT (rule written before the first v3 tick; readout n={len(lect)}"
        + ("" if len(lect) >= MIN_READ else f" < {MIN_READ}: PROVISIONAL") + ")")
    if baja > 0.60:
        out("=> COLAPSO: Psi pinned low; the new experience is as uninformative as the old, from the other side.")
    elif 0.30 <= alta <= 0.75:
        out("=> DESATURADA: Psi now visits MEDIA/BAJA inside introspection" + (" and the conditions of her life move it." if causa else "."))
    else:
        out("=> SATURADA: Psi still sits in ALTA inside introspection.")
    c = Counter(r["condicion"] for r, _ in lect)
    out(f"(conditions in readout: {dict(c)})")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "experience_v3_live_run.txt").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
