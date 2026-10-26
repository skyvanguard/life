"""Experience v3 -- de-saturating what the kernel sees of Yvyra's life.

Why this exists (``docs/PHASE_B_DESIGN.md``, "v3"): in 893 real ticks the kernel
received only 15 distinct 4-axis vectors, built from near-binary flags (mode,
"Wikipedia loaded", word-count thresholds, "mentions Fran") on a fixed AAA-BBB
schedule. The world model learned the schedule, so Psi became a clock detector:
in the last 400 ticks it left ALTA in 4% of ticks, only right after a mode
switch, and never inside an introspection run. Nothing of WHAT she lived in a
tick reached the kernel.

Two changes, both here:

1. LIFE (``elegir_evento``): each introspection tick draws one condition from a
   seeded, persisted generator -- FOCO (the rotating question, as before),
   MEMORIA (one of her own past reflections is shown to her), INTRUSION (an
   unrelated encyclopedia fragment she did not choose cuts into the question),
   VACIO (no question at all). The condition changes what she lives; the kernel
   never sees its label.
2. AXES (``ejes_v3``): continuous, objective features of how she RESPONDED --
   lexical novelty against her recent responses, self-reference density, how
   much of the material she received she took up, and length -- plus the
   structural flags (research, net, notify) the old axes had. The sentiment
   lexicon of ``integration_sentiment`` is EXCLUDED from every lexical feature,
   so a Phase-B correlation between sentiment and Psi cannot be manufactured by
   the same words feeding both.

Declared hands: the four condition probabilities, the axis weights, the history
length, the self-reference and length normalisers. They are constants below.

CLI (called by the heartbeat; one JSON state file holds history, pools and the
event counter)::

    python -m zeta_life.bridge.experience evento --state S --out FRAG
    python -m zeta_life.bridge.experience extracto --state S --file F
    python -m zeta_life.bridge.experience ejes --state S --text T --material M \\
        --research 0 --net 0 --notify 0 --condicion foco --log L
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .integration_sentiment import FRAGMENTED, INTEGRATED

CONDICIONES = ("foco", "memoria", "intrusion", "vacio")
PROBS = (0.50, 0.20, 0.15, 0.15)
HISTORIA = 10            # responses kept for lexical novelty
POOL_MEMORIA = 30        # past introspection responses available to MEMORIA
POOL_EXTRACTOS = 20      # encyclopedia fragments available to INTRUSION
FRAG_CHARS = 600         # length of the fragment shown to her
SELF_NORM = 0.08         # self-reference density that maps to 1.0
WORDS_FULL = 200         # response length that maps to 1.0
MIN_LEN = 5              # content words have at least this many letters
TEXTO_MAX = 4000         # chars kept per stored response

_SENTIMENT_STEMS = tuple(INTEGRATED) + tuple(FRAGMENTED)
_SELF = frozenset({"yo", "me", "mi", "mis", "conmigo", "mio", "mia", "mios", "mias"})
_STOP = frozenset("""
    about acerca ademas ahora algo algun alguna algunas alguno algunos alla alli
    antes aquel aquella aquello aquellos aqui cada casi como cosas cuando cual
    cuales cualquier cuanto desde donde durante entonces entre esas ese eso esos
    esta estaba estaban estamos estan estar estas este esto estos fuera hacer
    hacia hasta haya mientras mismo mucho muchos nada nadie ningun ninguna nosotros
    nuestra nuestro otra otras otro otros para pero poco porque puede pueden
    quien quienes sabes sobre solo somos tambien tanto tenes tengo tiene tienen
    todas todavia todos tuyo usted vamos vemos vosotros
""".split())


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    """Lower-case, accent-stripped alphabetic tokens (NFKD turns ñ into n)."""
    return re.findall(r"[a-z]+", _norm(text))


def content_words(text: str) -> set[str]:
    """Content-word types: long, not stop words, not from the sentiment lexicon."""
    return {w for w in tokens(text)
            if len(w) >= MIN_LEN and w not in _STOP and not w.startswith(_SENTIMENT_STEMS)}


def lexical_novelty(text: str, history: list[str]) -> float:
    """Fraction of the response's content-word types absent from recent responses."""
    cw = content_words(text)
    if not cw:
        return 0.0
    seen: set[str] = set()
    for h in history:
        seen |= content_words(h)
    return len(cw - seen) / len(cw)


def self_reference(text: str) -> float:
    """Density of first-person singular words, scaled so SELF_NORM -> 1.0."""
    tk = tokens(text)
    if not tk:
        return 0.0
    return min(1.0, sum(w in _SELF for w in tk) / len(tk) / SELF_NORM)


def material_overlap(text: str, material: str) -> float:
    """How much of the material she received she took up (0 if there was none)."""
    cm = content_words(material)
    ct = content_words(text)
    if not cm or not ct:
        return 0.0
    return min(1.0, len(ct & cm) / min(len(cm), 15))


