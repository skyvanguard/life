"""
§K14 -- THE SCHOOL: does the full arm (§K13's coin_regreso) keep its three gains under the
other upbringing, §K5's "dos"?
(docs/MUNDO_PROPIO.md; written 2026-10-28, before the smoke test and the calibration)

WHY. §K11-§K13 were run under "una" only (the childhood at home). There the full arm,
coin_regreso (coin + a slow wake while an expert explains its stream, the full rate while
it does not, and a slow return), is the first arm that does three things at once (§K13,
replicated): it keeps what sleep consolidates (awake home oracle 0.008 vs coin 0.042,
24/24), enters the never-lived world better than coin (first exile block 0.367 vs 0.560)
and returns home better than coin (home T2 0.111 vs 0.145, 22/24). All three were measured
in one life. "dos" (§K5, §K7: home and the school N alternating through the childhood,
ending at home) is the other life the program has: three experts instead of two, and the
home expert comes back from the school seven times in the childhood. Under §K13's rule
each of those is a slow return, which "una" never had. Is the full arm a property of the
kernel or of the one upbringing it was built in?

DESIGN. Two arms under "dos", with §K4's life, roles, exile and assays and §K7's loop:
coin, re-run (its §K7 "dos" lives have no awake probe, which §K11 added; the probe only
reads, so every re-run twin must equal its stored §K7 life on every stored key: 24
verifications per run), and coin_regreso, §K13's arm unchanged. Nothing is tuned.
Declared: no coin_vigilia or coin_madurez under "dos". The question is the full arm
against the repertoire it improves, not the attribution among its three hands.
Declared readout change: under "dos" only the last childhood blocks AT HOME erode the
home expert awake (only the active expert learns awake; all of them sleep), so the
awake home oracle is the median over the last ULTIMOS childhood blocks lived at home
(under "una" these are §K11's last ULTIMOS childhood blocks).

VERIFICATION. Every coin re-run equals its stored §K7 "dos" life on every stored key (max
diff 0) -- else stop: a bug.

Readouts per pair (mean of the twins): the awake home oracle (above); the first exile
block (e_early); the home cost at T1/Tm/T2 and abroad (the sibling's home) at T1/T2;
H(T1/Tm/T2); per home assay, the cost after the switch to h (§K13); the childhood
returns -- the mean e_early of the childhood blocks at home after the first (7 returns
from the school: 8 home blocks, the childhood's first and last among them) and at the
school after the first (6 of 7).

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019). E = coin_regreso, C = coin,
both under "dos".
  CONSERVA_D (primary) awake home oracle E < C.
  ENTRA_D    (primary) first exile block E < C.
  VUELVE_D   (primary) home cost at T2 E < C.
  PERSISTE_D (primary) H(T2) E > 0.
  RIGIDO_D   (primary, the price) abroad cost E > C at T1 or at T2 (>= 10/12 in either).
  VERDICT  no PERSISTE_D -> SIN IDENTIDAD EN LA ESCUELA; else any of CONSERVA_D, ENTRA_D,
           VUELVE_D missing -> NO AGUANTA (naming the ones that fail); all three without
           RIGIDO_D -> AGUANTA LA ESCUELA; all three and RIGIDO_D -> AGUANTA, MAS RIGIDO
           AFUERA.
  Secondary: NINEZ_D the childhood returns home E < C; ESCUELA_D the returns to the school
  E < C; home Tm E < C; AFUERA abroad T2 E < C; RECUPERA the cost after the switch at T2
  E < C; PAREADO H(T2) E > C; ELIGE E at T2; stuck blocks.
  Reported: EROSIONA (coin's awake home oracle > right after a sleep: the premise of
  CONSERVA_D under "dos"); the oracle table (home and school in the childhood, the exile
  at its end); experts in use, h and e; the latency to h; switches in the childhood.

PREDICTIONS (written before the smoke test and the calibration). VERIFICATION 24/24.
PERSISTE_D passes (coin under "dos" 22/24 pooled, §K7; the slow wake keeps the home expert
as it was). CONSERVA_D passes: the slow wake keeps what sleep consolidates whatever the
upbringing. VUELVE_D leaning pass (under "dos" coin's latency back to h at T2 is 17 ticks
vs 11 under "una", so the slow return has more to protect). ENTRA_D uncertain: under
"dos" coin already enters the exile at 0.327 (§K7) vs 0.50 under "una", below
coin_regreso's 0.367 under "una". RIGIDO_D does not pass. NINEZ_D passes (each return
from the school is protected). Verdict, predicted: AGUANTA LA ESCUELA or NO AGUANTA:
ENTRA_D.

SMOKE (pair 0, short life: not evidence). Verification 2/2, max diff 0.0. E vs C: awake
home oracle 0.013 vs 0.028; first exile block 0.347 vs 0.418; home T2 0.143 vs 0.184;
H(T2) +1.19 vs +0.84; abroad T1 0.416 vs 0.287 and T2 0.736 vs 0.604. The childhood
returns cannot be read there (one home and one school block).

CALIBRATION (`calibracion`, pairs 100-102, never test pairs;
results/mundo_propio_escuela_calibracion_run.txt; 36.2 min). Nothing was tuned.
Verification 6/6, max diff 0.0. CONSERVA_D 3/3 (awake home oracle 0.016 vs 0.049;
EROSIONA 3/3), ENTRA_D 1/3 (first exile block 0.476 vs 0.253), VUELVE_D 2/3 (home T2
0.207 vs 0.341), PERSISTE_D 3/3 (H(T2) +0.37 vs +0.10), RIGIDO_D T1 0/3, T2 2/3 (abroad
T2 0.394 vs 0.345). Secondary: NINEZ_D 2/3 (0.112 vs 0.107, no difference), ESCUELA_D
1/3, home Tm 0/3 (0.251 vs 0.250), ELIGE 3/3. Post hoc on these lives: at the exile both
arms do the same thing (h active for 33-37 ticks, then a spawn), and the X oracle before
the exile is the same (0.17-0.19). ENTRA_D's misses are two twins (100 B, 101 B) whose
coin_regreso gets stuck acting for ~150 ticks of the first exile block (cost ~0.8-1.1)
while its world model learns X as well as coin's (X oracle at the block's end 0.055 vs
0.085, 0.076 vs 0.058). Added after the calibration, before the test: the first exile
block per twin (reported).
PREDICTIONS added after the calibration, before any test pair (the ones above stand as
written). VERIFICATION 24/24. CONSERVA_D and PERSISTE_D pass. ENTRA_D fails: under "dos"
coin already enters at 0.33, and coin_regreso can get stuck there. VUELVE_D leaning pass.
RIGIDO_D does not pass at T1; at T2 uncertain. NINEZ_D fails (no difference in the
calibration). Verdict, predicted: NO AGUANTA: ENTRA_D.

REPLICATION, pre-registered with the test: pairs 12-23, the same rule, launched right
after the test unless a bug is found (any change recorded). REPLICADO if the verdict
repeats.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py calibracion   # pairs 100-102
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_escuela.py replica       # pairs 12-23

48 lives per run (24 coin re-runs, each a verification, and 24 new); 3 CPU processes, one
torch thread each. `reanudar` after any mode loads the lives already on disk.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("mundo_propio_regreso", HERE / "exp_mundo_propio_regreso.py")
k13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k13)
k11, k8, k7, cr, co, g = k13.k11, k13.k8, k13.k7, k13.cr, k13.co, k13.g
NUEVO = k13.NUEVO
DATA_K7 = ROOT / "data" / "mundo_propio_casas"
k7.DATA = DATA = ROOT / "data" / "mundo_propio_escuela"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
CRIANZA = "dos"
BRAZOS = ("coin", NUEVO)
ULTIMOS = k11.ULTIMOS


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def cargar_k7(par: int, gemelo: str, escala: dict) -> dict:
    """A stored §K7 coin life under "dos", in the shape vivir() returns."""
    x = dict(np.load(DATA_K7 / f"{CRIANZA}_coin_{par}_{gemelo}{cr.humo(escala)}.npz"))
    return k7.salida(("coin", par, gemelo, escala, CRIANZA), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> dict:
    h = cr.humo(escala)
    tareas = [(a, p, gm, escala, CRIANZA, f"{CRIANZA}_{a}_{p}_{gm}{h}", reanudar)
              for p in pares for a in BRAZOS for gm in GEMELOS]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    return {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas}


def veredicto(conserva: int, entra: int, vuelve: int, persiste: int, rigido: int) -> str:
    """The pre-registered §K14 rule."""
    if persiste < N_OK:
        return "SIN IDENTIDAD EN LA ESCUELA"
    fallan = [nombre for nombre, v in (("CONSERVA_D", conserva), ("ENTRA_D", entra), ("VUELVE_D", vuelve))
              if v < N_OK]
    if fallan:
        return "NO AGUANTA: " + ", ".join(fallan)
    return "AGUANTA, MAS RIGIDO AFUERA" if rigido >= N_OK else "AGUANTA LA ESCUELA"


def bloques_en(x: dict, rol: str) -> list[int]:
    """The childhood blocks a twin lived in its home (rol = its twin letter) or at the school ("N")."""
    nb, nn, _ = x["vida_bloques"]
    papel = g.papeles(x["par"])
    return [v for v in range(nb, nb + nn)
            if g.regimen(papel, x["gemelo"], v, nb, nn, x["crianza"]) == papel[rol]]


def vueltas(x: dict, rol: str) -> float:
    """Mean e_early of the childhood blocks in rol's world after the first (the returns); nan if none."""
    bloques = g.por_bloque(x, x["par"])
    v = bloques_en(x, rol)[1:]
    return float(np.mean([bloques[b]["early"] for b in v])) if v else float("nan")


