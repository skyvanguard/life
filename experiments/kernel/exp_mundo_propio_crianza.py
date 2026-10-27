"""
§K5 -- THE PRICE OF IDENTITY AND WHERE IT LIVES: a plural childhood against
rigidity, and a drift null for the declared identity module (docs/MUNDO_PROPIO.md;
pre-registered 2026-10-26, after §K4 and its replication, before any run).

WHY. §K4 (replicated, 24 pairs): twins raised in different worlds stay different
after a shared exile, IDENTIDAD (por el sueño). Two things were left open by it.
(1) The price: raised in ONE world, the kernel that keeps its childhood enters a
never-lived world worse than the kernel without sleep (RIGIDEZ 12/12, pre-registered
in the replication; 11/12 post hoc in the test). In §K3, raised among three regimes,
the same kernel learned to infer the regime. Does a plural childhood remove the
price without losing the identity? (2) Where it lives: the twins' self_embedding
distance did not shrink in the exile (it grew in the replication), but with no null
nobody can say whether it carries the life or is just drift.

Q1 -- CRIANZA. Same twins, same roles (gemelos.papeles), same exile and assays as
§K4; only the childhood changes. "una" = §K4 (its stored lives, data/
mundo_propio_gemelos, are REUSED, not re-run: the code path is verified identical
by re-running one life, max diff must be 0). "dos" = the 18 childhood blocks
alternate home and a SCHOOL -- the regime N, shared by both twins, never lived in
§K4 -- with the last childhood block at home (blocks 1,3,...,17 at home; 0,2,...,16
at school: 9 + 9, of them babbling 1 + 2). Declared: the home gets half the
childhood; the sibling's home and X stay never lived for each twin, so the §K4
rigidity readouts keep their meaning, and at T1 both crianzas assay from home.
Arms error_x4 and kernel (no sleep) in both crianzas.
  costo(arm, crianza, pair) = the T1 cost in the sibling's home (mean of twins;
  §K4's RIGIDEZ readout); brecha = costo(error_x4) - costo(kernel), the price of
  the sleep.
  ACHICA   (primary)   brecha(dos) < brecha(una), paired by pair, >= 10/12.
  CONSERVA             H(T2) > 0 on error_x4 under "dos" (the §K4 PERSISTE), >= 10/12.
  INVIERTE (secondary) under "dos", costo(error_x4) < costo(kernel), >= 10/12: the
                       sleep turns from a price into an advantage.
  VERDICT  no ACHICA -> LA RIGIDEZ SE QUEDA; ACHICA without CONSERVA -> MENOS
           RIGIDO, SIN IDENTIDAD; ACHICA and CONSERVA -> MENOS RIGIDO, CON IDENTIDAD
           (", y la invierte" with INVIERTE).
  Reported: FLEXIBLE (costo(error_x4, dos) < costo(error_x4, una)) and the same on
  kernel (a generic effect of practising regime switches), the first exile block
  (e_early of block 18, mean of twins) and stuck blocks per crianza, H at T1/Tm/T2,
  kernel PERSISTE under "dos", the probe (home, sibling, X, school).

Q2 -- DERIVA. Each §K4 error_x4 twin (pairs as above, crianza "una") is re-lived
with OTHER DICE: the same weights at birth (torch.manual_seed(pair)), the same home
and exile and the same assay draws, but torch reseeded after construction
(50000 + pair) and other test/babbling draws (rng 58000 + pair): the same life up to
chance, divergent from tick 0 as the §K4 twins are.
  d_mundo(T) = ||yo_A - yo_B|| (§K4 twins: other world, same dice);
  d_dados(T) = mean(||yo_A - yo_A'||, ||yo_B - yo_B'||) (same world, other dice).
  CONTROL (the yardstick reads) the same comparison on the world model's probe
          profile (the 4 regime probes at the block before the assay): d_mundo >
          d_dados at T1, >= 10/12.
  LLEVA   d_mundo > d_dados on the self_embedding at T1, >= 10/12: it carries
          something of the world beyond chance.
  NIÑEZ   the same at T2 (after the exile), >= 10/12: it carries the identity.
  VERDICT no CONTROL -> LA VARA NO LEE; no LLEVA -> DERIVA; LLEVA without NIÑEZ ->
          LLEVA LA VIDA, NO LA NIÑEZ; both -> EL YO LLEVA LA NIÑEZ.
  Reported: the probe control at T2, the medians, the dice twins' control (e_late).

SMOKE TEST (`humo`, pair 0, short life): the 'una' path reproduces the stored §K4
life (max diff 0); the dice twin is born with the same self_embedding (diff 0) and
its life diverges; the 'dos' schedule is home, school, home, then the exile.
PREDICTIONS (written before any run): Q1 -- ACHICA passes (with two regimes the
world model learns to read its error as "the regime changed", as in §K3, so a new
world is a new context instead of a confident mistake); CONSERVA passes (9 home
blocks still fit the sleep buffer); INVIERTE fails (the sleep still replays the
old worlds while it enters a new one). Q2 -- CONTROL passes, DERIVA (the
self_embedding is an EMA, tau ~100 ticks, of the reflected state, and a kernel
that controls well sees ~C in any world). The smoke test already showed d_mundo > d_dados on
one short pair (3.6 vs 1.3); the prediction stays as written.

REPLICATION, pre-registered with the test: pairs 12-23 (§K4 replication lives
reused for "una"), the same rule, launched right after the test unless a bug is
found (any change recorded). REPLICADO per question if its verdict repeats.

72 new lives + 1 verification life per run; 3 CPU processes, one torch thread each
(the declared kernel exception); ~95 min.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_crianza.py replica   # pairs 12-23
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("mundo_propio_gemelos", HERE / "exp_mundo_propio_gemelos.py")
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

RESULTS = ROOT / "results"
DATA = ROOT / "data" / "mundo_propio_crianza"
N_OK = g.N_OK
ARMS = g.ARMS
GEMELOS = g.GEMELOS
PAIRS = g.PAIRS
DADOS = 50_000


def vivir(args: tuple) -> dict:
    return g.vivir(args)


def humo(escala: dict) -> str:
    return "_humo" if escala == g.HUMO else ""


def cargar_k4(brazo: str, par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K4 life (crianza "una"), in the shape vivir() returns."""
    x = dict(np.load(g.DATA / f"{brazo}_{par}_{gemelo}{humo(escala)}.npz"))
    x.update(brazo=brazo, par=par, gemelo=gemelo, crianza="una",
             T=[t for t, _ in escala["ensayos"]], bloque=[b for _, b in escala["ensayos"]],
             vida_bloques=escala["vida"])
    return x


