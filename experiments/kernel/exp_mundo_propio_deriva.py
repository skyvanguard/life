"""
§K15 -- THE DRIFT: the same life, but the exile arrives gradually. Does what the kernel achieved
in §K6-§K14 hold in a world whose contexts do not change all at once?
(docs/MUNDO_PROPIO.md; written 2026-10-29, before the smoke test and the calibration)

WHY. The repertoire line is closed (the synthesis at the top of docs/MUNDO_PROPIO.md):
coin_regreso (§K13) keeps what sleep consolidates, returns home and holds the identity,
replicated under two upbringings (§K13, §K14). Everything was measured in ONE world, whose
four regimes are exact permutations that change all at once at a block boundary. The
repertoire switches expert when the running error crosses an absolute threshold and spawns
one when no expert explains for `persist` ticks: exactly what a world of clean contexts
rewards. §K14 asked whether the arm belonged to the kernel or to the upbringing it was built
in; this asks whether it belongs to the kernel or to that world. Fran, 2026-10-29: "vamos
con tu recomendacion" (change the world, keep the arm).

THE WORLD. §K4's life, roles, test ticks, assays and probes, unchanged, except the first
stretch of the exile: from its first tick to the Tm assay (blocks 18-22, L = 1500 ticks; the
smoke's short life: block 3, 300 ticks) the step is
    s' = normalize(0.7 s + 0.3 [(1 - f) roll(a, home) + f roll(a, X)]),  f = (t - t0 + 1) / L,
the remapping moving linearly from the twin's home to the exile X (exactly X at the last tick
of the ramp); pure X after, as before. The assays still visit pure worlds. Declared hands:
(1) a 50/50 mix of two permutations of the 4-simplex is singular: the best fixed point of a
mixed world is ||s* - C|| = 0.07 at f = 0.2, 0.18 at 0.3, 0.27-0.31 at 0.4 and 0.31-0.42 at
0.5 (0 at f <= 0.1 and >= 0.9), so the middle of the ramp cannot be fully controlled by
anyone and its blocks are left out of the stuck count (reported apart); (2) the pure exile is
10 blocks instead of 15; (3) under the home policy the pure-home prediction's one-step error
is 0.255 f, so the active expert's running error crosses the 0.08 threshold near f = 0.31 if
it does not learn.

ARMS. coin_regreso (E, the reference configuration) and coin (C), both under the drift, on
the test pairs; the references are their stored lives in the clean world, the same twins
with the same births and draws (E: §K13, data/mundo_propio_regreso; C: §K11,
data/mundo_propio_vigilia; for the calibration pairs C is §K7's and E's clean life is run
here). Nothing is tuned.

VERIFICATION. The drift starts after the T1 assay: every drifted life must equal its clean
life before the exile -- the per-tick series, the probes, the T1 assay, the self_embedding
there and the context events (exp_mundo_propio_ninez.ninez, plus the awake probes) -- max
diff 0, else stop: a bug. 24 per run.

Readouts per pair (mean of the twins): H at T1/Tm/T2; the home cost at Tm and T2 and abroad
at T2; whether the exile got its own expert (k7.casa_exilio: e != h); the first spawn of the
exile, its tick and f; the experts in use; the home oracle at the end of the exile (median of
the last 5 blocks, the best expert's probe error on the twin's home regime); the ramp's cost
(e_early, e_late of its blocks) and the first pure-X block's e_early; stuck blocks outside
the ramp; ELIGE.

RULE (sign tests over 12 pairs; 10/12 = one-sided p 0.019). E = coin_regreso; W = the drift,
L = the clean world (the stored life).
  VERIFICACION every drifted childhood equal to its clean life; else stop.
  SEPARA_W  (primary) the exile got its own expert (e != h) in both twins, E under W.
  PERSISTE_W (primary) H(T2) > 0, E under W.
  DANO_W    (primary) home cost at T2, E under W > E under L: the drift makes the return
            home cost more.
  VERDICT  no PERSISTE_W -> LA DERIVA BORRA LA IDENTIDAD; else SEPARA_W without DANO_W ->
           AGUANTA LA DERIVA; SEPARA_W and DANO_W -> SEPARA, PERO VUELVE PEOR; no SEPARA_W
           and no DANO_W -> SE FUNDE, SIN COSTO; no SEPARA_W and DANO_W -> SE FUNDE Y VUELVE
           PEOR.
  Secondary: the three for C; VUELVE_W home T2 E < C under W; AFUERA_W abroad T2 E < C under
  W; PAREADO_W H(T2) of E, W < L; ORACULO_W the home oracle at the end of the exile, E, W > L;
  ELIGE of E under W.
  Reported: the spawn tick and f, the experts in use, (h, e), the ramp's cost, the first pure-X
  block, stuck blocks outside the ramp, the latency to h, the oracle table.

PREDICTIONS (written before the smoke test and the calibration).
  VERIFICACION 24/24.
  SEPARA_W fails in both arms: the home expert follows the drift instead of handing the exile
  to a new one. A spawn needs every expert above the threshold for 30 consecutive ticks; the
  ramp moves f by 0.02 every 30 ticks and an expert learning at the full awake rate follows
  that. Leaning: E separates in more twins than C (its slow wake lags before the crossing).
  PERSISTE_W passes: the merged expert's buffer still holds the childhood and sleep replays
  it; §K4's single world model (error_x4) persisted 24/24 (H(T2) +0.53).
  DANO_W passes: merged, the return home costs what a single model's does (§K4 error_x4 home
  T2 0.300; E in the clean world 0.117).
  VERDICT, predicted: SE FUNDE Y VUELVE PEOR. Secondary: the same for C; VUELVE_W uncertain;
  ORACULO_W passes; PAREADO_W passes.
Background, not a prediction: in human motor adaptation the gradual-versus-abrupt comparison
is mixed (Leow et al.: savings needs a prior experience of the error, which a gradual change
avoids; Savalia et al., MathPsych 2020 abstract: a larger aftereffect back at baseline after
gradual training).

REPLICATION, pre-registered with the test: pairs 12-23, the same rule, launched right after
the test unless a bug is found (any change recorded). REPLICADO if the verdict repeats.

    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_deriva.py humo
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_deriva.py calibracion   # pairs 100-102
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_deriva.py
    PYTHONPATH=src python experiments/kernel/exp_mundo_propio_deriva.py replica       # pairs 12-23

48 lives per test run (24 per arm, each also a verification); the calibration adds the 6
clean coin_regreso lives it has no stored reference for. 3 CPU processes, one torch thread
each. `reanudar` after any mode loads the lives already on disk.
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
k9, ms = k11.k9, g.ms
NUEVO = k13.NUEVO
CRIANZA = "deriva"
BRAZOS = ("coin", NUEVO)
LIMPIAS = {"coin": (k11.DATA, ROOT / "data" / "mundo_propio_casas"), NUEVO: (k13.DATA,)}
k7.DATA = DATA = ROOT / "data" / "mundo_propio_deriva"
RESULTS = ROOT / "results"
GEMELOS = g.GEMELOS
N_OK = g.N_OK
D = g.D
ULTIMOS = k11.ULTIMOS


def tramo(escala: dict) -> tuple[int, int]:
    """(first tick, end tick) of the ramp: from the exile's first tick to the Tm assay."""
    nb, nn, _ = escala["vida"]
    return (nb + nn) * D, dict(escala["ensayos"])["Tm"] * D