def cambios_ninez(x: dict) -> int:
    nb, nn, _ = x["vida_bloques"]
    ev = x["eventos"]
    return int(((ev[:, 0] == co.EVENTO["switch"]) & (ev[:, 1] < (nb + nn) * D)).sum()) if len(ev) else 0


def informe(V: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2, jm = T[-1], len(T) - 1, T.index("Tm")
    nb, nn, ne = escala["vida"]
    exilio = range(nb + nn + ne - min(ULTIMOS, ne), nb + nn + ne)
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}, '{CRIANZA}'; coin re-run (control) and {NUEVO} (§K13's arm); "
        f"run {minutos:.1f} min")
    difs = [cr.diferencia(V[("coin", p, gm)], cargar_k7(p, gm, escala)) for p in pares for gm in GEMELOS]
    out(f"verification: every coin re-run vs its stored §K7 '{CRIANZA}' life (stored keys), max diff "
        f"{max(difs)} over {len(difs)} lives ({sum(d == 0.0 for d in difs)} equal)")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares] for a in BRAZOS for t in T}
    for a in BRAZOS:
        out(f"  {a:>12} | " + " | ".join(f"{t} {np.median(H[(a, t)]):+.3f} ({sum(v > 0 for v in H[(a, t)])}/{n})"
                                       for t in T))
    out("costs (medians): home T1 | abroad T1 | home Tm | home T2 | abroad T2 | first exile block | "
        "childhood returns home | to the school | stuck blocks (twins)")
    vu = {(a, rol): [k11.por_par(V, a, p, lambda x, gm, _r=rol: vueltas(x, gm if _r == "casa" else "N"))
                     for p in pares] for a in BRAZOS for rol in ("casa", "N")}
    for a in BRAZOS:
        b, tw = cr.atascos(V, a, pares)
        cel = [np.median([f(V, a, p, t) for p in pares])
               for t, f in (("T1", k8.casa), ("T1", g.afuera), ("Tm", k8.casa), (t2, k8.casa), (t2, g.afuera))]
        out(f"  {a:>12} | " + " | ".join(f"{v:.3f}" for v in cel)
            + f" | {np.median([cr.exilio(V, a, p) for p in pares]):.3f} | {np.median(vu[(a, 'casa')]):.3f} | "
            f"{np.median(vu[(a, 'N')]):.3f} | stuck {b} ({tw}/{2 * n})")
    primero = {a: {(p, gm): g.por_bloque(V[(a, p, gm)], p)[nb + nn]["early"] for p in pares for gm in GEMELOS}
               for a in BRAZOS}
    out(f"first exile block e_early per twin (coin / {NUEVO}): "
        + ", ".join(f"{p}{gm} {primero['coin'][(p, gm)]:.2f}/{primero[NUEVO][(p, gm)]:.2f}"
                    for p in pares for gm in GEMELOS))
    out("home assay, after the switch to h (median over pairs of the twins' mean) | first tick on h (median "
        "over twins) | switches in the childhood (median over twins)")
    R = {(a, j): [k11.por_par(V, a, p, lambda x, gm, _j=j: k13.despues(x, _j)[0]) for p in pares]
         for a in BRAZOS for j in (jm, j2)}
    for a in BRAZOS:
        lat = {j: np.median([k13.despues(V[(a, p, gm)], j)[1] for p in pares for gm in GEMELOS]) for j in (jm, j2)}
        sw = np.median([cambios_ninez(V[(a, p, gm)]) for p in pares for gm in GEMELOS])
        out(f"  {a:>12} | Tm {np.median(R[(a, jm)]):.3f} (tick {lat[jm]:.0f}) | {t2} {np.median(R[(a, j2)]):.3f} "
            f"(tick {lat[j2]:.0f}) | {sw:.0f}")
    out("experts")
    for a in BRAZOS:
        k8.expertos(V, a, pares, escala, out)
    out(f"oracle (median over pairs of the twins' mean; median over the last {ULTIMOS} blocks there): "
        "right after a sleep | awake (49 online steps later)")
    O = {}
    for a in BRAZOS:
        for donde in ("home, childhood", "school, childhood", "exile, end"):
            def f(x, gm, campo, _d=donde):
                papel = g.papeles(x["par"])
                if _d == "exile, end":
                    return k11.oraculo(x, campo, papel["X"], exilio)
                rol = gm if _d.startswith("home") else "N"
                return k11.oraculo(x, campo, papel[rol], bloques_en(x, rol)[-ULTIMOS:])
            for campo in ("oraculo", "oraculo_vigilia"):
                O[(a, donde, campo)] = [k11.por_par(V, a, p, lambda x, gm, c=campo: f(x, gm, c)) for p in pares]
            out(f"  {a:>12} {donde:>17} | {np.median(O[(a, donde, 'oraculo')]):.3f} | "
                f"{np.median(O[(a, donde, 'oraculo_vigilia')]):.3f}")
    out("")
    out("-" * 80)
    mayor = lambda xs, ys: sum(x > y for x, y in zip(xs, ys))  # noqa: E731
    costo = {(a, f.__name__, t): [f(V, a, p, t) for p in pares]
             for a in BRAZOS for f in (k8.casa, g.afuera) for t in ("T1", "Tm", t2)}
    ex = {a: [cr.exilio(V, a, p) for p in pares] for a in BRAZOS}
    casa = "home, childhood"
    conserva = mayor(O[("coin", casa, "oraculo_vigilia")], O[(NUEVO, casa, "oraculo_vigilia")])
    entra = mayor(ex["coin"], ex[NUEVO])
    vuelve = mayor(costo[("coin", "casa", t2)], costo[(NUEVO, "casa", t2)])
    persiste = sum(v > 0 for v in H[(NUEVO, t2)])
    rigido_t1 = mayor(costo[(NUEVO, "afuera", "T1")], costo[("coin", "afuera", "T1")])
    rigido_t2 = mayor(costo[(NUEVO, "afuera", t2)], costo[("coin", "afuera", t2)])
    erosiona = mayor(O[("coin", casa, "oraculo_vigilia")], O[("coin", casa, "oraculo")])
    out(f"(reported) EROSIONA coin awake > right after sleep (home, childhood): {erosiona}/{n}")
    out(f"CONSERVA_D awake home oracle {NUEVO} < coin: {conserva}/{n}")
    out(f"ENTRA_D first exile block {NUEVO} < coin: {entra}/{n}")
    out(f"VUELVE_D home {t2} {NUEVO} < coin: {vuelve}/{n}")
    out(f"PERSISTE_D H({t2}) {NUEVO} > 0: {persiste}/{n}")
    out(f"RIGIDO_D abroad {NUEVO} > coin: T1 {rigido_t1}/{n}, {t2} {rigido_t2}/{n}")
    out(f"(secondary) NINEZ_D childhood returns home {NUEVO} < coin: {mayor(vu[('coin', 'casa')], vu[(NUEVO, 'casa')])}"
        f"/{n} | ESCUELA_D returns to the school: {mayor(vu[('coin', 'N')], vu[(NUEVO, 'N')])}/{n} | home Tm "
        f"{NUEVO} < coin: {mayor(costo[('coin', 'casa', 'Tm')], costo[(NUEVO, 'casa', 'Tm')])}/{n} | AFUERA "
        f"abroad {t2} {NUEVO} < coin: {mayor(costo[('coin', 'afuera', t2)], costo[(NUEVO, 'afuera', t2)])}/{n}")
    out(f"(secondary) RECUPERA after the switch {t2} {NUEVO} < coin: {mayor(R[('coin', j2)], R[(NUEVO, j2)])}/{n} | "
        f"PAREADO H({t2}) {NUEVO} > coin: {mayor(H[(NUEVO, t2)], H[('coin', t2)])}/{n} | ELIGE {NUEVO}: "
        f"{sum(k7.elige(V, p, j2, NUEVO) for p in pares)}/{n}, coin: {sum(k7.elige(V, p, j2) for p in pares)}/{n}")
    if n == len(g.PAIRS):
        v = ("STOP: VERIFICATION FAILED" if max(difs) != 0.0
             else veredicto(conserva, entra, vuelve, persiste, max(rigido_t1, rigido_t2)))
        out(f"VERDICT (pre-registered rule): {v}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    V = correr(pares, escala, reanudar)
    informe(V, pares, escala, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_escuela_humo", "§K14 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "calibracion":
        main(g.PAIRS_CAL, g.ESCALA, "mundo_propio_escuela_calibracion",
             "§K14 CALIBRATION (pairs 100-102) -- the school", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_escuela_replica",
             "§K14 REPLICATION (pairs 12-23) -- the school", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_escuela", "§K14 -- the school", reanudar)