def tareas(pares: tuple, escala: dict) -> list[tuple[str, tuple]]:
    sufijo = humo(escala)
    t = [("verif", ("error_x4", pares[0], "A", escala,
                    {"dir": DATA, "archivo": f"verif_error_x4_{pares[0]}_A{sufijo}"}))]
    for p in pares:
        for a in ARMS:
            for gm in GEMELOS:
                t.append(("dos", (a, p, gm, escala,
                                  {"crianza": "dos", "dir": DATA, "archivo": f"dos_{a}_{p}_{gm}{sufijo}"})))
        for gm in GEMELOS:
            t.append(("dados", ("error_x4", p, gm, escala,
                                {"dados": DADOS + p, "pruebas": 8000 + DADOS + p, "dir": DATA,
                                 "archivo": f"dados_error_x4_{p}_{gm}{sufijo}"})))
    return t


def correr(pares: tuple, escala: dict) -> dict:
    t = tareas(pares, escala)
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, [args for _, args in t]))
    V = {"verif": {}, "dos": {}, "dados": {}}
    for (cond, _), x in zip(t, vidas):
        V[cond][(x["brazo"], x["par"], x["gemelo"])] = x
    return V


def diferencia(x: dict, ref: dict) -> float:
    """Max |difference| over every stored array (nan == nan)."""
    m = 0.0
    for k in ref:
        if not isinstance(ref[k], np.ndarray):
            continue
        a, b = np.asarray(x[k], dtype=float), np.asarray(ref[k], dtype=float)
        if a.shape != b.shape or not np.array_equal(np.isnan(a), np.isnan(b)):
            return float("inf")
        if a.size:
            m = max(m, float(np.nanmax(np.abs(a - b))) if np.isfinite(a).any() else 0.0)
    return m