def rampa(papel: dict, gemelo: str, t: int, escala: dict, crianza: str) -> np.ndarray | None:
    """Regime weights of tick t under the drift (f = 1/L ... 1 from the twin's home to X along
    the ramp); None elsewhere and in any other life."""
    if crianza != CRIANZA:
        return None
    t0, t1 = tramo(escala)
    if not t0 <= t < t1:
        return None
    f = (t - t0 + 1) / (t1 - t0)
    w = np.zeros(4)
    w[papel[gemelo]] += 1 - f
    w[papel["X"]] += f
    return w


k7.MEZCLA = rampa


def vivir(args: tuple) -> dict:
    return k7.vivir(args)


def ruta_limpia(brazo: str, par: int, gemelo: str, escala: dict) -> Path:
    """The stored clean-world life ('una') of a twin: the first of the arm's sources that has
    it, else this experiment's own (the calibration's coin_regreso)."""
    nombre = f"una_{brazo}_{par}_{gemelo}{cr.humo(escala)}.npz"
    for d in LIMPIAS[brazo] + (DATA,):
        if (d / nombre).exists():
            return d / nombre
    return DATA / nombre


def cargar_limpia(brazo: str, par: int, gemelo: str, escala: dict) -> dict:
    x = dict(np.load(ruta_limpia(brazo, par, gemelo, escala)))
    return k7.salida((brazo, par, gemelo, escala, "una"), x, time.time())