def _clip(x: float) -> float:
    return min(1.0, max(0.0, x))


def ejes_v3(*, text: str, history: list[str], material: str,
            research: bool, net: bool, notified: bool) -> tuple[float, float, float, float]:
    """The 4 axes (novedad, introspeccion, conexion, resolucion) in [0, 1]."""
    r = 1.0 if research else 0.0
    words = len(tokens(text))
    nov = 0.20 + 0.30 * r + 0.15 * (1.0 if net else 0.0) + 0.35 * lexical_novelty(text, history)
    intro = 0.30 + 0.30 * (1.0 - r) + 0.40 * self_reference(text)
    con = 0.10 + 0.50 * (1.0 if notified else 0.0) + 0.40 * material_overlap(text, material)
    res = 0.15 + 0.15 * r + 0.70 * min(1.0, words / WORDS_FULL)
    return (_clip(nov), _clip(intro), _clip(con), _clip(res))


@dataclass
class Estado:
    """Persisted experience state (one JSON file next to the kernel state)."""

    seed: int = 0
    contador: int = 0
    historia: list[str] = field(default_factory=list)
    memoria: list[str] = field(default_factory=list)
    extractos: list[str] = field(default_factory=list)

    @classmethod
    def cargar(cls, path: Path, seed: int = 0) -> Estado:
        if not path.exists():
            return cls(seed=seed)
        d = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{k: d[k] for k in ("seed", "contador", "historia", "memoria", "extractos") if k in d})

    def guardar(self, path: Path) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.__dict__, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)


def elegir_evento(est: Estado) -> tuple[str, str]:
    """Draw this introspection tick's condition and the fragment shown to her.

    Deterministic given (seed, counter). MEMORIA and INTRUSION fall back to FOCO
    when their pool is still empty. Returns (condition, fragment text).
    """
    rng = random.Random(f"{est.seed}:{est.contador}")
    est.contador += 1
    cond = rng.choices(CONDICIONES, weights=PROBS, k=1)[0]
    if cond == "memoria" and est.memoria:
        return cond, rng.choice(est.memoria)[:FRAG_CHARS]
    if cond == "intrusion" and est.extractos:
        return cond, rng.choice(est.extractos)[:FRAG_CHARS]
    if cond in ("memoria", "intrusion"):
        return "foco", ""
    return cond, ""


def registrar_respuesta(est: Estado, text: str, introspeccion: bool) -> None:
    """Add her response to the rolling history (and to the MEMORIA pool if A)."""
    t = text[:TEXTO_MAX]
    est.historia = (est.historia + [t])[-HISTORIA:]
    if introspeccion and t.strip():
        est.memoria = (est.memoria + [t])[-POOL_MEMORIA:]


def _leer(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="zeta_life.bridge.experience")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("evento")
    e.add_argument("--state", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--seed", type=int, default=0)
    x = sub.add_parser("extracto")
    x.add_argument("--state", required=True)
    x.add_argument("--file", required=True)
    a = sub.add_parser("ejes")
    a.add_argument("--state", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--material", default=None)
    a.add_argument("--research", type=int, default=0)
    a.add_argument("--net", type=int, default=0)
    a.add_argument("--notify", type=int, default=0)
    a.add_argument("--condicion", default="")
    a.add_argument("--log", default=None)
    args = ap.parse_args(argv)

    path = Path(args.state)
    est = Estado.cargar(path, seed=getattr(args, "seed", 0))
    if args.cmd == "evento":
        cond, frag = elegir_evento(est)
        Path(args.out).write_text(frag, encoding="utf-8")
        est.guardar(path)
        print(cond)
        return 0
    if args.cmd == "extracto":
        t = _leer(args.file).strip()
        if t:
            est.extractos = (est.extractos + [t[:TEXTO_MAX]])[-POOL_EXTRACTOS:]
            est.guardar(path)
        return 0
    text, material = _leer(args.text), _leer(args.material)
    hist = list(est.historia)
    ax = ejes_v3(text=text, history=hist, material=material, research=bool(args.research),
                 net=bool(args.net), notified=bool(args.notify))
    registrar_respuesta(est, text, introspeccion=not args.research)
    est.guardar(path)
    if args.log:
        rec = {"ts": time.time(), "condicion": args.condicion, "research": args.research,
               "axes": [round(v, 4) for v in ax],
               "novelty": round(lexical_novelty(text, hist), 4), "selfref": round(self_reference(text), 4),
               "overlap": round(material_overlap(text, material), 4), "words": len(tokens(text))}
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(" ".join(f"{v:.2f}" for v in ax))
    return 0


if __name__ == "__main__":
    sys.exit(main())