def costo(V: dict, brazo: str, p: int) -> float:
    return g.afuera(V, brazo, p, "T1")


def exilio(V: dict, brazo: str, p: int) -> float:
    """e_early of the first exile block, mean of the twins."""
    nb, nn, _ = V[(brazo, p, "A")]["vida_bloques"]
    return float(np.mean([g.por_bloque(V[(brazo, p, gm)], p)[nb + nn]["early"] for gm in GEMELOS]))


def atascos(V: dict, brazo: str, pares: tuple) -> tuple[int, int]:
    """(stuck acting blocks, twins with any) -- late > 0.3, the §K1 readout."""
    bloques, gemelos = 0, 0
    for p in pares:
        for gm in GEMELOS:
            n = sum(b["late"] > 0.3 for b in g.por_bloque(V[(brazo, p, gm)], p) if b["fase"] == "act")
            bloques, gemelos = bloques + n, gemelos + (n > 0)
    return bloques, gemelos


def veredicto_crianza(achica: int, conserva: int, invierte: int) -> str:
    """The pre-registered §K5 Q1 rule."""
    if achica < N_OK:
        return "LA RIGIDEZ SE QUEDA"
    if conserva < N_OK:
        return "MENOS RIGIDO, SIN IDENTIDAD"
    return "MENOS RIGIDO, CON IDENTIDAD" + (", y la invierte" if invierte >= N_OK else "")


def veredicto_yo(control: int, lleva: int, ninez: int) -> str:
    """The pre-registered §K5 Q2 rule."""
    if control < N_OK:
        return "LA VARA NO LEE"
    if lleva < N_OK:
        return "DERIVA"
    if ninez < N_OK:
        return "LLEVA LA VIDA, NO LA NIÑEZ"
    return "EL YO LLEVA LA NIÑEZ"


def perfil(x: dict, j: int) -> np.ndarray:
    """The 4 regime probes at the block before assay j."""
    return x["sonda"][x["bloque"][j] - 1]