def correr(pares: tuple, escala: dict, reanudar: bool) -> tuple[dict, dict]:
    h = cr.humo(escala)
    tareas = [(a, p, gm, escala, CRIANZA, f"{CRIANZA}_{a}_{p}_{gm}{h}", reanudar)
              for p in pares for a in BRAZOS for gm in GEMELOS]
    tareas += [(a, p, gm, escala, "una", f"una_{a}_{p}_{gm}{h}", reanudar)
               for p in pares for a in BRAZOS for gm in GEMELOS
               if not ruta_limpia(a, p, gm, escala).exists()]
    with ProcessPoolExecutor(max_workers=g.WORKERS) as pool:
        vidas = list(pool.map(vivir, tareas))
    W = {(x["brazo"], x["par"], x["gemelo"]): x for x in vidas if x["crianza"] == CRIANZA}
    L = {(a, p, gm): cargar_limpia(a, p, gm, escala) for p in pares for a in BRAZOS for gm in GEMELOS}
    return W, L


def ninez(x: dict, escala: dict) -> dict:
    """The part of a life before the exile (§K9's, plus the awake probes of §K11 where the life
    has them: §K7's lives, the calibration's clean coin, predate them)."""
    nb, nn, _ = escala["vida"]
    out = k9.ninez(x, escala)
    out.update({k: np.asarray(x[k])[: nb + nn] for k in ("sonda_vigilia", "oraculo_vigilia") if k in x})
    return out


def oraculo(x: dict, campo: str, bloques: range) -> float:
    """The twin's home oracle over the blocks; nan if the life has no such probe."""
    return k11.oraculo(x, campo, g.papeles(x["par"])[x["gemelo"]], bloques) if campo in x else float("nan")


def veredicto(separa: int, persiste: int, dano: int) -> str:
    """The pre-registered §K15 rule."""
    if persiste < N_OK:
        return "LA DERIVA BORRA LA IDENTIDAD"
    if separa >= N_OK:
        return "SEPARA, PERO VUELVE PEOR" if dano >= N_OK else "AGUANTA LA DERIVA"
    return "SE FUNDE Y VUELVE PEOR" if dano >= N_OK else "SE FUNDE, SIN COSTO"


def separa(V: dict, a: str, p: int) -> bool:
    """The exile got its own expert in both twins."""
    return all(k7.casa_exilio(V[(a, p, gm)], p)[1] != k7.casa_exilio(V[(a, p, gm)], p)[0] for gm in GEMELOS)


def parto(x: dict, escala: dict) -> int | None:
    """Ticks from the exile's start to its first spawn; None if none."""
    t0, _ = tramo(escala)
    ev = np.asarray(x["eventos"]).reshape(-1, 3)
    ticks = ev[(ev[:, 0] == co.EVENTO["spawn"]) & (ev[:, 1] >= t0), 1]
    return int(ticks.min() - t0) if ticks.size else None