def informe(V: dict, U: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float,
            verif: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    D_, Q = V["dos"], V["dados"]
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}; crianza 'una' = stored §K4 lives, 'dos' = home/school alternating; "
        f"dice twins of error_x4 (una); run {minutos:.1f} min")
    out(f"verification: the 'una' code path re-run on error_x4 pair {pares[0]} twin A vs the stored §K4 life, "
        f"max diff {verif}")
    out("")
    out("Q1 -- CRIANZA")
    out("T1 cost in the sibling's home (mean of twins; median over pairs) | first exile block e_early | "
        "stuck blocks (twins)")
    for crianza, W in (("una", U), ("dos", D_)):
        for a in ARMS:
            b, tw = atascos(W, a, pares)
            out(f"  {crianza:>3} {a:>8} | {np.median([costo(W, a, p) for p in pares]):.3f} | "
                f"{np.median([exilio(W, a, p) for p in pares]):.3f} | stuck {b} ({tw}/{2 * n})")
    out("")
    out("H_early (cross) medians and H>0, per crianza x arm x assay")
    H = {}
    for crianza, W in (("una", U), ("dos", D_)):
        for a in ARMS:
            cel = []
            for t in T:
                h = [g.cruce(g.leer(W, a, p, t, "early")) for p in pares]
                H[(crianza, a, t)] = h
                cel.append(f"{t} {np.median(h):+.3f} ({sum(v > 0 for v in h)}/{n})")
            out(f"  {crianza:>3} {a:>8} | " + " | ".join(cel))
    out("")
    out("probe under 'dos' (median over twins and pairs): home | sibling | X | school")
    for a in ARMS:
        for j, t in enumerate(T):
            if escala["ensayos"][j][1] == 0:
                continue
            cel = []
            for rol in ("home", "sibling", "X", "N"):
                vals = []
                for p in pares:
                    pa = g.papeles(p)
                    for gm, otro in (("A", "B"), ("B", "A")):
                        x = D_[(a, p, gm)]
                        r = {"home": gm, "sibling": otro, "X": "X", "N": "N"}[rol]
                        b = x["bloque"][j]
                        vals.append(x["sonda"][b - 1, pa[r]])
                cel.append(f"{np.median(vals):.3f}")
            out(f"  {a:>8} {t:>3} | " + " | ".join(cel))
    c = {(cr, a): [costo(W, a, p) for p in pares] for cr, W in (("una", U), ("dos", D_)) for a in ARMS}
    brecha = {cr: [x - y for x, y in zip(c[(cr, "error_x4")], c[(cr, "kernel")])] for cr in ("una", "dos")}
    achica = sum(x < y for x, y in zip(brecha["dos"], brecha["una"]))
    conserva = sum(v > 0 for v in H[("dos", "error_x4", T[-1])])
    invierte = sum(x < y for x, y in zip(c[("dos", "error_x4")], c[("dos", "kernel")]))
    out("")
    out("brecha (error_x4 - kernel T1 cost) per pair:")
    for cr in ("una", "dos"):
        out(f"  {cr}: " + str([round(v, 3) for v in brecha[cr]]))
    ex = {(cr, a): [exilio(W, a, p) for p in pares] for cr, W in (("una", U), ("dos", D_)) for a in ARMS}
    out("-" * 80)
    out(f"ACHICA   (primary)   brecha(dos) < brecha(una): {achica}/{n} "
        f"(medians {np.median(brecha['dos']):+.3f} vs {np.median(brecha['una']):+.3f})")
    out(f"CONSERVA             H(T2) > 0 on error_x4 under dos: {conserva}/{n}")
    out(f"INVIERTE (secondary) under dos, cost error_x4 < kernel: {invierte}/{n}")
    out(f"(reported) FLEXIBLE  cost dos < una: error_x4 "
        f"{sum(x < y for x, y in zip(c[('dos', 'error_x4')], c[('una', 'error_x4')]))}/{n}, kernel "
        f"{sum(x < y for x, y in zip(c[('dos', 'kernel')], c[('una', 'kernel')]))}/{n}")
    out(f"(reported) first exile block, error_x4 dos < una: "
        f"{sum(x < y for x, y in zip(ex[('dos', 'error_x4')], ex[('una', 'error_x4')]))}/{n}; under dos "
        f"error_x4 > kernel: {sum(x > y for x, y in zip(ex[('dos', 'error_x4')], ex[('dos', 'kernel')]))}/{n}")
    out(f"(reported) kernel PERSISTE under dos: {sum(v > 0 for v in H[('dos', 'kernel', T[-1])])}/{n}; paired "
        f"H(T2) error_x4 > kernel under dos: "
        f"{sum(x > y for x, y in zip(H[('dos', 'error_x4', T[-1])], H[('dos', 'kernel', T[-1])]))}/{n}")
    v1 = veredicto_crianza(achica, conserva, invierte) if n == len(PAIRS) else "(n < 12: no verdict)"
    out(f"VERDICT Q1 (pre-registered rule): {v1}")
    out("")
    out("Q2 -- DERIVA (error_x4, crianza una)")
    lect = {}
    for campo in ("yo", "probe"):
        for j, t in enumerate(T):
            dm, dd = [], []
            for p in pares:
                A, B = U[("error_x4", p, "A")], U[("error_x4", p, "B")]
                A2, B2 = Q[("error_x4", p, "A")], Q[("error_x4", p, "B")]
                if campo == "yo":
                    f = lambda x: x["yo"][j]  # noqa: E731
                else:
                    if A["bloque"][j] == 0:
                        continue
                    f = lambda x: perfil(x, j)  # noqa: E731
                dm.append(float(np.linalg.norm(f(A) - f(B))))
                dd.append(float(np.mean([np.linalg.norm(f(A) - f(A2)), np.linalg.norm(f(B) - f(B2))])))
            if not dm:
                continue
            k = sum(x > y for x, y in zip(dm, dd))
            lect[(campo, t)] = k
            out(f"  {campo:>5} {t:>3} | d_mundo {np.median(dm):.4f} | d_dados {np.median(dd):.4f} | "
                f"d_mundo > d_dados {k}/{len(dm)}")
    late = [np.mean([b["late"] for b in g.por_bloque(Q[("error_x4", p, gm)], p)[-5:]])
            for p in pares for gm in GEMELOS]
    out(f"  dice twins' control: median e_late of the last 5 exile blocks {np.median(late):.3f}")
    out("-" * 80)
    control, lleva, ninez = lect[("probe", "T1")], lect[("yo", "T1")], lect[("yo", T[-1])]
    out(f"CONTROL  probe profile d_mundo > d_dados at T1: {control}/{n} (T2 {lect[('probe', T[-1])]}/{n})")
    out(f"LLEVA    self_embedding d_mundo > d_dados at T1: {lleva}/{n}")
    out(f"NIÑEZ    self_embedding d_mundo > d_dados at T2: {ninez}/{n}")
    v2 = veredicto_yo(control, lleva, ninez) if n == len(PAIRS) else "(n < 12: no verdict)"
    out(f"VERDICT Q2 (pre-registered rule): {v2}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines), encoding="utf-8")
    (RESULTS / f"{nombre}_lecturas.json").write_text(json.dumps({
        "brecha": brecha, "costo": {f"{k[0]}_{k[1]}": v for k, v in c.items()},
        "H": {f"{k[0]}_{k[1]}_{k[2]}": v for k, v in H.items()},
        "q2": {f"{k[0]}_{k[1]}": v for k, v in lect.items()}, "veredictos": [v1, v2]}), encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str) -> None:
    t0 = time.time()
    V = correr(pares, escala)
    U = {(a, p, gm): cargar_k4(a, p, gm, escala) for a in ARMS for p in pares for gm in GEMELOS}
    verif = diferencia(V["verif"][("error_x4", pares[0], "A")], U[("error_x4", pares[0], "A")])
    if escala == g.HUMO:
        x0, q0 = U[("error_x4", pares[0], "A")], V["dados"][("error_x4", pares[0], "A")]
        print(f"dice twin at birth: |yo T0 - §K4 yo T0| max {np.abs(q0['yo'][0] - x0['yo'][0]).max():.2e}; "
              f"life differs: max |dist| diff {np.abs(q0['dist'] - x0['dist']).max():.3f}")
        nb, nn, ne = escala["vida"]
        pa = g.papeles(pares[0])
        print("dos schedule (twin A):", [g.regimen(pa, "A", v, nb, nn, "dos") for v in range(nb + nn + ne)],
              "roles", pa)
    informe(V, U, pares, escala, nombre, titulo, (time.time() - t0) / 60, verif)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_crianza_humo", "§K5 SMOKE TEST (pair 0, short life)")
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_crianza_replica",
             "§K5 REPLICATION (pairs 12-23) -- the price of identity and where it lives")
    else:
        main(PAIRS, g.ESCALA, "mundo_propio_crianza", "§K5 -- the price of identity and where it lives")