def bloques_rampa(escala: dict) -> range:
    t0, t1 = tramo(escala)
    return range(t0 // D, t1 // D)


def costo_bloques(V: dict, a: str, p: int, bloques: range, campo: str) -> float:
    return float(np.mean([np.mean([g.por_bloque(V[(a, p, gm)], p)[b][campo] for b in bloques]) for gm in GEMELOS]))


def atascos_fuera(V: dict, a: str, pares: tuple, escala: dict) -> tuple[int, int]:
    """(stuck acting blocks outside the ramp, twins with any) -- late > 0.3."""
    rampa_ = set(bloques_rampa(escala))
    bloques, gemelos = 0, 0
    for p in pares:
        for gm in GEMELOS:
            n = sum(b["late"] > 0.3 for v, b in enumerate(g.por_bloque(V[(a, p, gm)], p))
                    if b["fase"] == "act" and v not in rampa_)
            bloques, gemelos = bloques + n, gemelos + (n > 0)
    return bloques, gemelos


def informe(W: dict, L: dict, pares: tuple, escala: dict, nombre: str, titulo: str, minutos: float) -> None:
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    n = len(pares)
    T = [t for t, _ in escala["ensayos"]]
    t2, j2 = T[-1], len(T) - 1
    nb, nn, ne = escala["vida"]
    t0, t1 = tramo(escala)
    rb = bloques_rampa(escala)
    exilio = range(nb + nn + ne - min(ULTIMOS, ne), nb + nn + ne)
    mundos = (("W", W), ("L", L))
    out("=" * 80)
    out(titulo)
    out("=" * 80)
    out(f"pairs {pares[0]}-{pares[-1]}; {BRAZOS} under the drift (W: ramp home -> X over ticks {t0}-{t1 - 1}, "
        f"blocks {rb.start}-{rb.stop - 1}) vs their clean lives (L); run {minutos:.1f} min")
    difs = [cr.diferencia(ninez(W[key], escala), ninez(L[key], escala)) for key in W]
    out(f"verification: every drifted childhood vs its clean life, max diff {max(difs)} over {len(difs)} lives "
        f"({sum(d == 0.0 for d in difs)} equal); whole lives differ in "
        f"{sum(cr.diferencia(W[key], L[key]) > 0 for key in W)}/{len(W)}")
    out("")
    out("H_early (cross) medians and H>0 per assay")
    H = {(m, a, t): [g.cruce(g.leer(V, a, p, t, "early")) for p in pares]
         for m, V in mundos for a in BRAZOS for t in T}
    for a in BRAZOS:
        for m, _ in mundos:
            out(f"  {a:>12} {m} | " + " | ".join(
                f"{t} {np.median(H[(m, a, t)]):+.3f} ({sum(v > 0 for v in H[(m, a, t)])}/{n})" for t in T))
    out("costs (medians): home Tm | home T2 | abroad T2 | ramp blocks early / late | first pure-X block | "
        "stuck outside the ramp (twins)")
    for a in BRAZOS:
        for m, V in mundos:
            b, tw = atascos_fuera(V, a, pares, escala)
            cel = [np.median([f(V, a, p, t) for p in pares]) for t, f in (("Tm", k8.casa), (t2, k8.casa),
                                                                       (t2, g.afuera))]
            re_ = np.median([costo_bloques(V, a, p, rb, "early") for p in pares])
            rl = np.median([costo_bloques(V, a, p, rb, "late") for p in pares])
            px = np.median([costo_bloques(V, a, p, range(rb.stop, rb.stop + 1), "early") for p in pares])
            out(f"  {a:>12} {m} | " + " | ".join(f"{v:.3f}" for v in cel)
                + f" | {re_:.3f} / {rl:.3f} | {px:.3f} | stuck {b} ({tw}/{2 * n})")
    out("the exile's first spawn: ticks after the exile starts (f at it) per twin; None = no spawn")
    for a in BRAZOS:
        for m, V in mundos:
            cel = []
            for p in pares:
                for gm in GEMELOS:
                    d = parto(V[(a, p, gm)], escala)
                    cel.append(f"{p}{gm} " + ("None" if d is None else
                                              f"{d} ({min(1.0, (d + 1) / (t1 - t0)):.2f})" if m == "W" else f"{d}"))
            out(f"  {a:>12} {m}: " + ", ".join(cel))
    out("experts")
    for a in BRAZOS:
        for m, V in mundos:
            out(f" [{m}]")
            k8.expertos(V, a, pares, escala, out)
    out(f"home oracle at the end of the exile (median of the last {ULTIMOS} blocks; median over pairs of the "
        "twins' mean): right after a sleep | awake")
    O = {}
    for a in BRAZOS:
        for m, V in mundos:
            for campo in ("oraculo", "oraculo_vigilia"):
                O[(m, a, campo)] = [k11.por_par(V, a, p, lambda x, gm, c=campo: oraculo(x, c, exilio))
                                    for p in pares]
            out(f"  {a:>12} {m} | {np.median(O[(m, a, 'oraculo')]):.3f} | {np.median(O[(m, a, 'oraculo_vigilia')]):.3f}")
    out("")
    out("-" * 80)
    mayor = lambda xs, ys: sum(x > y for x, y in zip(xs, ys))  # noqa: E731
    costo = {(m, a, f.__name__, t): [f(V, a, p, t) for p in pares]
             for m, V in mundos for a in BRAZOS for f in (k8.casa, g.afuera) for t in ("Tm", t2)}
    lect = {}
    for a in BRAZOS:
        lect[a] = (sum(separa(W, a, p) for p in pares), sum(v > 0 for v in H[("W", a, t2)]),
                   mayor(costo[("W", a, "casa", t2)], costo[("L", a, "casa", t2)]))
        out(f"{'' if a == NUEVO else '(secondary) '}{a}: SEPARA_W both twins e != h {lect[a][0]}/{n} | "
            f"PERSISTE_W H({t2}) > 0 {lect[a][1]}/{n} | DANO_W home {t2} W > L {lect[a][2]}/{n} | SEPARA in L "
            f"{sum(separa(L, a, p) for p in pares)}/{n}")
    out(f"(secondary) VUELVE_W home {t2} {NUEVO} < coin under W: "
        f"{mayor(costo[('W', 'coin', 'casa', t2)], costo[('W', NUEVO, 'casa', t2)])}/{n} | AFUERA_W abroad {t2} "
        f"{NUEVO} < coin under W: {mayor(costo[('W', 'coin', 'afuera', t2)], costo[('W', NUEVO, 'afuera', t2)])}/{n}"
        f" | PAREADO_W H({t2}) {NUEVO} W < L: {mayor(H[('L', NUEVO, t2)], H[('W', NUEVO, t2)])}/{n} | ORACULO_W "
        f"{NUEVO} W > L: {mayor(O[('W', NUEVO, 'oraculo')], O[('L', NUEVO, 'oraculo')])}/{n} | ELIGE {NUEVO} W: "
        f"{sum(k7.elige(W, p, j2, NUEVO) for p in pares)}/{n}, L: {sum(k7.elige(L, p, j2, NUEVO) for p in pares)}/{n}")
    if n == len(g.PAIRS):
        v = "STOP: VERIFICATION FAILED" if max(difs) != 0.0 else veredicto(*lect[NUEVO])
        out(f"VERDICT (pre-registered rule): {v}")
    else:
        out("(n < 12: no verdict)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{nombre}_run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def humo_mezcla() -> float:
    """A one-hot mix gives exactly mover()'s step (max |difference| over random states)."""
    import torch
    rng = np.random.default_rng(0)
    s = torch.tensor(rng.dirichlet(np.ones(4), size=64), dtype=torch.float32)
    a = torch.tensor(rng.dirichlet(np.ones(4), size=64), dtype=torch.float32)
    return max(float((ms.mezcla(s, a, np.eye(4)[k]) - ms.mover(s, a, k)).abs().max()) for k in range(4))


def main(pares: tuple, escala: dict, nombre: str, titulo: str, reanudar: bool) -> None:
    t0 = time.time()
    if escala == g.HUMO:
        a, b = tramo(escala)
        papel = g.papeles(pares[0])
        print(f"one-hot mix vs mover, max diff {humo_mezcla()}; ramp ticks {a}-{b - 1}; weights of twin A at "
              f"{a}: {rampa(papel, 'A', a, escala, CRIANZA)}, at {b - 1}: {rampa(papel, 'A', b - 1, escala, CRIANZA)}, "
              f"at {b}: {rampa(papel, 'A', b, escala, CRIANZA)}; roles {papel}")
    W, L = correr(pares, escala, reanudar)
    informe(W, L, pares, escala, nombre, titulo, (time.time() - t0) / 60)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    reanudar = "reanudar" in argumentos
    modo = next((a for a in argumentos if a != "reanudar"), "")
    if modo == "humo":
        main((0,), g.HUMO, "mundo_propio_deriva_humo", "§K15 SMOKE TEST (pair 0, short life)", reanudar)
    elif modo == "calibracion":
        main(g.PAIRS_CAL, g.ESCALA, "mundo_propio_deriva_calibracion",
             "§K15 CALIBRATION (pairs 100-102) -- the drift", reanudar)
    elif modo == "replica":
        main(tuple(range(12, 24)), g.ESCALA, "mundo_propio_deriva_replica",
             "§K15 REPLICATION (pairs 12-23) -- the drift", reanudar)
    else:
        main(g.PAIRS, g.ESCALA, "mundo_propio_deriva", "§K15 -- the drift", reanudar)
